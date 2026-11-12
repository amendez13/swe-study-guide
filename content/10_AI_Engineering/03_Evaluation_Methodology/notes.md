# Evaluation Methodology

Evaluation methodology is how you score a sample from a foundation model. This topic covers why that score is hard, the language-model losses behind perplexity, exact checks against tests and references, embeddings, a model used as a judge, and ranking models from pairwise votes. The launch pipeline, the criteria catalog, and the survey of public benchmarks live in the next topic.

## Key Points

- **Why evaluation is hard** — many answers can be acceptable, one model serves many tasks, each call is a sample, and public benchmarks leak and then saturate. Metrics that all sound like quality can move in opposite directions.
- **Entropy** — average surprise of a distribution. A fair coin is 1 bit. A 0.9/0.1 coin is about 0.469 bits. Entropy is the floor under the training loss, not the loss itself.
- **Cross entropy** — the model's surprise on the data's outcomes. It equals entropy plus the KL penalty. On a 0.7, 0.2, 0.1 distribution, a model that says 0.5, 0.3, 0.2 pays 1.2796 bits against an entropy of 1.1568 bits.
- **Bits per character and bits per byte** — total cross entropy divided by the original text, so two tokenizers can be compared. On an exercise file, the lower perplexity was the worse encoding.
- **Perplexity** — `e` to the mean loss in nats. A loss of 2.0 nats is perplexity 7.3891. Treating that 2.0 as bits yields 4. Lower means a tighter fit to that text, under that tokenizer.
- **How to read perplexity** — a training curve, a domain probe, and a corpus filter. Not a ranking across tokenizers. A rise after post-training can be the objective changing, the alignment tax, rather than the chat model getting worse.
- **Exact and subjective** — a program marks code, labels, and query results. A judgment marks tone and usefulness. A feature usually has both, and each field uses its own tool. A schema check is exact and is not the business rule.
- **Functional correctness** — HumanEval's 164 problems and a SWE-bench patch are right when tests pass. With 3 successes in 10 draws, unbiased pass@5 is 0.9167 and the independence plug-in is 0.8319. Text-to-SQL is right when the result table matches.
- **Exact match** — equality after a normalization you wrote down. SQuAD reports it, with token F1, for short spans. It is the wrong metric for a paraphrase or for code you could have executed.
- **Lexical similarity** — edit distance and n-gram overlap. "$12.50" and "$125.0" are Levenshtein distance 2. BLEU is precision with a brevity penalty. A half-length candidate is multiplied by about 0.3679. Shared words do not make a fact true.
- **Semantic similarity** — embeddings, BERTScore, and an NLI entailment check score meaning, including a paraphrase BLEU misses. A negated policy or a swapped number can still look similar. The amount stays on an exact check.
- **Embeddings** — vectors trained so similar texts point the same way. Cosine, not the raw dot product, cancels length. On (1, 2, 2) and (2, 1, 2) the cosine is 8/9. Sentence-BERT, E5, BGE, Cohere Embed, and text-embedding-3 are real models. The score is not a probability.
- **Why use an AI judge** — open text has no unit test, and people cannot relabel every prompt change. On MT-Bench, a GPT-4 judge agreed with people more than 80 percent of the time, in the human-human range for that study. Your rubric starts uncalibrated.
- **How to use an AI judge** — pointwise scores, pairwise wins, a reference or a source, and a rubric whose levels are checks. Pin the judge. Chance-corrected agreement on a human slice, and a read of the disagreements, is the calibration.
- **Limits of an AI judge** — inconsistency, a vague criterion, cost and latency, and bias. Swap the order for position bias. Hold length fixed for verbosity. Do not let a model grade its own family and call that an evaluation.
- **Which models can judge** — a stronger model for open-ended quality, the same model only for its own preference, a weaker model only where you measured it, and a reward model or an NLI checker for a narrow job. A parser does not need a judge.
- **Ranking from pairwise votes** — Elo updates online and depends on order. From 1500 and 1500, one win at K of 32 goes to 1516 and 1484. Bradley-Terry fits the whole matrix. Chatbot Arena has used both, on an Elo-like scale. Cite the method and the date.
- **Challenges of comparative evaluation** — five models are 10 pairs and twenty are 190. Votes need guidelines, gold pairs, and your traffic, not only a copied arena UI. The winner of a weak pool can still fail an absolute check.
- **Where comparative evaluation is going** — a standing system: pairwise ranks with intervals, private sets from production traffic, exact checks on every field a program can decide, and a calibrated judge for the residue. A public rank is context, not the launch gate.

