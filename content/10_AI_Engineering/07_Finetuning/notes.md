# Finetuning

Finetuning continues training from a checkpoint you already have. This topic covers when that run is the right lever, why the memory bill explodes, which number formats and quantizers change the bill, and the parameter-efficient, merging, and hyperparameter choices that make a 7B update fit. Supervised finetuning and preference losses stay in Understanding Foundation Models. Retrieval stays in RAG and Agents. The held-out eval stays in Evaluate AI Systems. Serving kernels stay in Inference Optimization.

## Key Points

- **What finetuning is** — continued training from existing weights, which is transfer learning. A new head, a full update, and a small adapter are the three degrees. The demonstrations set the ceiling.
- **Finetuning objectives** — continued pretraining, supervised finetuning, then a preference loss. Code Llama continued Llama 2 on code. The answer-token mask and DPO stay on the earlier cards.
- **Reasons to finetune** — a stable behavior a measured prompt does not hold, a volume where in-context examples dominate the bill, or a student that should imitate a teacher. A changing fact is not on this list.
- **Reasons not to finetune** — facts you must update or delete, syntax a mask can forbid, an unscored prompt, a handful of noisy examples, a target that changes weekly, a license that forbids the derivative, or an eval set you do not have.
- **Finetuning and RAG** — retrieval supplies information. Finetuning changes behavior. Production often does both, and the demonstrations have to contain the passage or the model learns to ignore the index.
- **Backpropagation and trainable parameters** — mixed-precision AdamW is 16 bytes a trainable parameter: BF16 weight 2, BF16 gradient 2, FP32 master 4, Adam moments 8. A 4096 by 4096 matrix is 32 MiB in BF16 and 256 MiB to train. An FP32 gradient is the 18-byte count, 288 MiB for that matrix. Freezing removes the update state. It removes a layer's activations only when the backward stops before that layer.
- **Inference memory** — weights plus KV cache plus activations. The untied Llama 2 7B layout is 6,738,415,616 parameters and 12.6 GiB in BF16. The cache is 512 KiB a token, 2 GiB at 4,096 tokens, 14.6 GiB with the weights, and 28.6 GiB for eight such requests.
- **Training memory** — a whiteboard 7B is 104.3 GiB of 16-byte state, and Llama 2 7B is 100.4 GiB, before activations. FP32 gradients make that layout 113.0 GiB. ZeRO stage 1 shards the optimizer. On 8 GPUs the model state is about 34.5 GiB a card. Query and value LoRA at rank 8 is 12.61 GiB on a BF16 base. With those adapters included, a QLoRA floor that leaves the embeddings in BF16 is 3.66 GiB, and packing every parameter is 3.30 GiB. Activations sit on top.
- **Numerical representations** — FP16 tops out at 65,504. BF16 reaches about 3.4e38, which is why training moved to it. TF32 and FP8 are compute formats. INT4 has 16 codes plus a scale.
- **Inference quantization** — post-training, weight-only GPTQ and AWQ, or weight-and-activation methods such as LLM.int8 and SmoothQuant. INT4 saves memory and is the format that most often moves arithmetic.
- **Training quantization** — mixed precision, quantization-aware training, or QLoRA. NF4, double quantization from 0.5 bits to 0.126953 bits of scale at the paper's block sizes, and paged optimizers. The QLoRA paper's 65B comparison is from more than 780 GB to under 48 GB. The 780 GB matches 12 bytes a parameter on a round 65B, not the 16-byte row.
- **Parameter-efficient finetuning** — train a small set, freeze the base, and skip the 100.4 GiB model state. Adapters sit inside the block. Soft prompts sit on the input. Hugging Face PEFT is the library.
- **Adapters, prefixes, and rescaling** — a Houlsby bottleneck at rank 64 on the 7B width is 33,554,432 parameters and stays a branch at serve time. Prefix tuning, prompt tuning, and IA3 do not fold back into `W`.
- **LoRA** — `W + (alpha / r) BA`. Hu and coauthors fixed alpha at the first rank. Rank 8 and alpha 16, a common library pair, scales by 2. The QLoRA LLaMA runs used rank 64 and alpha 16, which scales by 0.25. A 4096 by 4096 matrix at rank 8 is 65,536 parameters. Query and value on Llama 2 7B are 4,194,304 parameters, an 8 MiB file, and 64 MiB of 16-byte optimizer state.
- **Serving many adapters** — leave the LoRAs unmerged on one base. Punica batches the low-rank products. S-LoRA pages adapters beside the KV cache. vLLM is the server whose rank and module limits you read. The cache does not shrink because the adapter is small.
- **Model merging** — one checkpoint from same-shaped models, without the data. The goals are multi-task, on-device, and federated averages such as FedAvg. Summing, stacking, and concatenation are different tensor operations.
- **Summing weights** — soups average checkpoints. Task arithmetic adds finetuned-minus-base. A `+0.4` and a `−0.4` cancel. TIES elects a sign. DARE drops and rescales by `1 / (1 − p)`. SLERP is the two-model arc. mergekit implements them.
- **Layer stacking** — same hidden size, more depth. SOLAR 10.7B builds 48 layers by `2 × (32 − 8)` and then continues pretraining. A splice without that training is a frankenmerge.
- **Concatenation** — width, not depth. Sparse upcycling copies a feed-forward into experts, adds a router, and keeps training. An average of two models' outputs is an ensemble, not a merged file.
- **Multi-task finetuning and merging** — joint training when the data can sit together, task arithmetic when it cannot and one file is required, separate LoRAs when requests are separable. Score each skill. An average can hide a regression.
- **Finetuning frameworks** — PEFT and TRL, Axolotl, Unsloth, and torchtune when you need the weights. The OpenAI fine-tuning API and Vertex AI Gemini tuning take examples and return a hosted model, not weights. The chat template is part of the data.
- **Choosing a base model** — prompt, then retrieval, then PEFT on a model you can serve, then distillation, then a full update. DistilBERT is the classic student. The license on the base binds the finetune.
- **Finetuning hyperparameters** — sweep near `10^-5` for a full update and near `10^-4` for LoRA. The QLoRA paper used `2 × 10^-4` on its 7B and 13B runs and `10^-4` on its 33B and 65B runs, on a constant schedule. Effective batch is microbatch times accumulation times GPUs. One, eight, and four make 32. A prompt loss weight of 0 trains on the answer. On 100 prompt tokens and 20 answer tokens, a weight of 1 leaves the answer at 0.167 of the tokens.

