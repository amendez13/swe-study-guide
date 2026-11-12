# AI Engineering Architecture and User Feedback

This topic is the production path around a foundation model, and the feedback that path collects once people use it. Context, guardrails, a router, a gateway, response caches, and a routed agent are added when a measured failure needs them. Metrics, traces, and drift detection say whether the path you shipped is the one that ran. Feedback is a separate loop: explicit and implicit signals, the biases in them, and the flywheel that may turn a checked signal into the next prompt or model. Retrieval, attacks, judges, the KV prefix cache, and the training file stay in the earlier topics. The figures below cite those results and do not recompute them.

## Key Points

- **The incremental architecture** — context, guardrails, router, gateway, response cache, and a routed agent, with a log line from the first production call. The KV prefix cache stays in Inference Optimization.
- **Enhance context** — put this request's facts in the prompt before you add machinery. At the shared $0.50 per million input price, a 1,200-token page is $600 per million calls, half of the 2,400-token prefix's $1,200 because it is half the tokens.
- **Input guardrails** — Presidio can replace, mask, or hash a private span. Llama Guard and OpenAI's Moderation API score hazards and are not injection detectors. Prompt Guard, NeMo Guardrails, and Azure Prompt Shields target jailbreaks and injections. A draft can redact and continue. A tool call blocks. Prompt Guard 2's 512-token window stays on the system-level defenses card.
- **Output guardrails** — a parser for format, a substring citation for a policy quote, a harm classifier, and one retry. Guardrails AI can reask. The cap of one is this architecture's policy. The failed draft is untrusted if you feed it back.
- **Guardrail implementation** — parallel checks take the max. Under the exercise 0.820 second first-token budget, parallel input checks land at 0.770 and sequential checks at 0.850. Output checks add 0.180 seconds, not 0.225. A 60-token draft held for the output guard is not visible until 2.425 seconds.
- **Streaming and a guardrail** — a flushed token cannot be unsaid. Buffer a message the company will send. Copilot ghost text may stream because acceptance is a later decision. The card-number drill is a different clock.
- **One retry and one fallback** — a guardrail retry, a router backup, and a gateway fallback are different second chances. One timeout plus one healthy fallback plus one healthy retry is 2.900 seconds, under a 3.000 second cap. Four timeouts are 8.000. That clock is a short call, not the 2.425 second draft.
- **The model router** — intent routing picks a pipeline. RouteLLM, Ong and coauthors 2024, routes strong versus weak from preference data. Fit the prompt to the target model's context limit when the route changes. The 1 July 2024 LMSYS headline is the best reported routers on GPT-4 Turbo versus Mixtral 8x7B, not every router in the figures. The abstract's 2× claim is for certain cases. The exercise blend is $476.80, against $1,440.00 always-large and $64.00 always-small, a $963.20 saving that assumes the hard labels are right.
- **The model gateway** — one interface, a spend ledger, limits, and provider fallbacks. Load balancing picks a healthy instance. Routing picks the model. A tool gateway holds tool credentials outside the agent process. LiteLLM's proxy and Portkey issue virtual keys. Cloudflare AI Gateway and Kong's AI gateway log, limit, and cache on an edge or a proxy. Cloudflare can fall back on an error or a timeout. OpenRouter also routes. Four exercise caps of 100, 100, 150, and 150 sum to a 500-request provider limit.
- **Exact response caching** — hash the model, the template version, the prompt, the decoding settings, and the user when the answer is personal. A 12 percent exercise hit rate saves $40.80 of a $340.00 million-call bill. Every call pays the lookup and only a miss pays the model, so average latency moves from 0.900 seconds to 0.79400.
- **Semantic caching** — GPTCache can do this. Read the evaluator before you copy a threshold, because a distance and a cosine do not point the same way. At exercise cosine 0.92, 180,000 of one million queries hit, 7,200 are false, the gross saving is $207.00, and average latency falls from 0.850 to 0.7120 seconds. At 0.98 the saving is $69.00 and the false hits are 300. Bump a namespace when the corpus changes.
- **Prompt cache versus response cache** — a prefix cache still generates. The Prompt caching card prices that at $7,010 versus $2,402, with a 0.50 GiB prefix on Llama 3 8B. A response cache skips the call. The two bills use different exercise rates on purpose.
- **Agents and write actions** — the agent is one route. The six-step bill of $684.00 against $140.00 stays in RAG and Agents. Writes stay proposals: recomputed arguments, a person, an idempotency key. Tool output is untrusted.
- **Monitoring and observability** — a monitor pages a known line. A trace answers a question you did not graph. Schema and latency can be exhaustive. A judge or a human read is a spot check, and a person should still read a slice of production traffic every day. OpenTelemetry's GenAI names were still Development in November 2026. `gen_ai.system` and `gen_ai.provider.name` are two generations of one fact. Cached tokens sit inside the input count, and adding a cache-read or cache-write subset double-counts. Message bodies are Opt-In. LangSmith, Langfuse, and Arize Phoenix are the trace products.
- **Quality, latency, cost, and reliability** — offline eval plus online failure rates, the TTFT formula from Evaluate AI Systems, dollars per successful task. Plot those series next to a north star such as retention or resolved tickets per agent-hour. On eight exercise incidents, detection is 11.0 minutes, mitigation after the page is 32.5, and onset to recovery is 43.5. User rates need a denominator.
- **Logs and traces** — template version, model id, route, verdicts, passage ids, and not the raw card number. One exercise answer is 1,140 milliseconds. Retrieval plus the model are 94.74 percent of it, and the output guard is 3.51 percent.
- **Drift detection** — prompt or corpus, the model behind an API name, and the user mix. Exercise total variation between two intent mixes is 0.20. Read a daily sample of production traces. The metrics do not replace that read. Pin the model id. A green canary on the old mix is incomplete.
- **Pipeline orchestration** — start with one request function. Add Airflow or Prefect when the reindex or the nightly eval no longer fits that function. The request path can stay a function. LangChain, LlamaIndex, Haystack, and DSPy do not own the tool allow-list. DSPy's search bill stays on the prompt engineering tools card.
- **Explicit and implicit feedback** — ChatGPT's thumb and a side-by-side pick are explicit. Copilot acceptance per suggestion shown is implicit, and lines accepted are a different rate. Midjourney's four-image pick is deliberate. Isolating a cell is not the same control as a variation or a later upscale. Thumbs are not the traffic, and the $3,125.00 label budget stays in Dataset Engineering.
- **Natural language feedback** — a stop is ambiguous, a complaint has no target, sentiment words lie, and a correction is a training pair only if the replacement is better. "Are you sure?" and "show the sources" are trust failures. Slice them by intent, because a diverse dialogue is not one thumb rate.
- **Regenerate, edits, length, and deletion** — regenerate is a miss in a draft product and the product itself in Midjourney. Copilot cycles inline suggestions and Copilot Chat on GitHub can reload a response. Those are not the draft's rate. An edit that changes a fact is the useful pair. Length needs a completed-task split. Deletion is confounded with privacy.
- **When to collect feedback** — at the moment the person can judge the thing you will change. Ask when the model is unsure, calibrate at onboarding, and leave a way to finish the task when the model fails. A refund is confirmed before it runs. Sample the widget. Do not add a draft score to an outcome score.
- **How to collect feedback** — a quiet thumb, a reason only on the negative, or a pairwise pick with the side randomized and logged. A private thumb and a public heart are different signals. The 65.0 percent swap consistency is the judge probe in Evaluation Methodology, not a human click rate.
- **Feedback biases** — leniency, randomness, position, and a taste for length or agreement. More data makes a bias more precise. The raters are not the traffic.
- **A confidence interval on a thumb rate** — 336 of 480 exercise ratings is 0.70, and the 95 percent Wald interval is 0.6590 to 0.7410. A ±0.03 Wald margin at that rate needs 897 ratings. Wilson replaces Wald when the miss count is a handful. The annotation card's 3,551 per arm is power for a different comparison.
- **Online experiments** — two pinned variants, a sticky user or tenant, and one metric declared in advance. 897 ratings and 3,551 per arm size different questions. Do not peek. Writes stay on the arm the eval scored.
- **Degenerate feedback loops** — thumbs that reward agreement train agreement. Sharma and coauthors, ICLR 2024, found five assistants sycophantic across four free-form tasks, preference data that favors matching the user, and optimization that can trade away truth without every sycophancy measure moving together. Recommenders loop on what they chose to show.
- **What traces and feedback may keep** — ids and verdicts by default, prompt text only for a named purpose after redaction. A debug window and a training export are different stores. A thumb is not the prompt. A product delete does not clear your log or your training file until those stores are in the deletion path.
- **Feedback and the data flywheel** — redact, filter, write the file Dataset Engineering specifies, and pass an eval that file cannot touch. That loop is the data advantage on the AI product defensibility card. Checked edits and debiased comparisons may enter. Bare thumbs, deletions, and the eval set may not.

