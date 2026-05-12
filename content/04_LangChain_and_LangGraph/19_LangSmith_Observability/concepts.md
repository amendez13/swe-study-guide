## Why observability matters for LLM apps

A normal web service has predictable behavior — given the same input, it returns the same output, and bugs are reproducible. LLM applications don't: outputs vary by temperature, models update, prompts drift, retrieval changes shape, and the same question can produce subtly different answers each time.

The fundamentals of debugging are the same — see [Logging and Observability](../../01_FastAPI/13_Logging_and_Observability/) for the structured-logging foundation. What changes is that **every LLM call is potentially the source of the bug**, so you need observability that captures every prompt sent, every response received, and every tool call in between.

LangSmith is LangChain's purpose-built observability platform for this. You can run a LangChain/LangGraph app without it — but you'll spend more time debugging than building.

## Tracing — what gets captured

A **trace** is a hierarchical record of one application invocation:

- The top-level `Runnable` (your chain or graph)
- Every sub-`Runnable` it called, with timing
- For LLM calls: prompts, responses, token counts, model, temperature, latency
- For tool calls: arguments, output, errors
- For retrievers: query, retrieved documents, scores
- For each step: inputs, outputs, metadata, errors

Open a trace in the LangSmith UI and you see the whole call tree — click into any node to see exactly what was sent and what came back. This is the single most useful debugging tool in the ecosystem.

## Enabling tracing

Tracing is **opt-in via environment variables** — no code changes required:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...
export LANGSMITH_PROJECT=my-app           # logical grouping
```

With those set, every LangChain/LangGraph `invoke`/`stream` produces a trace in the LangSmith dashboard. Unset `LANGSMITH_TRACING` and tracing is off — no performance overhead, no data leaving your process.

For multiple environments, give each its own project (`my-app-dev`, `my-app-prod`) so production data isn't mixed with debugging noise.

## Tagging and naming runs

By default, runs appear with auto-generated names. Add `run_name` and `tags` via `with_config` or per-invocation config:

```python
result = chain.invoke(
    {"input": "..."},
    config={
        "run_name": "user_question",
        "tags": ["v2-prompt", "experiment-42"],
        "metadata": {"user_id": "user-42", "session": "abc"},
    },
)
```

Tags let you filter the trace list ("show me all `v2-prompt` runs"); metadata is structured per-run context you can group by. Use them to make searches fast — without good tagging, finding the one bad trace in 10,000 is an exercise in scrolling.

## Datasets

A **dataset** is a collection of (input, expected output) pairs you can run your application against. The two ways to build them:

- **From production traces** — find good or bad runs in the trace UI and promote them to a dataset with one click. This is the easy path; your eval set grows from real usage.
- **Hand-curated** — write canonical inputs and expected outputs for the cases you care about most.

```python
from langsmith import Client

client = Client()

dataset = client.create_dataset("my-eval-set")
client.create_examples(
    dataset_id=dataset.id,
    inputs=[{"question": "..."}],
    outputs=[{"expected": "..."}],
)
```

Once you have a dataset, you can run your application against it (an **experiment**) and grade the results. Without one, "did my prompt change improve things?" is a vibes question.

## Evaluators

An evaluator is a function that scores one input-output pair. Two flavors:

- **Deterministic** — code that compares the actual output to the expected output (exact match, regex, JSON schema validation, contains-keyword).
- **LLM-as-judge** — an LLM call that scores the output on a rubric ("Is this answer factually correct? 1-5.").

```python
def correctness(run, example):
    expected = example.outputs["expected"]
    actual = run.outputs["answer"]
    return {"score": 1.0 if expected.lower() in actual.lower() else 0.0}

def factuality_judge(run, example):
    # LLM-as-judge call
    verdict = judge_model.invoke(grading_prompt(run, example))
    return {"score": verdict.score, "comment": verdict.reasoning}
```

Use deterministic evaluators when the answer has a checkable structure (JSON shape, set of values, specific keyword). Use LLM-as-judge for qualitative properties (helpfulness, tone, faithfulness). Often both — deterministic for the "did it parse?" check, LLM-as-judge for "is it any good?"

## Experiments — variant comparison

An **experiment** runs your chain/graph against a dataset with one or more evaluators, producing scored results. Compare experiments to see whether a change helped or hurt.

```python
from langsmith.evaluation import evaluate

results = evaluate(
    my_chain,
    data="my-eval-set",
    evaluators=[correctness, factuality_judge],
    experiment_prefix="v2-prompt",
)
```

The UI shows side-by-side: every example, every variant's output, every evaluator's score. You see exactly which inputs regressed, which improved, and the aggregate quality delta.

This is the single most important thing LangSmith gives you that you couldn't easily build yourself: a controlled way to know whether a prompt or model change is actually an improvement.

## Production monitoring

Beyond debugging individual traces, LangSmith offers production-scale dashboards: latency p50/p95/p99, cost per request, error rate, evaluator scores over time. Alerts when something regresses.

The recipe: tag production runs with a versioned prompt/model identifier, ship one variant at a time, watch the dashboard for changes. If error rate jumps or eval scores fall, you have a fingerprint to revert to.

This is the same hygiene as any normal production service — just with LLM-specific metrics added (tokens, cost, evaluator scores) alongside the usual latency and error rate.

## Tracing without LangChain

LangSmith works as a standalone tracing API too — you can wrap arbitrary functions with `@traceable` to log them, even if they don't go through LangChain:

```python
from langsmith import traceable

@traceable(run_type="chain")
def my_custom_function(query: str) -> str:
    # Direct OpenAI SDK call, not via LangChain
    return openai_client.chat.completions.create(...)
```

Useful when only part of your stack is LangChain and you want unified observability. Less useful for greenfield apps where you'd use LangChain anyway.

## Cost discipline through tracing

Trace data includes token usage per LLM call, which aggregates to cost per trace. The LangSmith dashboard surfaces this as a sortable column.

The first few times you look at production cost, expect surprises: an agent loop that takes 12 iterations on 5% of queries, a retrieval chain that re-embeds the query when it shouldn't, a system prompt that duplicates 500 tokens on every call. These show up in traces; they don't show up in your bill until end of month.

Build the habit: when you ship a new chain or graph, open the LangSmith trace and verify it's making the calls you expect, in the order you expect, with the prompt sizes you expect.
