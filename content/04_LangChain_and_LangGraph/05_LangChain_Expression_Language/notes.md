# LangChain Expression Language (LCEL)

The composition layer that gives LangChain its shape. Once you internalize `Runnable` + `|`, most of the framework reduces to "pick the primitives, pipe them together."

## Key Points

- **`Runnable` interface** — every primitive implements `.invoke`, `.ainvoke`, `.batch`, `.abatch`, `.stream`, `.astream`, `.astream_events`.
- **`|` composes** — output of left becomes input of right; the composed object is itself a `Runnable`.
- **`RunnablePassthrough`** — forwards input unchanged; used to keep the original input alongside transformed branches.
- **`RunnableParallel`** — runs N runnables on the same input concurrently and returns a dict of results.
- **`RunnableLambda`** — wraps any callable as a `Runnable`; the bridge from custom Python into LCEL.
- **`RunnableBranch`** — simple conditional routing; reach for LangGraph when it gets non-trivial.
- **`bind` and `ConfigurableField`** — pre-fill or expose runtime parameters without duplicating the chain.
- **Async/batch/streaming come free** — any chain inherits every execution mode.
- **`.with_retry` / `.with_fallbacks` / `.with_config`** — wrap operational concerns at the chain boundary.
- **LCEL's edge** — linear and DAG composition; cycles, stateful branching, and HITL belong in LangGraph.

## Example

A document-analysis chain that demonstrates `RunnableParallel` (fan-out for summary + tags + sentiment), `RunnablePassthrough.assign` (keeping the original text available), `RunnableLambda` (a small post-processing step), and `.with_retry` (operational hardening).

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda, RunnableParallel, RunnablePassthrough,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# --- Sub-chains, each a Runnable ---
summary_chain = (
    ChatPromptTemplate.from_template("Summarize in one sentence: {text}")
    | model
    | StrOutputParser()
)


class Tags(BaseModel):
    tags: list[str] = Field(description="3-5 short topic tags")


tag_chain = (
    ChatPromptTemplate.from_template("Tag the topics in: {text}")
    | model.with_structured_output(Tags)
    | RunnableLambda(lambda r: r.tags)        # extract the list from the Pydantic model
)

sentiment_chain = (
    ChatPromptTemplate.from_template(
        "Reply only with one of: positive, neutral, negative. Text: {text}"
    )
    | model
    | StrOutputParser()
    | RunnableLambda(str.strip)                # lower-cost than another LLM call
)


# --- Composed pipeline ---
# 1. Fan out: run all three analyzers in parallel
analysis = RunnableParallel(
    summary=summary_chain,
    tags=tag_chain,
    sentiment=sentiment_chain,
)

# 2. Keep the original text alongside the analysis results
pipeline = (
    {"text": RunnablePassthrough()}              # input dict for the analyzers
    | RunnablePassthrough.assign(analysis=analysis)
).with_retry(stop_after_attempt=2)


if __name__ == "__main__":
    article = (
        "FastAPI 0.110 was released today with significant improvements to "
        "dependency injection performance and better async error handling."
    )
    result = pipeline.invoke(article)

    print("Original text:", result["text"][:50], "…")
    print("Summary:      ", result["analysis"]["summary"])
    print("Tags:         ", result["analysis"]["tags"])
    print("Sentiment:    ", result["analysis"]["sentiment"])
```

Behavior:

- The three sub-chains run concurrently inside `RunnableParallel`, so the wall-clock latency is roughly the slowest of the three (not their sum).
- `RunnablePassthrough.assign` keeps the original text in the output dict alongside the analysis results.
- `.with_retry` retries the entire pipeline on transient failures; failures + retries appear as separate spans in LangSmith.
- Switching to `await pipeline.ainvoke(article)` runs the same pipeline asynchronously.
- `pipeline.batch([article_a, article_b, article_c])` processes three articles in parallel.

That's the LCEL payoff: one chain definition, every execution mode.