## Example

The numbers that come up in a finetune review are the 16-byte state, the LoRA file, and the FP16 overflow. GiB means 1024 cubed bytes. The 16 bytes are a BF16 weight, a BF16 gradient, an FP32 master copy, and Adam's two FP32 moments. The Llama 2 counts are the untied layouts. A launch replaces the static byte counts with the peak the profiler reports on the GPU you will use.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(32, 4096, 11008)
LORA = 32 * 2 * 8 * (4096 + 4096)
BITS = 4 + 8 / 64 + 32 / (64 * 256)
BYTES = 2 + 2 + 4 + 4 + 4
EMBED = 2 * 32_000 * 4096
NORMS = 32 * 2 * 4096 + 4096
LINEARS = PARAMS - EMBED - NORMS
print(8 * (4096 + 4096))
print(f"{(2 - 2**-10) * 2**15:.0f} {(2 - 2**-7) * 2**127:.3e}")
print(f"{7_000_000_000 * BYTES / 1024**3:.1f} {PARAMS * BYTES / 1024**3:.1f} {PARAMS * (BYTES + 2) / 1024**3:.1f}")
print(f"{(PARAMS * 2 + LORA * BYTES) / 1024**3:.2f}")
print(f"{(PARAMS * BITS / 8 + LORA * BYTES) / 1024**3:.2f}")
print(f"{(LINEARS * BITS / 8 + (EMBED + NORMS) * 2 + LORA * BYTES) / 1024**3:.2f}")
print(1 * 8 * 4)
# 65536
# 65504 3.390e+38
# 104.3 100.4 113.0
# 12.61
# 3.30
# 3.66
# 32
```

A 4096 by 4096 matrix at rank 8 is 65,536 trainable parameters. FP16 overflows at 65,504. BF16's maximum is about 3.390e38. A whiteboard 7B full AdamW state is 104.3 GiB at 16 bytes, and the Llama 2 7B configuration is 100.4 GiB, before activations. The same layout with FP32 gradients is 113.0 GiB. Query and value LoRA on that configuration is 12.61 GiB on a BF16 base. The same adapters on a base packed entirely at the double-quantized 4-bit width are a 3.30 GiB floor. Leaving the embeddings, the output projection, and the norms in BF16, and packing only the linear weights, is 3.66 GiB with those adapters included. A microbatch of 1, accumulated 8 times, on 4 GPUs, is an effective batch of 32. The drills apply the same arithmetic to a Harvey labeler, a 13B QLoRA job on a 4090, a GitHub triager's rank, fifty customer adapters, an INT4 math failure, a code-and-chat merge, a loss curve, and a Zendesk classifier's base size.

## Source Chapter

- **Book chapter**: Chapter 7
- **Title**: Finetuning

## Book Outline

- Finetuning Overview
- When to Finetune
  - Reasons to Finetune
  - Reasons Not to Finetune
  - Finetuning and RAG
- Memory Bottlenecks
  - Backpropagation and Trainable Parameters
  - Memory Math
    - Memory needed for inference
    - Memory needed for training
  - Numerical Representations
  - Quantization
    - Inference quantization
    - Training quantization
- Finetuning Techniques
  - Parameter-Efficient Finetuning
    - PEFT techniques
    - LoRA
  - Model Merging and Multi-Task Finetuning
    - Summing
    - Layer stacking
    - Concatenation
  - Finetuning Tactics
    - Finetuning frameworks and base models
    - Finetuning hyperparameters
- Summary

## Status

- `concepts.md` is a study set of 23 cards: what finetuning is, finetuning objectives, reasons to finetune, reasons not to finetune, finetuning and RAG, backpropagation and trainable parameters, inference memory, training memory, numerical representations, inference quantization, training quantization, parameter-efficient finetuning, adapters prefixes and rescaling, LoRA, serving many adapters, model merging, summing weights, layer stacking, concatenation, multi-task finetuning and merging, finetuning frameworks, choosing a base model, and finetuning hyperparameters. The key points above are the chapter summary.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: 16 bytes per trainable parameter (BF16 weight, BF16 gradient, FP32 master, two FP32 moments), the 18-byte FP32-gradient variant, the untied Llama 2 7B and 13B layouts, a 4096 by 4096 LoRA at rank 8, NF4 double quantization at the QLoRA paper's block sizes, and an effective batch. A launch replaces the static byte counts with a measured peak, the license on the pinned checkpoint, and the held-out eval.
- Supervised finetuning, reward models, and preference losses stay in Understanding Foundation Models. Retrieval stays in RAG and Agents. The launch pipeline and the license terms stay in Evaluate AI Systems. Chat templates stay in Prompt Engineering. Serving kernels stay in Inference Optimization.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — prompting, retrieval, and finetuning as the three levers, in that order.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — the 18-byte FP32-gradient variant of the memory count, the KV-cache formula, supervised finetuning, preference finetuning, and finetuning as the fourth rung of structured output.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — the held-out pipeline a checkpoint has to pass, and the license on the base weights.
- [Prompt Engineering](../05_Prompt_Engineering/) — the prompt you score before you train, the few-shot tax a finetune can remove, and the chat template the trainer has to apply.
- [RAG and Agents](../06_RAG_and_Agents/) — the index for facts that change, and the calculator a quantized model should call instead of inventing a digit.
- [Dataset Engineering](../08_Dataset_Engineering/) — building the demonstrations this topic assumes you already have.
- [Inference Optimization](../09_Inference_Optimization/) — the kernels behind a quantized serve and a paged KV cache, once the byte budget is known.
