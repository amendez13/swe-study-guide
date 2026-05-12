## What "self-improving" means here

Self-improvement in this context is **within-task improvement**: the agent produces a draft, evaluates it, refines, and tries again — all in one execution. It's not online learning; the model weights don't change. The agent gets better at this task by criticizing its own output and incorporating the criticism.

This family of patterns wins when the first attempt is rarely the best attempt: open-ended generation (essays, code), multi-step reasoning, retrieval where the first set of chunks might be wrong. It's overkill when the first attempt is usually right — adding a critic doubles the cost without proportional quality gain.

## Reflection — generator + critic

The simplest self-improving pattern: two nodes alternating. A **generator** produces output; a **critic** reads it and writes a critique; the generator revises with the critique in mind.

```
generator → critic → generator → critic → … → final answer
```

Exit when the critic says "good enough" (or after N rounds, whichever comes first).

```python
def generate(state):
    response = model.invoke([
        SystemMessage("Write an essay."),
        *state["messages"],
    ])
    return {"messages": [response]}

def critique(state):
    response = model.invoke([
        SystemMessage(
            "Critique the previous essay. If it's good, say 'OK'. "
            "Otherwise, list specific changes the writer should make."
        ),
        *state["messages"],
    ])
    return {"messages": [response]}

def should_continue(state):
    if state["iteration"] >= 3:
        return END
    last = state["messages"][-1].content
    return END if "OK" in last[:10] else "generate"
```

Two LLM calls per round; cheap to add to an existing chain.

## Reflexion — reflection with structured memory

Reflexion (Shinn et al., 2023) extends reflection with **persistent memory of past mistakes**. Across multiple attempts at the same task, the agent records what went wrong and uses it as context for the next attempt.

The structure: an actor attempts the task → an evaluator scores the result → a self-reflection step produces structured criticism → the actor retries with the prior reflections injected into its prompt.

```python
class ReflexionState(TypedDict):
    task: str
    messages: Annotated[list, add_messages]
    reflections: Annotated[list[str], lambda a, b: (a or []) + (b or [])]
    score: int
```

Where reflection's memory is implicit in the conversation, Reflexion's memory is **explicit** — the `reflections` field — which makes it survive across distinct task attempts and is easier to inspect.

Used most famously for code generation (the agent writes code, runs tests, reflects on failures, rewrites) where there's a deterministic grader (test pass rate).

## ReAct — Reasoning + Acting

ReAct (covered in detail in [The ReAct Loop](../09_The_ReAct_Loop/)) is the foundational "self-improving" pattern: the model reasons about what to do, acts via a tool, observes the result, and reasons again. Each tool result is implicit feedback that shapes the next reasoning step.

It's not usually filed under "self-improvement" — it's filed under "agents" — but mechanically it's the same family: the model uses prior steps' outputs to inform later ones. Reflection and Reflexion add explicit **critique** steps on top of ReAct's implicit reasoning loop.

## Corrective RAG (CRAG)

A retrieval-specific self-improving pattern. The classic shape:

```
retrieve → grade relevance → (if poor: rewrite query, retrieve again) → generate
```

The grader is an LLM call that scores each retrieved chunk for relevance to the question. If the average relevance is below threshold, the agent rewrites the query (paraphrase, generalize, decompose) and retrieves again. If still poor after N tries, fall back to web search or "I don't know."

The win: retrieval failures (the index doesn't have what the user asked for, or the question is phrased badly) get caught before generation, instead of producing a confident-but-wrong answer.

## Self-RAG

Self-RAG (Asai et al., 2023) goes further: the model decides **whether to retrieve at all**, then critiques both the retrieval and the generation. It's trained to emit special tokens (`[Retrieve]`, `[Relevant]`, `[Supported]`, `[Useful]`) that gate each step.

In LangGraph, you implement the same shape without retraining the model: dedicated grading nodes (each an LLM call with a binary or scalar output) decide whether to retrieve, whether the retrieved chunks are relevant, whether the generation is supported by the sources, and whether the final answer is useful. Edges route based on the grades.

It's more nodes than CRAG; for small RAG apps, CRAG covers 80% of the value at 50% of the cost.

## Adaptive RAG

The next step up from CRAG/Self-RAG. The agent classifies the **type of question** first (factual lookup, complex reasoning, no-context-needed), then routes to a different retrieval strategy per type:

- Simple factual → single retrieve + generate
- Complex reasoning → multi-step decompose, retrieve per sub-question, synthesize
- General knowledge → skip retrieval entirely, answer directly

Adaptive RAG is where retrieval starts to look like a graph in its own right (covered in [Retrieval-Augmented Generation](../07_Retrieval-Augmented_Generation/)).

## Plan-and-Execute

A different flavor of self-improvement: the agent writes a **multi-step plan upfront**, then executes each step, replanning when reality diverges from the plan.

```
plan → execute step 1 → re-plan? → execute step 2 → re-plan? → … → final answer
```

Useful for long, well-decomposed tasks (write a research report, refactor a module). Costs more than ReAct because of the planning overhead. Worse than ReAct when the task is short or unpredictable — the plan becomes obsolete halfway through.

A useful rule of thumb: if the task has 5+ steps and the steps are roughly predictable upfront, Plan-and-Execute wins. Otherwise, ReAct.

## When self-improvement helps

Match the pattern to the failure mode:

| Failure | Pattern |
|---------|---------|
| Output is plausible but wrong | Reflection (have it critique itself) |
| Same wrong attempts across retries | Reflexion (persistent memory of failures) |
| Retrieval gives bad chunks | CRAG (grade + rewrite) |
| Different question types need different strategies | Adaptive RAG |
| Task is long and structured | Plan-and-Execute |
| Single tool call would suffice | Plain ReAct or a chain |

Reaching for a fancier pattern when the simpler one is failing for a different reason is the most common mistake. Diagnose the failure mode first.

## The cost of self-improvement

Every critique step is another LLM call. A 3-round reflection costs ~6× a single generation; full Self-RAG with 4 graders can be 10× or more. Concretely on `gpt-4o-mini`:

- Single chain: ~$0.0002, 500ms
- 3-round reflection: ~$0.0012, 3s
- Adaptive RAG with grading: ~$0.005, 8s

For batch jobs and high-volume APIs, this matters. Decide whether the quality lift justifies the cost via evals — measure quality before and after on a fixed dataset. If the difference is in the noise, stick with the simpler pattern.

## Implementation hygiene

Three things that separate hobby self-improving agents from production ones:

- **Bounded loops.** Always cap the number of refinement rounds. An agent that refines forever is a bigger problem than one that ships an OK answer after 3 tries.
- **Structured critiques.** Make the critic emit a Pydantic schema (`severity`, `category`, `suggested_fix`), not free-text prose. Easier to act on, easier to log, easier to evaluate.
- **Persisted reflection.** Use a checkpointer ([Persistence and Checkpointers](../14_Persistence_and_Checkpointers/)) so you can inspect every critique → revision step in LangSmith and learn which critiques actually improve outputs.