## Example

The planning numbers are the guardrail clocks, the router blend, the semantic-cache saving, and the thumb interval. Prices are the exercise rates of $0.50 per million input tokens and $2.00 per million output tokens, except the large model on the router, which is $4.00 and $16.00 in the same exercise. None of these are a rate card. The Wald quantile is the one the annotation card uses.

```python
import math


def bill(calls: float, input_tokens: int, output_tokens: int, input_rate: float, output_rate: float) -> float:
    return calls * input_tokens / 1_000_000 * input_rate + calls * output_tokens / 1_000_000 * output_rate


first_parallel = max(0.080, 0.120) + 0.650
first_sequential = (0.080 + 0.120) + 0.650
generation = 0.650 + 0.025 * (60 - 1)
buffered = max(0.080, 0.120) + generation + max(0.005, 0.040, 0.180)
routed = bill(70_000, 800, 120, 0.50, 2.00) + bill(30_000, 2_000, 400, 4.00, 16.00)
all_large = bill(100_000, 2_000, 400, 4.00, 16.00)
per_call = bill(1, 1_500, 200, 0.50, 2.00)
saved_semantic = 180_000 * per_call
average_s = 0.015 + 820_000 / 1_000_000 * 0.850
z = 1.959963984540054
rate = 336 / 480
margin = z * math.sqrt(rate * (1.0 - rate) / 480)
needed = math.ceil(rate * (1.0 - rate) / (0.03 / z) ** 2)
print(f"{first_parallel:.3f} {first_sequential:.3f} {buffered:.3f}")
print(f"{routed:.2f} {all_large - routed:.2f}")
print(f"{saved_semantic:.2f} {average_s:.4f}")
print(f"{rate:.2f} {rate - margin:.4f} {rate + margin:.4f} {needed}")
# 0.770 0.850 2.425
# 476.80 963.20
# 207.00 0.7120
# 0.70 0.6590 0.7410 897
```

