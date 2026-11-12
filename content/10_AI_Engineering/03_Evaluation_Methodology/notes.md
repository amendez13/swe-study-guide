# Evaluation Methodology

Evaluation methodology is how you score a sample from a foundation model. This topic covers why that score is hard, the language-model losses behind perplexity, exact checks against tests and references, embeddings, a model used as a judge, and ranking models from pairwise votes. The launch pipeline, the criteria catalog, and the survey of public benchmarks live in the next topic.

## Key Points

- **Why evaluation is hard** — many answers can be acceptable, one model serves many tasks, each call is a sample, and public benchmarks leak and then saturate. Metrics that all sound like quality can move in opposite directions.
- **Entropy** — average surprise of a distribution. A fair coin is 1 bit. A 0.9/0.1 coin is about 0.469 bits. Entropy is the floor under the training loss, not the loss itself.
- **Cross entropy** — the model's surprise on the data's outcomes. It equals entropy plus the KL penalty. On a 0.7, 0.2, 0.1 distribution, a model that says 0.5, 0.3, 0.2 pays 1.2796 bits against an entropy of 1.1568 bits.
- **Bits per character and bits per byte** — total cross entropy divided by the original text, so two tokenizers can be compared. On an exercise file, the lower perplexity was the worse encoding.
- **Perplexity** — `e` to the mean loss in nats. A loss of 2.0 nats is perplexity 7.3891. Treating that 2.0 as bits yields 4. Lower means a tighter fit to that text, under that tokenizer.
- **How to read perplexity** — a training curve, a domain probe, a corpus filter, and a contamination smell only against a matched control. Structured text scores lower, a larger vocabulary scores higher, and a longer context usually scores lower, so compare at the same tokenizer, mix, and length. Not a ranking across tokenizers. InstructGPT's alignment tax was a regression on public tasks such as SQuAD, reduced by mixing pretraining updates back into PPO. A Wikipedia perplexity rise is that objective change, not by itself a reason to revert.
- **Exact and subjective** — a program marks code, labels, and query results. A judgment marks tone and usefulness. A factual or medical answer is not a preference, and forcing the pick writes a vote the ranker will treat as taste. Comparative evaluation ranks two answers. An A/B test measures a live product metric. A feature usually has both exact and subjective fields, and each field uses its own tool. A schema check is exact and is not the business rule.
- **Functional correctness** — HumanEval's 164 problems are right when the unit tests pass. A SWE-bench patch is resolved when the fail-to-pass tests pass and the pass-to-pass tests still pass. With 3 successes in 10 draws, unbiased pass@5 is 0.9167 and the plug-in is 0.8319, biased low. Text-to-SQL follows the result the user asked for. Spider's original score matches SQL components. BIRD runs the query.
- **Exact match** — equality after a normalization you wrote down. SQuAD reports it, with token F1, for short spans. It is the wrong metric for a paraphrase or for code you could have executed.
- **Lexical similarity** — edit distance, BLEU, ROUGE, and METEOR. "$12.50" and "$125.0" are Levenshtein distance 2. BLEU is precision with a brevity penalty. A half-length candidate is multiplied by about 0.3679. METEOR aligns stems and synonyms and still misses a swapped window. Shared words do not make a fact true.
- **Semantic similarity** — embeddings, BERTScore, and an NLI entailment check score meaning, including a paraphrase BLEU misses. A negated policy or a swapped number can still look similar. The amount stays on an exact check.
- **Embeddings** — vectors trained so similar texts point the same way. Cosine, not the raw dot product, cancels length. On (1, 2, 2) and (2, 1, 2) the cosine is 8/9. Sentence-BERT, E5, BGE, Cohere Embed, and text-embedding-3 are real models. The score is not a probability.
- **Why use an AI judge** — open text has no unit test, and people cannot relabel every prompt change. On MT-Bench, GPT-4 agreed with experts about 85 percent of the time with ties removed, and about 66 percent with ties and order flips counted as ties. Both sit near expert agreement under the same counting. The abstract's "over 80 percent" is the non-tie number. Your rubric starts uncalibrated.
- **How to use an AI judge** — pointwise scores, pairwise wins, a reference or a source, and a rubric whose levels are checks. A self-critique is a revision step, not the score that ships. Pin the judge. Chance-corrected agreement on a human slice, and a read of the disagreements, is the calibration.
- **Limits of an AI judge** — inconsistency, a vague criterion, cost and latency, and limited reasoning. On a 10-question math probe, GPT-4's default prompt accepted a wrong answer on 14 of 20 judgments, and a separate reference cut that to 3 of 20.
- **Biases of an AI judge** — position, verbosity, and a self-enhancement effect the MT-Bench paper looked for and did not establish. On similar answers, GPT-4 was consistent across a swap 65.0 percent of the time. On 23 padded lists, GPT-4 preferred the padding 8.7 percent of the time and the other judges they tried 91.3 percent. Swap the order. Hold length fixed when the fact is the question.
- **Which models can judge** — a stronger model for open-ended quality, the same model only for its own preference, a weaker model only where you measured it, and a specialized scorer for a narrow job. A reward model scores one completion. A reference-based judge uses a gold answer. A preference model, such as PandaLM, JudgeLM, or Prometheus, picks between two. A parser does not need a judge.
- **Ranking from pairwise votes** — Elo updates online and depends on order. From 1500 and 1500, one win at K of 32 goes to 1516 and 1484. Bradley-Terry fits the whole matrix and assumes transitivity, so a cycle in the votes is not three strengths on a line. Sparse pairing fills the edges you did not annotate with that assumption. Arena launched in May 2023 on online Elo, moved to Bradley-Terry, and later made style control a default. Under their scale, 400 points is 10-to-1. Cite the method, the date, and the style setting.
- **Challenges of comparative evaluation** — five models are 10 pairs, twenty are 190, and fifty votes on those 190 pairs is 9,500 judgments. Sample pairs with an estimator that matches the sampling. Votes need guidelines, gold pairs, hidden names, a tie rule, and your traffic.
- **From a ranking to a pass** — Elo and Bradley-Terry have no unit for correct. Style control is still a preference. The winner of a weak pool can fail an absolute check. The ranking chooses who earns the eval. The eval chooses the launch.
- **Where comparative evaluation is going** — the public board already has Bradley-Terry, intervals, category boards, and style control. The private half is still the work: production prompts kept out of training, exact checks on every field a program can decide, and a calibrated judge for the residue. A public rank is context, not the launch gate.

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

- `concepts.md` is a study set of 21 cards: why evaluation is hard, entropy, cross entropy, bits per character and bits per byte, perplexity, how to read perplexity, exact and subjective evaluation, functional correctness, exact match, lexical similarity, semantic similarity, embeddings, why use an AI judge, how to use an AI judge, limits of an AI judge, biases of an AI judge, which models can judge, ranking from pairwise votes, challenges of comparative evaluation, from a ranking to a pass, and where comparative evaluation is going.
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
