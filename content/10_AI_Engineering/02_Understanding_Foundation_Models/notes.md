# Understanding Foundation Models

A foundation model is a base checkpoint plus the choices that make its output usable: the data it continued, the architecture that reads a prompt, the post-training that turns continuation into an answer, and the sampler that picks the next token. This topic is those choices. It stays with public models and public numbers. Evaluation metrics, prompt recipes, retrieval mechanics, the finetune training stack, and serving kernels live in the later topics.

## Key Points

- **Training data** — the base model learns to continue filtered web text, code, and curated prose. It is strongest where that mix was dense. Private facts were never in it.
- **Multilingual models** — one checkpoint serves many languages, and the tokenizer plus the data mix still make them unequal. Some languages cost more tokens and score worse. Measure both.
- **Domain-specific models** — Codex, Code Llama, StarCoder, BloombergGPT, and Med-PaLM put more training on one field. Use one when an eval says a general model is short on that field. Retrieval owns facts that change.
- **The transformer** — attention over the sequence, from the 2017 encoder-decoder. Decoder-only causal models write ChatGPT, Copilot, and the public Llama and Mistral checkpoints. BERT keeps the encoder.
- **Attention, the KV cache, and context** — each new token reuses stored keys and values. On a Llama 70B shape in BF16, one request is 1.25 GiB of cache at 4,096 tokens and 40 GiB at 131,072 tokens.
- **Other architectures** — Mamba and RWKV keep a fixed state instead of a growing cache, and they give up exact lookup of an earlier token. Jamba keeps some attention layers. Mixtral is still a transformer.
- **Parameters, tokens, and FLOPs** — a 70B model is 130.4 GiB of BF16 weights and 65.2 GiB at INT8. Dense training FLOPs are about `6ND`. A mixture of experts stores more parameters than it uses on each token. A full Adam update is on the order of 18 bytes per parameter.
- **Compute-optimal scaling** — Chinchilla's rule of thumb is about 20 tokens per parameter for a fixed training-FLOP budget. A 70B model wants about 1.4 trillion tokens. Llama 3's published scale, about 15 trillion tokens, trains smaller models past that ratio because inference is paid on every request.
- **Scaling extrapolation and bottlenecks** — a curve fit on smaller runs does not include running out of high-quality data, a megawatt cap, or a product metric that has stopped tracking token loss. Some apparent capability jumps are the scoring rule.
- **Supervised finetuning** — prompt-and-answer pairs, with the loss on the answer tokens, teach a base model to reply. The demonstrations set the ceiling. This does not rank two plausible answers.
- **Reward models** — a Bradley-Terry scorer on preference pairs. It can train a policy or pick the best of N samples. It also learns shortcuts in the comparisons, and length is the usual one.
- **RLHF and DPO** — InstructGPT is supervised finetuning, then a reward model, then PPO with a KL penalty. DPO trains on pairs directly and skips the reward head and the online loop. Fresh documents stay in retrieval.
- **Sampling from logits** — softmax turns logits into probabilities. On the scores 2, 1, and 0, temperature 1 gives about 0.665, 0.245, and 0.090. Temperature 0.5 gives about 0.867, 0.117, and 0.016. The leading token does not change.
- **Temperature, top-k, top-p, and stopping** — temperature reshapes the gaps, top-k and top-p drop the tail, and a stop string or a token cap ends the sample. Move one knob. Do not stop on a string that a valid answer can contain.
- **Test-time compute** — extra samples or extra reasoning tokens, as in best-of-N, self-consistency, o1, and DeepSeek-R1. They help when a verifier can reject a failure. Inline ghost text cannot spend them.
- **Structured outputs** — prompting, post-processing, constrained sampling, and finetuning. A schema mask removes illegal syntax. A parser still checks the values, because a valid object can hold a false total.
- **Inconsistency** — the fact stayed put and the answer moved, across samples or across phrasings. Agreement and support are different tests. Sampling knobs reduce sample variance and repeat a wrong mode.
- **Hallucination** — fluent content the source or the world does not support. Plausible next-token training, missing data, self-conditioning, a preference for complete answers, and an unlucky sample are different causes. Only the last one is a temperature problem.

## Example

The three numbers that come up in design reviews are a softmax at two temperatures, the weight memory of a 70B model, and the Chinchilla token count. GiB means 1024 cubed bytes.

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
print(chinchilla_tokens(70_000_000_000))
# 0.6652 0.2447 0.0900
# 0.8668 0.1173 0.0159
# 130.4 65.2
# 1400000000000
```

Temperature 1 leaves the leading token at about two thirds of the mass. Temperature 0.5 pushes it to about 0.867 and leaves the same token in front. The 70B weights are 130.4 GiB in BF16, which misses an 80 GiB GPU, and 65.2 GiB in INT8, which fits. The Chinchilla rule of thumb asks that 70B model for 1.4 trillion tokens. A paste of 131,072 tokens on the Llama 70B attention shape adds another 40 GiB of KV cache on top of whichever weight budget you chose. The drills compute that cache, the best-of-8 bill, and the broken-JSON repair.

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

- `concepts.md` is a study set of 18 cards: training data, multilingual models, domain-specific models, the transformer, attention and the KV cache, other architectures, parameters and FLOPs, compute-optimal scaling, extrapolation and bottlenecks, supervised finetuning, reward models, RLHF and DPO, sampling, temperature and stopping, test-time compute, structured outputs, inconsistency, and hallucination.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: about 20 tokens per parameter, 2 bytes per BF16 parameter, GiB as 1024 cubed bytes, and about `6ND` training FLOPs. A launch replaces them with a measured tokenizer, the GPU's reported memory, and the provider's current rate card.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — which tasks to give a model, and the product around the call. Architecture and sampling were deferred to this topic.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — how to score a sample once you know it is a draw, including faithfulness and a model used as a judge.
- [Prompt Engineering](../05_Prompt_Engineering/) — the instruction side of structured output, and the first adaptation lever.
- [RAG and Agents](../06_RAG_and_Agents/) — putting a source next to a model that would otherwise answer from the pretraining mix.
- [Finetuning](../07_Finetuning/) — the training mechanics behind supervised finetuning and preference updates.
- [Dataset Engineering](../08_Dataset_Engineering/) — building a corpus, when this topic's training-data card is no longer something you only inherit.
- [Inference Optimization](../09_Inference_Optimization/) — serving the KV cache, quantization, and the latency the memory math implies.
