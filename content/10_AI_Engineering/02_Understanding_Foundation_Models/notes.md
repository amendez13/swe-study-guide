# Understanding Foundation Models

A foundation model is a base checkpoint plus the choices that make its output usable: the data it continued, the architecture that reads a prompt, the post-training that turns continuation into an answer, and the sampler that picks the next token. This topic is those choices. It stays with public models and public numbers. Evaluation metrics, prompt recipes, retrieval mechanics, the finetune training stack, and serving kernels live in the later topics.

## Key Points

- **Training data** — the base model learns to continue filtered web text, code, and curated prose. It is strongest where that mix was dense. Private facts were never in it.
- **Multilingual models** — one checkpoint serves many languages, and the tokenizer plus the data mix still make them unequal. Llama 3's English sample moved from 3.17 to 3.94 characters per token. Measure tokens and quality per language.
- **Domain-specific models** — Codex, Code Llama, and StarCoder are code models. BloombergGPT was pretrained from scratch on a financial-plus-general mix, 50.6 billion parameters in the paper's table. Med-PaLM adapts a general model. One model on an unfiltered mix under-trains a rare field. A specialist is not automatically ahead of a stronger general model. Retrieval owns facts that change.
- **The transformer** — attention over the sequence, from the 2017 encoder-decoder. Decoder-only causal models write ChatGPT, Copilot, and the public Llama and Mistral checkpoints. Llama uses SwiGLU. BERT keeps the encoder. Gemini 1.5 Pro is a mixture-of-experts Transformer.
- **Attention, the KV cache, and context** — each new token reuses stored keys and values. On the Llama 2 70B and Llama 3 70B shape, 80 layers and 8 key-value heads in BF16, one request is 1.25 GiB of cache at 4,096 tokens and 40 GiB at 131,072 tokens. The length includes tokens generated so far.
- **Other architectures** — Mamba and RWKV keep a fixed state instead of a growing cache, and they give up exact lookup of an earlier token. Jamba keeps some attention layers and is also a mixture of experts. Mixtral is still a transformer.
- **Parameters, tokens, and FLOPs** — a round 70 billion parameters is 130.4 GiB of BF16 weights. The released Llama 3 70B configuration is 70,553,706,496 parameters and 131.4 GiB in BF16, or 65.7 GiB at INT8. Mixed-precision AdamW is 16 bytes per parameter with a BF16 gradient, 1,043.1 GiB at the round count and 1,051.3 GiB for that configuration, and 18 bytes when the gradient is FP32, 1,173.5 GiB and 1,182.7 GiB. A FLOP is a count and a FLOP/s is a rate. At an exercise $2 per GPU-hour, the Chinchilla-sized `6ND` sketch is $330,166 at the H100 dense peak and $825,416 at 40 percent utilization. A mixture of experts stores more parameters than it uses on each token.
- **Compute-optimal scaling** — Chinchilla's rule of thumb is about 20 tokens per parameter for a fixed training-FLOP budget. A 70B model wants about 1.4 trillion tokens. Llama 3's 405B run is near that split for its budget. The 8B and 70B were trained out to about 15 trillion tokens because inference is paid on every request. Parameters are learned. Hyperparameters, including the learning rate, are chosen, and a pretraining run is often one shot at them. μP is the attempt to tune the small model and carry the optimum up in width.
- **Scaling extrapolation** — a curve fit on smaller runs predicts loss inside the same architecture, data mix, and recipe. It does not predict a benchmark. Some apparent capability jumps are the scoring rule. Inverse scaling, from the 2023 prize write-up, is a task where larger models score worse, and some of those tasks later turn U-shaped. Score the size you will serve.
- **Scaling bottlenecks** — usable text, accelerator power, and a product metric that has stopped tracking loss. Llama 3's 405B run used up to 16,384 H100 GPUs at a 700 watt TDP, 11.5 megawatts of nameplate before cooling.
- **Supervised finetuning** — prompt-and-answer pairs, with the loss on the answer tokens, teach a base model to reply. The demonstrations set the ceiling. This does not rank two plausible answers.
- **Reward models** — a Bradley-Terry scorer on preference pairs. It can train a policy or pick the best of N samples. It also learns shortcuts in the comparisons, and length is the usual one.
- **RLHF and DPO** — InstructGPT and Llama 2-Chat are supervised finetuning, then a reward model, then PPO with a KL penalty. Llama 3's report uses supervised finetuning, rejection sampling, and DPO. Fresh documents stay in retrieval.
- **Sampling from logits** — softmax turns logits into probabilities. On the scores 2, 1, and 0, temperature 1 gives about 0.665, 0.245, and 0.090. Temperature 0.5 gives about 0.867, 0.117, and 0.016. The leading token does not change.
- **Temperature, top-k, top-p, and stopping** — temperature reshapes the gaps, top-k and top-p drop the tail, and min-p drops tokens below a base times the leader's probability. On the temperature-1 exercise a base of 0.2, above the paper's 0.05 to 0.1 band, leaves 0.7311 and 0.2689. At temperature 0.5 a base of 0.1 leaves 0.8808 and 0.1192. Move one knob. Do not stop on a string that a valid answer can contain.
- **Test-time compute** — extra samples or extra reasoning tokens, as in best-of-N, self-consistency, o1, and DeepSeek-R1. They help when a verifier can reject a failure. Without a verifier, the sum of token log-probabilities prefers a shorter sample. On an exercise pair the sum picks −0.5 over −0.8, and the length average picks −0.2 over −0.5. Inline ghost text cannot spend the extra samples.
- **Structured outputs** — prompting, post-processing, constrained sampling, and finetuning. A closed label set can skip generation and train a classifier head on a frozen body. JSON mode promises a JSON string. A schema mask promises the declared fields. A tool call still needs your code to decide whether the function runs. A parser checks the values, because a valid object can hold a false total.
- **Inconsistency** — the fact stayed put and the answer moved, across samples or across phrasings. Agreement and support are different tests. Sampling knobs reduce sample variance and repeat a wrong mode. A paraphrase or a reordered prompt is a robustness check, not an attack. An exercise drop from 0.96 to 0.70 is a phrasing the clean score hid.
- **Hallucination** — fluent content the source or the world does not support. Plausible next-token training, missing data, self-conditioning, a preference for complete answers, and an unlucky sample are different causes. Only the last one is a temperature problem. Asking the model to say it does not know, and asking for a short answer, cut some inventions and raise false refusals and concise errors. Neither inserts the missing page.

