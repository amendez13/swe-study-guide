# Dataset Engineering

Dataset engineering is how you build the examples a model learns from, and how you decide what those examples are allowed to teach. This topic covers curation, synthesis, and the processing that turns a raw export into a trainer file. The pretraining corpus a base model inherited stays in Understanding Foundation Models. Judges stay in Evaluation Methodology. The held-out set, the contamination screen, and the license on a checkpoint stay in Evaluate AI Systems. Chat templates stay in Prompt Engineering. The training run that consumes the file stays in Finetuning.

## Key Points

- **What dataset engineering is** — the examples are the work, and data-centric AI spends the next effort there while the model stays put. The finetune cannot exceed the demonstrations. The eval set is not extra training data.
- **What the data teaches** — chain-of-thought, a tool call, and a second turn have to be written in the targets. Orca trained on explanation traces. LIMA's 1,000 examples had no dialogue, and 30 hand-crafted chains were what improved multi-turn.
- **Data quality** — relevance, alignment with the task, rater consistency, a parseable format, uniqueness, and compliance. Fluency is not one of the six.
- **Data coverage** — task types, lengths, languages, and topics, including the cells where they intersect. In the exercise mix, 500 Spanish rows and 1,000 long rows do not create a long Spanish row.
- **Data quantity** — new correct cases help, and copies stop helping. A full update needs far more diverse rows than LoRA. Start the curve with a pilot on the order of fifty examples, then stage domain text before labels and synthetic rows before checked ones. LIMA aligned a 65B Llama with 1,000 diverse rows, 750 from forums and 250 written. On the exercise curve the first 900 diverse rows buy 0.22 and the next 15,000 buy 0.03.
- **Acquiring data** — public sets, consented traffic, a vendor such as Scale AI, a queue such as Label Studio, or a generator. Thumbs are not the traffic. At the exercise rate, 2,000 comparisons plus a second read and a redraw cost $3,125.00.
- **Annotation guidelines and agreement** — a decision, an example of each label, and the edge case. On an exercise slice, 64 of 80 is a percent of 0.80, and that percent is not kappa. The disagreements rewrite the guideline.
- **Why synthesize data** — quantity, coverage, quality, privacy, and distillation. Alpaca, Phi-1, Llama 3's rejection sampling and 2.7 million synthetic code examples, and Nemotron-4 340B's generate-then-filter loop are the public shapes.
- **Rule-based synthesis** — a template or a label-preserving perturbation. A paraphrase of a damaged order stays a review. Shortening the window to 14 days is a refusal, and the copied label fails.
- **Simulation** — a trace a simulator or a sandbox actually produced. Isaac Sim, CARLA, WebArena, and SWE-bench are that kind of process. A refund story with no result is not a trace.
- **AI-powered synthesis** — self-play needs an external score. A translation round trip needs a label check. Sennrich's back-translation is a different procedure.
- **Back-translation** — Sennrich, Haddow, and Birch, ACL 2016, is one reverse translation onto real monolingual text. A round trip is a paraphrase. For a language the model barely writes, keep the human sentence on the side users will read. "Leave the charge in place" is still a refusal, and "refund the order" is not.
- **Instruction data synthesis** — Self-Instruct turned 175 seeds into 52,445 instructions. Evol-Instruct has five in-depth rewrites and a long-tail in-breadth rewrite. Instruction backtranslation writes a prompt for a human document and then has to curate.
- **Long-context synthesis** — a real long source, and an answer that is a span or a check. Llama 3's ablation mixed synthetic long-context rows at 0.1 percent. "30 days from delivery" stays. A restocking fee that is not in the contract goes.
- **Verifying synthetic data** — execute what you can, apply a heuristic, and only then a calibrated judge. The judge does not outvote a failed parser. Llama 3 keeps a row when either the reward model or the Llama quality score marks it high quality.
- **Limits of AI-generated data** — fluent errors, style without the right answer, and model collapse under recursive replacement. Shumailov and coauthors, Nature 2024, is the collapse result. One checked slice mixed into human data is a different regime.
- **Data lineage** — teacher, version, seed, filter, and license for a synthetic row. Phi-1 omits some synthetic-generation details for proprietary reasons, so the student file still gets a contamination check.
- **Model distillation** — soft targets carry the teacher's uncertainty. DistilBERT is the published encoder student. An API teacher usually forces training on the text. OpenAI's consumer terms and the January 1, 2026 Services Agreement forbid using outputs to train a competing model. The exception is in the Services Agreement.
- **Reasoning-trace distillation** — the steps have to be in the target. DeepSeek-R1's students are Qwen and Llama models from 1.5B to 70B, supervised on about 800,000 samples, about 600,000 of them reasoning trajectories. The reinforcement-learning comparison is the 32B result. A trace that writes 100 for 48 times 2 is dropped.
- **Inspecting a dataset** — distributions plus a read. In the exercise sample the mean length is 191.7 and the median is 40.5. Trial-run a slice, and write a new versioned file instead of editing the canonical one in place. A datasheet records the source, the filters, and the license.
- **Deduplicating data** — exact hash, MinHash for Jaccard, LSH to limit comparisons, and decontamination against the eval set. The refund sentences have Jaccard 0.7143. The eight-document file falls from 8 to 5 to 4. When you own the finetune, the overlapping row leaves the training file.
- **Semantic deduplication** — SemDeDup embeds, clusters, and drops neighbors above a cosine threshold. The 50 percent figure is a LAION result, not a quota. In the exercise, cosine 0.9600 is over 0.9 and 0.0000 is not.
- **Cleaning and filtering** — C4-style heuristics, FineWeb-Edu's classifier, CCNet's Wikipedia perplexity, a toxicity rule that matches the product, and a privacy pass. Delete the rows that demonstrate a behavior you are trying to stop. A sentence that says "don't" next to a hundred demonstrations is the weaker gradient. A phone regex catches `555-010-0142` and misses the spelled-out number. C4's bad-word list also removed medical text and some dialects. Sample what you drop.
- **Selecting which rows to keep** — spend the label budget on unsure and rare rows, cap the dominant pattern, and keep a random floor. The exercise round labels 300 of 5,000. DSIR-style resampling toward a trusted target is a different lever.
- **Formatting training data** — messages for supervised rows, chosen and rejected for preference rows, and the chat template that shipped with the weights. Turn a few-shot prompt into training rows and serve the short instruction you trained on. ChatML and a missing blank line are different strings. On a 100-token prompt and a 20-token answer, 0.167 is the answer's share of an unmasked loss. An unregistered end-of-turn token splits one boundary into many pieces.