Parallel guards put the first token at 0.770 seconds, inside an exercise budget the sequential path misses at 0.850. Buffering the 60-token draft for the output guard waits until 2.425 seconds. The router blend costs $476.80 and saves $963.20 against always using the large model, if the hard labels are right. Semantic neighbors at the looser exercise threshold save $207.00 gross and pull average latency to 0.7120 seconds, because every query pays the lookup and a miss also pays the model. False hits are included in that average. A week of 480 thumbs at a 0.70 rate supports 0.6590 to 0.7410, and 897 ratings are what a ±0.03 Wald margin needs. The drills use other numbers: a cross-account cache hit, a card number already on screen, a hard slice the router called easy, a provider outage, a thumb-down move the eval cannot see, a regenerate rate, a sycophancy canary, and a trace whose time is an unfiltered retry.

## Source Chapter

- **Book chapter**: Chapter 10
- **Title**: AI Engineering Architecture and User Feedback

## Book Outline

- AI Engineering Architecture
  - Step 1. Enhance Context
  - Step 2. Put in Guardrails
    - Input guardrails
    - Output guardrails
    - Guardrail implementation
  - Step 3. Add Model Router and Gateway
    - Router
    - Gateway
  - Step 4. Reduce Latency with Caches
    - Exact caching
    - Semantic caching
  - Step 5. Add Agent Patterns
  - Monitoring and Observability
    - Metrics
    - Logs and traces
    - Drift detection
  - AI Pipeline Orchestration
- User Feedback
  - Extracting Conversational Feedback
    - Natural language feedback
    - Other conversational feedback
  - Feedback Design
    - When to collect feedback
    - How to collect feedback
  - Feedback Limitations
    - Biases
    - Degenerate feedback loop
- Summary

## Status

- `concepts.md` is a study set of 29 cards: the incremental architecture, enhance context, input guardrails, output guardrails, guardrail implementation, streaming and a guardrail, one retry and one fallback, the model router, the model gateway, exact response caching, semantic caching, prompt cache versus response cache, agents and write actions, monitoring and observability, quality latency cost and reliability, logs and traces, drift detection, pipeline orchestration, explicit and implicit feedback, natural language feedback, regenerate edits length and deletion, when to collect feedback, how to collect feedback, feedback biases, a confidence interval on a thumb rate, online experiments, degenerate feedback loops, what traces and feedback may keep, and feedback and the data flywheel. The key points above are the chapter summary.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic at the exercise prices of $0.50 per million input tokens and $2.00 per million output tokens, with the router's large model at $4.00 and $16.00. Cache latency charges the lookup on every request and the model only on a miss. The prefix-cache bill of $7,010 versus $2,402, the 0.50 GiB Llama 3 8B prefix, the six-step agent bill of $684.00 versus $140.00, the $3,125.00 labeling budget, the 3,551-example power plan, and the judge's 65.0 percent swap consistency are cited from the earlier topics and not recomputed. RouteLLM's 1 July 2024 headline is that post's best reported routers on GPT-4 Turbo versus Mixtral 8x7B, and the paper's 2× claim is for certain cases. Sharma and coauthors' sycophancy findings are cited as that paper's results. OpenTelemetry's GenAI attribute rules are dated to the public docs checked in November 2026. A launch replaces every exercise rate, latency, and audit count with the trace and the eval you run.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — the three-layer stack, and maintenance under a model id that moves.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — structured outputs, the schema mask a format guardrail should not reinvent.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — AI-judge position and verbosity biases, and how pairwise votes become a rating.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — TTFT, TPOT, goodput, cost, factual consistency, and the 3,551-example power plan.
- [Prompt Engineering](../05_Prompt_Engineering/) — the prompt the model actually sees, prompt injection, and the system-level defenses an input guardrail sits beside.
- [RAG and Agents](../06_RAG_and_Agents/) — retrieval, the agent loop, write tools, and the $684.00 versus $140.00 exercise bill.
- [Finetuning](../07_Finetuning/) — the model-tier change, once a checked feedback file has earned one.
- [Dataset Engineering](../08_Dataset_Engineering/) — the training file, why thumbs are not the traffic, and model collapse if the flywheel trains on itself.
- [Inference Optimization](../09_Inference_Optimization/) — the KV prefix cache, its $7,010 versus $2,402 exercise bill, and the latency clocks under the call.