## Example

The three numbers that come up in design reviews are a softmax at two temperatures, the weight memory of a 70B model, and the Chinchilla token count. GiB means 1024 cubed bytes. `70 × 10^9` is the whiteboard count. 70,553,706,496 is the released Llama 3 70B configuration, with a separate input embedding and output projection for the 128,256 vocabulary.

```python
import math


def softmax(temperature: float) -> str:
    scaled = [logit / temperature for logit in (2.0, 1.0, 0.0)]
    largest = max(scaled)
    weights = [math.exp(item - largest) for item in scaled]
    total = sum(weights)
    return " ".join(f"{item / total:.4f}" for item in weights)


def weight_gib(params: int, bytes_per_param: int) -> float:
    return round(params * bytes_per_param / 1024**3, 1)


def chinchilla_tokens(params: int, tokens_per_param: int = 20) -> int:
    return params * tokens_per_param


print(softmax(1.0))
print(softmax(0.5))
print(weight_gib(70_000_000_000, 2), weight_gib(70_000_000_000, 1))
print(weight_gib(70_553_706_496, 2), weight_gib(70_553_706_496, 1))
print(chinchilla_tokens(70_000_000_000))
# 0.6652 0.2447 0.0900
# 0.8668 0.1173 0.0159
# 130.4 65.2
# 131.4 65.7
# 1400000000000
```

Temperature 1 leaves the leading token at about two thirds of the mass. Temperature 0.5 pushes it to about 0.867 and leaves the same token in front. The round 70B weights are 130.4 GiB in BF16. The Llama 3 70B configuration is 131.4 GiB in BF16 and 65.7 GiB in INT8. Both BF16 figures miss an 80 GiB GPU, and both INT8 figures fit. The Chinchilla rule of thumb asks a `70 × 10^9` model for 1.4 trillion tokens. A paste of 131,072 tokens on the Llama 70B attention shape adds another 40 GiB of KV cache on top of whichever weight budget you chose. The drills compute that cache, the best-of-4 bill, and a Stripe refund tool call.

## Source Chapter

- **Book chapter**: Chapter 2
- **Title**: Understanding Foundation Models

## Book Outline

- Training Data
  - Multilingual Models
  - Domain-Specific Models
- Modeling
  - Model Architecture
    - Transformer architecture
    - Other model architectures
  - Model Size
    - Scaling law: Building compute-optimal models
    - Scaling extrapolation
    - Scaling bottlenecks
- Post-Training
  - Supervised Finetuning
  - Preference Finetuning
    - Reward model
    - Finetuning using the reward model
- Sampling
  - Sampling Fundamentals
  - Sampling Strategies
    - Temperature
    - Top-k
    - Top-p
    - Stopping condition
  - Test Time Compute
  - Structured Outputs
    - Prompting
    - Post-processing
    - Constrained sampling
    - Finetuning
  - The Probabilistic Nature of AI
    - Inconsistency
    - Hallucination
- Summary

## Status

- `concepts.md` is a study set of 19 cards: training data, multilingual models, domain-specific models, the transformer, attention and the KV cache, other architectures, parameters and FLOPs, compute-optimal scaling, scaling extrapolation, scaling bottlenecks, supervised finetuning, reward models, RLHF and DPO, sampling, temperature and stopping, test-time compute, structured outputs, inconsistency, and hallucination.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: about 20 tokens per parameter, 2 bytes per BF16 parameter, GiB as 1024 cubed bytes, about `6ND` training FLOPs, and the released Llama 3 70B configuration total of 70,553,706,496 parameters. AdamW training memory is labeled twice: 16 bytes with a BF16 gradient (1,043.1 GiB at `70 × 10^9`, 1,051.3 GiB for the configuration) and 18 bytes with an FP32 gradient (1,173.5 GiB and 1,182.7 GiB). The Llama 2 7B totals, 100.4 GiB and 113.0 GiB, stay in Finetuning. A launch replaces them with a measured tokenizer, the GPU's reported memory, and the provider's current rate card.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — which tasks to give a model, and the product around the call. Architecture and sampling were deferred to this topic.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — how to score a sample once you know it is a draw, including faithfulness and a model used as a judge.
- [Prompt Engineering](../05_Prompt_Engineering/) — the instruction side of structured output, and the first adaptation lever.
- [RAG and Agents](../06_RAG_and_Agents/) — putting a source next to a model that would otherwise answer from the pretraining mix.
- [Finetuning](../07_Finetuning/) — the training mechanics behind supervised finetuning and preference updates.
- [Dataset Engineering](../08_Dataset_Engineering/) — building a corpus, when this topic's training-data card is no longer something you only inherit.
- [Inference Optimization](../09_Inference_Optimization/) — serving the KV cache, quantization, and the latency the memory math implies.