## Example

The planning numbers are a MinHash estimate, a two-pass dedup, an annotation bill, and a quantity curve. The win rates and the label price are exercises. LIMA's 1,000 is the public count. The Jaccard and the eight-document reduction are computed from the strings in the block.

```python
import hashlib


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    tokens = norm(text).split()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    return len(left & right) / len(left | right)


def minhash(grams: set[tuple[str, ...]], seeds: range) -> list[int]:
    signature = []
    for seed in seeds:
        best = None
        for gram in grams:
            digest = hashlib.sha256(f"{seed}:{gram}".encode()).hexdigest()
            value = int(digest[:16], 16)
            best = value if best is None or value < best else best
        signature.append(best)
    return signature


left = shingles("the refund window is thirty days from delivery")
right = shingles("the refund window is thirty days from shipment")
exact = jaccard(left, right)
a = minhash(left, range(128))
b = minhash(right, range(128))
estimate = sum(x == y for x, y in zip(a, b)) / 128
docs = [
    "Reset your password from the settings page.",
    "Reset your password from the settings page.",
    "reset your password from the settings page.",
    "Reset your password from the settings screen.",
    "Where is my order 1001?",
    "Where is my order 1002?",
    "Where is my order 1001?",
    "The capital of France is Paris.",
]
seen: set[str] = set()
exact_kept = []
for doc in docs:
    digest = hashlib.sha256(norm(doc).encode()).hexdigest()
    if digest not in seen:
        seen.add(digest)
        exact_kept.append(doc)
near_kept = []
for doc in exact_kept:
    grams = shingles(doc)
    if all(jaccard(grams, shingles(kept)) < 0.65 for kept in near_kept):
        near_kept.append(doc)
prompts = 2_000
rate = 1.25
labels = prompts + round(prompts * 0.15) + round(prompts * 0.10)
diverse = (0.62, 0.84, 0.87)
print(f"{exact:.4f} {estimate:.4f}")
print(len(docs), len(exact_kept), len(near_kept))
print(f"{labels * rate:.2f}")
print(f"{diverse[1] - diverse[0]:.2f} {diverse[2] - diverse[1]:.2f}")
# 0.7143 0.7109
# 8 5 4
# 3125.00
# 0.22 0.03
```

