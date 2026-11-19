# Evaluate AI Systems

This topic turns a scoring toolkit into a launch decision. It covers what you measure, how you choose a model, how you read a public benchmark, and how you build the pipeline that produces the number you ship on. Exact checks, similarity, judges, and pairwise rankings stay in the previous topic. This one points at them and does not re-derive them.

## Key Points

- **Evaluation criteria** — domain capability, generation quality, instruction following, and cost and latency. Fluency and coherence are the older generation pair, and they pass a fluent wrong window. The criteria are about the system the user touches. A leaderboard is not the list.
- **Domain-specific capability** — MMLU is 57 four-choice subjects and has saturated for frontier models. MMLU-Pro is the ten-choice revision. GPQA is 448 gated graduate-science questions, and leaderboards usually quote the 198-question diamond subset. HumanEval, SWE-bench, and LiveCodeBench measure code by running it. A letter grade is not the product's answer.
- **Factual consistency** — local consistency checks the source, with an entailment judgment. Global consistency checks a named source. SelfCheckGPT only flags claims that change across samples. FActScore is precision against that source, not truth in the world. SAFE searches. A date still wants an exact match.
- **Safety** — Llama Guard 3 emits an MLCommons hazard label. The OpenAI moderation endpoint uses a different list. The license and the product policy both bind you. Score refusals and over-refusals, on the generator and on the filter. TruthfulQA is imitative falsehood, not a hazard taxonomy.
- **Instruction following** — IFEval grades 541 prompts and 25 verifiable instruction types with a program. Prompt-level strict fails a reply that misses one constraint. Loose scoring tries eight variants. InFoBench's 2,250 decomposed requirements are a judge. A schema mask owns the format, and the model is graded on the values.
- **Roleplaying** — Character.AI, a custom GPT, and a brand-voice bot have to hold a role for the session. A leaked instruction is an exact fail. The launch number is conversations that held, not the average turn.
- **Latency** — TTFT plus TPOT times the remaining tokens. At 0.400 seconds and 0.020 seconds, 500 output tokens take 10.38 seconds, a 50 token-per-second decode and a 48.17 token-per-second end-to-end rate. Throughput counts finished requests. Goodput counts the ones inside every objective: 6 against 4 in the one-second example.
- **Cost** — per 1,000 requests of 3,000 in and 500 out, the exercise cards cost $1.125 and $22.50, and the long prompt is the larger line on both. Prices move. A GPU floor is a different shape.
- **Model selection workflow** — hard attributes remove a model before a score can save it. Soft attributes rank the survivors. Quality, latency, and cost are a Pareto front when no candidate wins all three. Build the use case whose outcome you can measure, and name the harm that easy metric misses. A private eval confirms the rank. A constraint moves between the two lists only on purpose.
- **Build versus buy** — application teams buy the checkpoint and build the product and the eval around it. Pretraining is a separate project. A finetune builds a behavior on weights you bought and does not replace a document that changes.
- **Open weights and licenses** — downloadable weights are not the OSI open-source AI definition from October 2024, which also wants data information and code. Data information describes the corpus. It is not a dump of every token. Apache 2.0 carries a patent grant. MIT does not. The Llama 3 community license has a 700 million monthly-active-user snapshot on April 18, 2024, a "Built with Meta Llama 3" notice, and a "Llama 3" name prefix on a distributed derivative. Mistral has shipped Apache 2.0, a non-production license, and a modified MIT revenue gate, depending on the checkpoint. Gemma ships under its own terms and a prohibited-use policy.
- **Self-hosting and model APIs** — privacy, lineage, and control favor weights you run, including on-device models such as Gemini Nano. Performance and new features often favor an API. Losing the key, the region, the use case, or the provider to a country restriction is an access failure, and it wants a second path you have already scored. API cost scales with tokens. GPU cost is a floor, so the crossover depends on utilization and on the peak, not the average alone.
- **Public benchmarks** — HELM is a matrix. Arena is a preference rating whose statistics stay in the previous topic. The Open LLM Leaderboard averaged a six-task mix, replaced it in June 2024 with a harder six that normalized some tasks above chance, and the maintainers retired it in March 2025. Read the model id, the harness, the date, and the metric.
- **Benchmark selection and aggregation** — a task earns a column by matching a criterion. On the worksheet the mean picks B at 71.33, the mean rank picks A at 1.667, and a floor of 50 removes A. The product then picks the column.
- **Data contamination** — a long n-gram overlap is the screen while the crawl is available. The GPT-3 training filter looked for 13-word overlaps and only partly removed them. A clean slice that matches the full set is not proof the overlap was harmless. A score that is an outlier on one benchmark, or a standard deviation that collapses where answers should still vary, is a hint to run the paraphrase check. Defend the clean slice when it drops. A public score without that check is a hypothesis.
- **Evaluate every component** — log retrieval, tool arguments, grounding, and the final task. A wrong refund amount can sit inside a resolved ticket. A correct answer on a retrieval miss does not clear a product that promised the document.
- **An evaluation guideline** — decisions a rater can make, an example of each level, and a business outcome you check by slicing the log. A rubric that does not move edits or reopens does not gate the launch.
- **Choosing evaluation methods** — programs take what they can mark, classifiers take safety, a calibrated judge takes the residue, and pairwise votes only rank candidates that still need a pass line.
- **Annotating evaluation data** — production traffic, an expert tail, a frozen set, and a rotating set. Neither set is training data. Detecting 70 percent versus 73 percent needs 3,551 independent examples per model on the unpooled Wald plan, or 3,554 when the significance term uses the pooled rate. A shared item set is a paired comparison. Cohen's kappa and the rating bootstrap stay in the previous topic.
- **Evaluating the evaluation** — signal, reliability, correlation with the business outcome, and cost. A metric that fails one of the four stays a diagnostic.
- **Iterate and version** — a score travels with the model id, the set hash, the guideline version, the judge, the harness, and the date. A rubric edit starts a new series. The versioned private eval is the launch gate.

