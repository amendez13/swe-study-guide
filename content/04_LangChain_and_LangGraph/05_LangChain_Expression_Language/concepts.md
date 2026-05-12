## The `Runnable` interface

LCEL is built on one abstraction: the `Runnable`. Every LangChain primitive — chat models, prompt templates, output parsers, retrievers, tools, functions — implements it. Once you have a `Runnable`, you have these methods for free:

- `.invoke(input)` — sync, one input
- `.ainvoke(input)` — async, one input
- `.batch([input1, input2])` — sync, parallel
- `.abatch([input1, input2])` — async, parallel
- `.stream(input)` — sync, token-by-token
- `.astream(input)` — async, token-by-token
- `.astream_events(input)` — fine-grained event stream

You don't write concurrency or streaming code. The framework gives them to you because everything speaks the same interface.

## Composition with `|`

The pipe operator chains runnables: the output of the left side becomes the input of the right.

```python
chain = prompt | model | parser
```

It's `chain.invoke(...)`-ing in left-to-right order: `prompt.invoke(input) → model.invoke(prompt_output) → parser.invoke(model_output)`. Type matching is your responsibility — `prompt` produces a `PromptValue`, which `model` accepts; `model` produces an `AIMessage`, which `StrOutputParser` accepts.

The composed object is itself a `Runnable`, so chains are composable to any depth.

## `RunnablePassthrough`

Forwards its input downstream unchanged. Useful when you need a parallel branch to receive the original input as well as a transformed version:

```python
from langchain_core.runnables import RunnablePassthrough

chain = {
    "context": retriever,
    "question": RunnablePassthrough(),
} | prompt | model | parser
```

Here `retriever` consumes the question and produces context; `RunnablePassthrough()` keeps the original question available so the prompt template can reference both `{context}` and `{question}`.

`RunnablePassthrough.assign(key=runnable)` extends the dict: it keeps existing keys and adds a new one computed by `runnable`.

## `RunnableParallel`

Runs multiple runnables on the same input and returns a dict of their outputs.

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
    sentiment=sentiment_chain,
)

result: dict = parallel.invoke("Some long article text…")
# {"summary": "...", "keywords": [...], "sentiment": "positive"}
```

The three sub-chains execute concurrently. This is the canonical pattern for fan-out: do N independent things on one input, gather all the results.

The dict-literal syntax in the previous concept (`{"context": retriever, "question": RunnablePassthrough()}`) is sugar for `RunnableParallel(...)`; both forms work.

## `RunnableLambda`

Wraps any plain Python callable as a `Runnable`. Use it to inject custom logic into a chain.

```python
from langchain_core.runnables import RunnableLambda

def uppercase(text: str) -> str:
    return text.upper()

chain = prompt | model | StrOutputParser() | RunnableLambda(uppercase)
```

The callable can be sync or async; LCEL handles both. Most chains have at least one `RunnableLambda` for the small data transformation between primitives.

## `RunnableBranch`

Conditional routing without LangGraph — pick a sub-chain based on a predicate.

```python
from langchain_core.runnables import RunnableBranch

routed = RunnableBranch(
    (lambda x: "math" in x["question"].lower(), math_chain),
    (lambda x: "code" in x["question"].lower(), code_chain),
    default_chain,
)

routed.invoke({"question": "What's 2+2?"})  # → math_chain
```

Each entry is `(predicate, runnable)`; the first matching predicate wins. The last argument is the default. For anything more complex than a couple of branches, reach for LangGraph instead — `RunnableBranch` is a convenience, not a replacement for stateful routing.

## `bind` and configurable runtime parameters

`Runnable.bind(**kwargs)` pre-fills constructor-like parameters at invoke time. Most often used to switch a model's `stop`, `temperature`, or attached tools per chain.

```python
chain = prompt | model.bind(stop=["\n"]) | StrOutputParser()
```

For fields the user may set at invoke time, declare them `Configurable`:

```python
from langchain_core.runnables import ConfigurableField

model = ChatOpenAI(model="gpt-4o-mini").configurable_fields(
    temperature=ConfigurableField(id="temperature"),
)

chain.invoke(input, config={"configurable": {"temperature": 0.9}})
```

Useful for serving the same chain at multiple temperatures, models, or prompt variants without duplicating the chain definition.

## Async, batch, and streaming for free

Because every primitive implements all the methods of `Runnable`, any chain you compose has them too. You write `prompt | model | parser` once; the framework handles:

- `await chain.ainvoke(...)` — uses async drivers when present, threadpool otherwise.
- `chain.batch([...])` — parallelizes across inputs with a configurable concurrency cap.
- `chain.stream(...)` — propagates streaming through every stage that supports it (model streaming flows through `StrOutputParser`; structured-output parsers buffer until complete).
- `chain.astream_events(version="v2")` — emits granular `on_chain_start`, `on_llm_stream`, `on_tool_end` events for observability and UI updates.

This is the payoff for the `Runnable` abstraction: a simple chain definition expands into every execution mode without extra code.

## `.with_retry`, `.with_fallbacks`, `.with_config`

Operational behaviors as decorators on the chain itself:

```python
robust = (prompt | model | parser).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

resilient = primary_chain.with_fallbacks([cheaper_chain, local_chain])

tagged = chain.with_config({"tags": ["v2", "experiment-42"], "run_name": "extract"})
```

Retries, fallbacks, and runtime config flow into LangSmith traces so failures are visible. Wrap once at the chain boundary instead of every call site.

## When LCEL stops being enough

LCEL is great for linear-and-DAG composition: prompt → model → parser, with fan-out and fan-in. It is **not** great when you need cycles, branching that depends on accumulated state, or human-in-the-loop pauses.

The moment you reach for `while`, `if-then-else` over mutable state, or "let me re-run this with the result of the last attempt," you've outgrown LCEL. That's what LangGraph is for — see [LangGraph Fundamentals](../11_LangGraph_Fundamentals/). The two compose: a LangGraph node is just a `Runnable`, and a LangGraph itself is a `Runnable` you can drop into an LCEL chain.