## Example

The numbers that come up in an eval review are a coin's entropy, the base under a perplexity, a bits-per-byte comparison that reverses a perplexity ranking, a pass@k, and one Elo step. The tokenizer losses are an exercise, not a published model card. The drills compute a real tokenizer jump, a judge's kappa, a position swap, a BLEU that prefers the wrong window, and a five-model ranking.

```python
import math


def entropy_bits(probabilities: tuple[float, ...]) -> float:
    return -sum(p * math.log(p, 2) for p in probabilities if p > 0.0)


def pass_at_k(n: int, c: int, k: int) -> float:
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def expected(left: float, right: float) -> float:
    return 1 / (1 + 10 ** ((right - left) / 400))


loss_nats = 2.0
ln2 = math.log(2)
print(f"{entropy_bits((0.5, 0.5)):.4f} {entropy_bits((0.9, 0.1)):.4f}")
print(f"{math.exp(loss_nats):.4f} {2 ** loss_nats:.4f}")
print(f"{(2.0 * 250) / (1000 * ln2):.4f} {(1.4 * 400) / (1000 * ln2):.4f}")
print(f"{pass_at_k(10, 3, 5):.4f}")
print(1500 + 32 * (1 - expected(1500, 1500)), f"{expected(1900, 1500):.4f}")
# 1.0000 0.4690
# 7.3891 4.0000
# 0.7213 0.8079
# 0.9167
# 1516.0 0.9091
```

A fair coin is 1 bit and a 0.9/0.1 coin is about 0.469 bits. A loss of 2.0 is perplexity 7.3891 in nats and 4 if those units were already bits. On 1,000 bytes, 250 tokens at 2.0 nats is 0.7213 bits per byte, and 400 tokens at 1.4 nats is 0.8079, so the lower perplexity is the worse encoding. Three successes in ten draws give unbiased pass@5 of 0.9167. One Elo win from 1500 against 1500, at K of 32, lands on 1516, and a 400-point favorite has expected score 0.9091.

## Source Chapter

- **Book chapter**: Chapter 3
- **Title**: Evaluation Methodology

## Book Outline

- Challenges of Evaluating Foundation Models
- Understanding Language Modeling Metrics
  - Entropy
  - Cross Entropy
  - Bits-per-Character and Bits-per-Byte
  - Perplexity
  - Perplexity Interpretation and Use Cases
- Exact Evaluation
  - Functional Correctness
  - Similarity Measurements Against Reference Data
    - Exact match
    - Lexical similarity
    - Semantic similarity
  - Introduction to Embedding
- AI as a Judge
  - Why AI as a Judge?
  - How to Use AI as a Judge
  - Limitations of AI as a Judge
    - Inconsistency
    - Criteria ambiguity
    - Increased costs and latency
    - Biases of AI as a judge
  - What Models Can Act as Judges?
- Ranking Models with Comparative Evaluation
  - Challenges of Comparative Evaluation
    - Scalability bottlenecks
    - Lack of standardization and quality control
    - From comparative performance to absolute performance
  - The Future of Comparative Evaluation
- Summary

## Status

- `concepts.md` is a study set of 19 cards: why evaluation is hard, entropy, cross entropy, bits per character and bits per byte, perplexity, how to read perplexity, exact and subjective evaluation, functional correctness, exact match, lexical similarity, semantic similarity, embeddings, why use an AI judge, how to use an AI judge, limits of an AI judge, which models can judge, ranking from pairwise votes, challenges of comparative evaluation, and where comparative evaluation is going.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: logarithms, a pass@k estimator, cosine on hand vectors, an Elo step, and exercise losses and token prices. A launch replaces them with a measured tokenizer, the provider's current rate card, and labels from the queue you ship to.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — which tasks get a model, and the quality bar a metric has to serve.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — why a call is a sample, and the reward model a pairwise judge can train.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — criteria, benchmarks, and the pipeline that turns this methodology into a launch gate.
- [Prompt Engineering](../05_Prompt_Engineering/) — the instruction side of a judge prompt and of the feature being measured.
- [RAG and Agents](../06_RAG_and_Agents/) — where embeddings retrieve a source, and where faithfulness is a check against that source.
- [Finetuning](../07_Finetuning/) — supervised and preference updates, which are what a post-training perplexity change is reacting to.