## Example

The numbers that come up in a launch review are a streamed wait, a goodput, a per-thousand-request bill, a sample size, and an aggregate that disagrees with itself. The prices, the one-second serving window, and the worksheet scores are exercises. A launch replaces them with the current rate card and the benchmarks you selected on purpose.

```python
import math

Z_975 = 1.959963984540054
Z_80 = 0.841621233572914


def latency(ttft: float, tpot: float, tokens: int) -> float:
    return ttft + tpot * (tokens - 1)


def cost_per_thousand(input_tokens: int, output_tokens: int, input_rate: float, output_rate: float) -> float:
    per_request = input_tokens / 1_000_000 * input_rate + output_tokens / 1_000_000 * output_rate
    return per_request * 1_000


def examples_per_arm(baseline: float, target: float) -> int:
    variance = baseline * (1.0 - baseline) + target * (1.0 - target)
    z_sum = Z_975 + Z_80
    needed = z_sum * z_sum * variance / (target - baseline) ** 2
    return math.ceil(needed)


scores = {"A": (86, 90, 35), "B": (84, 60, 70), "C": (80, 75, 55)}
means = {name: sum(values) / 3 for name, values in scores.items()}
wait = latency(0.400, 0.020, 500)
print(f"{wait:.2f} {500 / wait:.2f}")
print(10, 6, f"{6 / 10:.2f}", 16, 4, f"{4 / 16:.2f}")
print(f"{cost_per_thousand(3_000, 500, 0.25, 0.75):.3f}")
print(f"{cost_per_thousand(3_000, 500, 5.00, 15.00):.3f}")
print(examples_per_arm(0.70, 0.73))
print(f"{means['A']:.2f} {means['B']:.2f} {min(scores['A']) < 50}")
# 10.38 48.17
# 10 6 0.60 16 4 0.25
# 1.125
# 22.500
# 3551
# 70.33 71.33 True
```

Five hundred tokens at a TTFT of 0.400 seconds and a TPOT of 0.020 seconds take 10.38 seconds, which is 48.17 tokens a second end to end against a 50 token-per-second decode. Over one second, finishing 10 requests with 6 inside the latency objectives is goodput 6, and finishing 16 with only 4 inside is goodput 4. One thousand RAG-shaped requests cost $1.125 on the small exercise card and $22.500 on the frontier one. Seeing a rise from 70 percent to 73 percent takes 3,551 examples in each independent arm. On the worksheet, A's mean of 70.33 loses to B's 71.33, and A's science score of 35 still fails a floor of 50. The drills price a GPU floor, a contaminated 0.86, a voice budget, an Amazon Rufus return table, a Japanese Slack AI interval, a Glean retrieval miss, and a Khanmigo session that a turn average flatters.

## Source Chapter

- **Book chapter**: Chapter 4
- **Title**: Evaluate AI Systems

## Book Outline

- Evaluation Criteria
  - Domain-Specific Capability
  - Generation Capability
    - Factual consistency
    - Safety
  - Instruction-Following Capability
    - Instruction-following criteria
    - Roleplaying
  - Cost and Latency
- Model Selection
  - Model Selection Workflow
  - Model Build Versus Buy
    - Open source, open weight, and model licenses
    - Open source models versus model APIs
  - Navigate Public Benchmarks
    - Benchmark selection and aggregation
    - Data contamination with public benchmarks
- Design Your Evaluation Pipeline
  - Step 1. Evaluate All Components in a System
  - Step 2. Create an Evaluation Guideline
    - Define evaluation criteria
    - Create scoring rubrics with examples
    - Tie evaluation metrics to business metrics
  - Step 3. Define Evaluation Methods and Data
    - Select evaluation methods
    - Annotate evaluation data
    - Evaluate your evaluation pipeline
    - Iterate
- Summary

## Status

- `concepts.md` is a study set of 21 cards: evaluation criteria, domain-specific capability, factual consistency, safety, instruction following, roleplaying, latency, cost, model selection workflow, build versus buy, open weights and licenses, self-hosting and model APIs, public benchmarks, benchmark selection and aggregation, data contamination, evaluate every component, an evaluation guideline, choosing evaluation methods, annotating evaluation data, evaluating the evaluation, and iterate and version.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: a streamed latency, a one-second goodput, exercise token prices, a two-proportion sample size, and a worksheet of benchmark scores. A launch replaces them with the provider's current rate card, the license on the pinned checkpoint, and labels from the queue you ship to.
- Metric definitions for exact checks, judges, Cohen's kappa, bootstrap intervals, and pairwise ratings stay in Evaluation Methodology. This topic cites them and does not re-derive them. Pass@k and the hallucination behavior stay in the earlier topics.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — which tasks get a model, and the latency, cost, and maintenance bar a selection has to meet.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — why a call is a sample, how domain models differ, and the decoding that can take a format constraint away from the model.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — how to score a sample once a criterion exists, including perplexity as a contamination smell and a model used as a judge.
- [Prompt Engineering](../05_Prompt_Engineering/) — the instruction a following eval measures, and the injection a roleplaying leak check detects.
- [RAG and Agents](../06_RAG_and_Agents/) — the retriever and the tools whose stages this pipeline scores separately from the final answer.
- [Finetuning](../07_Finetuning/) — the build-on-a-purchase path, which still needs the eval set kept out of the training data.
- [Inference Optimization](../09_Inference_Optimization/) — the serving work behind TTFT, TPOT, and throughput once a budget has disqualified a model.