The refund sentences share 5 of 7 shingles, Jaccard 0.7143, and 128 hash functions estimate 0.7109 on this run. The eight-document file falls to 5 after an exact hash and to 4 after a Jaccard threshold of 0.65. Two thousand exercise comparisons, plus a 15 percent second read and a 10 percent redraw, cost $3,125.00 at $1.25 a label. On the exercise curve, diverse data gains 0.22 by 1,000 rows and 0.03 after that. The drills apply the same habits to a rare Zendesk intent, a SQL pair that has to execute, a repeated complaint, a leaked eval, an OpenAI output clause, a preference pair rendered in two wrappers, a fluent wrong refund, and a moderation label a bad-word list deleted.

## Source Chapter

- **Book chapter**: Chapter 8
- **Title**: Dataset Engineering

## Book Outline

- Data Curation
  - Data Quality
  - Data Coverage
  - Data Quantity
  - Data Acquisition and Annotation
- Data Augmentation and Synthesis
  - Why Data Synthesis
  - Traditional Data Synthesis Techniques
    - Rule-based data synthesis
    - Simulation
  - AI-Powered Data Synthesis
    - Instruction data synthesis
    - Data verification
    - Limitations to AI-generated data
  - Model Distillation
- Data Processing
  - Inspect Data
  - Deduplicate Data
  - Clean and Filter Data
  - Format Data
- Summary

## Status

- `concepts.md` is a study set of 25 cards: what dataset engineering is, what the data teaches, data quality, data coverage, data quantity, acquiring data, annotation guidelines and agreement, why synthesize data, rule-based synthesis, simulation, AI-powered synthesis, back-translation, instruction data synthesis, long-context synthesis, verifying synthetic data, limits of AI-generated data, data lineage, model distillation, reasoning-trace distillation, inspecting a dataset, deduplicating data, semantic deduplication, cleaning and filtering, selecting which rows to keep, and formatting training data. The key points above are the chapter summary.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are a computed Jaccard and MinHash estimate, an eight-document dedup, an exercise annotation bill, and an exercise quantity curve. A launch replaces the exercise prices and win rates with the contract, the queue, and the slice you measured. LIMA's 1,000 examples, Self-Instruct's 52,445 instructions, and the cited model reports are the public counts. OpenAI's consumer terms and Services Agreement are both cited as effective January 1, 2026. The May 1, 2025 business terms are the previous page.
- Pretraining mix and the supervised-finetuning ceiling stay in Understanding Foundation Models. Judge calibration stays in Evaluation Methodology. Eval annotation, the n-gram contamination screen, and checkpoint licenses stay in Evaluate AI Systems. The chat-template encoding stays in Prompt Engineering. The training run stays in Finetuning.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — prompting, retrieval, and finetuning as the three levers. This topic builds the examples the third lever consumes.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — the pretraining corpus, supervised finetuning, preference data, and why the demonstrations set the ceiling.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — AI judges, their biases, and Cohen's kappa for a double-labeled slice.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — how eval data is annotated, the contamination screen, and the license on a checkpoint.
- [Prompt Engineering](../05_Prompt_Engineering/) — the chat template the training file and the server both have to apply.
- [RAG and Agents](../06_RAG_and_Agents/) — the tools whose executed traces this topic would train on.
- [Finetuning](../07_Finetuning/) — the run, the answer-token mask, and distillation as a reason to train.
- [Inference Optimization](../09_Inference_Optimization/) — serving the student you distilled once the training file is real.
- [AI Engineering Architecture and User Feedback](../10_AI_Engineering_Architecture_and_User_Feedback/) — the product feedback that becomes the next flywheel, once this file exists.
