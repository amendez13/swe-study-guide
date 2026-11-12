# Dataset Engineering

Dataset engineering is how you build the examples a model learns from, and how you decide what those examples are allowed to teach. This topic covers curation, synthesis, and the processing that turns a raw export into a trainer file. The pretraining corpus a base model inherited stays in Understanding Foundation Models. Judges stay in Evaluation Methodology. The held-out set, the contamination screen, and the license on a checkpoint stay in Evaluate AI Systems. Chat templates stay in Prompt Engineering. The training run that consumes the file stays in Finetuning.

## Key Points

- **What dataset engineering is** — the examples are the work, and data-centric AI spends the next effort there while the model stays put. The finetune cannot exceed the demonstrations. The eval set is not extra training data.
- **What the data teaches** — chain-of-thought, a tool call, and a second turn have to be written in the targets. Orca trained on explanation traces. LIMA's 1,000 examples had no dialogue, and 30 hand-written chains were what improved multi-turn.
- **Data quality** — relevance, alignment with the task, rater consistency, a parseable format, uniqueness, and compliance. Fluency is not one of the six.
- **Data coverage** — task types, lengths, languages, and topics, including the cells where they intersect. In the exercise mix, 500 Spanish rows and 1,000 long rows do not create a long Spanish row.
- **Data quantity** — new correct cases help, and copies stop helping. LIMA aligned a 65B LLaMa with 1,000 diverse rows, 750 from forums and 250 written. On the exercise curve the first 900 diverse rows buy 0.22 and the next 15,000 buy 0.03.
- **Acquiring and annotating data** — public sets, consented traffic, a vendor such as Scale AI, a queue such as Label Studio, or a generator. Thumbs are not the traffic. At the exercise rate, 2,000 comparisons plus a second read and a redraw cost $3,125.00.
- **Why synthesize data** — quantity, coverage, quality, privacy, and distillation. Alpaca, Phi-1, Llama 3's rejection sampling, and Nemotron-4 340B's generate-then-filter loop are the public shapes.
- **Rule-based synthesis** — a template or a label-preserving perturbation. A paraphrase of a damaged order stays a review. Shortening the window to 14 days is a refusal, and the copied label fails.
- **Simulation** — a trace a simulator or a sandbox actually produced. Isaac Sim, CARLA, WebArena, and SWE-bench are that kind of process. A refund story with no result is not a trace.
- **AI-powered synthesis** — self-play needs an external score, paraphrase and back-translation need a label check, and translation is a bridge rather than the missing language.
- **Instruction data synthesis** — Self-Instruct turned 175 seeds into 52,445 instructions. Evol-Instruct raises difficulty. Instruction backtranslation writes a prompt for a human document and then has to curate. Long-context rows need a real source and a checkable answer.
- **Verifying synthetic data** — execute what you can, apply a heuristic, and only then a calibrated judge. The judge does not outvote a failed parser.
- **Limits of AI-generated data** — fluent errors, style without the right answer, model collapse under recursive replacement, an unseen teacher corpus, and a contract. Shumailov and coauthors, Nature 2024, is the collapse result. One checked slice mixed into human data is a different regime.
- **Model distillation** — soft targets carry the teacher's uncertainty. DistilBERT is the published encoder student. An API teacher usually forces training on the text, and DeepSeek-R1's students train on about 800,000 traces. OpenAI's terms forbid using outputs to train a competing model, with a narrow exception.
- **Inspecting a dataset** — distributions plus a read. In the exercise sample the mean length is 191.7 and the median is 40.5. A datasheet records the source, the filters, and the license.
- **Deduplicating data** — exact hash, MinHash for Jaccard, LSH to limit comparisons, semantic dedup for paraphrases, and decontamination against the eval set. The refund sentences have Jaccard 0.7143. The eight-document file falls from 8 to 5 to 4. The overlapping row leaves the training file.
- **Cleaning and filtering** — C4-style heuristics, quality classifiers, a toxicity rule that matches the product, and a privacy pass. A phone regex catches `555-010-0142` and misses the spelled-out number. Sample what you drop.
- **Selecting which rows to keep** — spend the label budget on unsure and rare rows, cap the dominant pattern, and keep a random floor. The exercise round labels 300 of 5,000. DSIR-style resampling toward a trusted target is a different lever.
- **Formatting training data** — messages for supervised rows, chosen and rejected for preference rows, and the chat template that shipped with the weights. ChatML and a missing blank line are different strings. An unregistered end-of-turn token splits one boundary into many pieces.

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

The refund sentences share 5 of 7 shingles, Jaccard 0.7143, and 128 hash functions estimate 0.7109 on this run. The eight-document file falls to 5 after an exact hash and to 4 after a Jaccard threshold of 0.65. Two thousand exercise comparisons, plus a 15 percent second read and a 10 percent redraw, cost $3,125.00 at $1.25 a label. On the exercise curve, diverse data gains 0.22 by 1,000 rows and 0.03 after that. The drills apply the same habits to a rare Zendesk intent, a SQL pair that has to execute, a repeated complaint, a leaked eval, an OpenAI output clause, a Llama 3 transcript, a fluent wrong refund, and a phone number a regex missed.

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

- `concepts.md` is a study set of 19 cards: what dataset engineering is, what the data teaches, data quality, data coverage, data quantity, acquiring and annotating data, why synthesize data, rule-based synthesis, simulation, AI-powered synthesis, instruction data synthesis, verifying synthetic data, limits of AI-generated data, model distillation, inspecting a dataset, deduplicating data, cleaning and filtering, selecting which rows to keep, and formatting training data. The key points above are the chapter summary.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are a computed Jaccard and MinHash estimate, an eight-document dedup, an exercise annotation bill, and an exercise quantity curve. A launch replaces the exercise prices and win rates with the contract, the queue, and the slice you measured. LIMA's 1,000 examples, Self-Instruct's 52,445 instructions, and the cited model reports are the public counts.
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
