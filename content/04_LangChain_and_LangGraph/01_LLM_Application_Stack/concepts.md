## Why a framework at all

A real LLM application is never just a single call to a provider's API. You need **prompt management** (templates, versioning, few-shot examples), **output parsing** (text → typed values), **memory** (state across turns), **retrieval** (RAG over your own data), **tool use** (the LLM calling your code), **branching and loops** (agents, retries), and **observability** (tracing, evals, monitoring).

You can build all of this yourself on top of `openai`/`anthropic` SDKs. The argument for LangChain isn't "you can't do it without us" — it's that you'll write the same primitives anyway, and the framework's version is composable, swap-able across providers, and free of glue code you have to maintain.

## LangChain, LangGraph, and LangSmith

Three sibling libraries from the same vendor with distinct concerns:

- **LangChain** — the primitives library. Models, prompt templates, output parsers, retrievers, tools, memory, simple chains. The unit of composition is the `Runnable` interface.
- **LangGraph** — the orchestration layer. Stateful graphs with nodes, edges, and reducers; cyclic and branching workflows; agents; human-in-the-loop. Built for what chains can't express.
- **LangSmith** — the observability layer. Tracing every prompt and tool call, datasets, evaluators, production monitoring. Works whether you're using LangChain, LangGraph, or just the OpenAI SDK.

Most production apps use all three: LangChain primitives composed into LangGraph workflows, traced by LangSmith.

## The package split (v1+)

LangChain v1 reorganized the library into smaller, more stable packages instead of one monolithic install:

```bash
pip install langchain-core         # interfaces and base classes — almost no deps
pip install langchain              # the standard library built on -core
pip install langchain-community    # third-party integrations
pip install langchain-openai       # provider-specific (one per provider)
pip install langchain-anthropic
pip install langgraph              # the graph orchestration layer
pip install langsmith              # the observability client
```

Pin these coherently — a `langchain-core==0.4` with `langchain==0.2` is the kind of mismatch that produces baffling import errors. Most production projects pin all `langchain-*` packages to a known-good set.

## Python and JavaScript parity

LangChain ships first-class implementations in both Python (`langchain`) and JavaScript/TypeScript (`langchain` on npm). The mental model is identical: same primitives, same `Runnable` interface, same LangSmith integration.

Pick by your runtime: Python for ML/data-adjacent backends and the dominant ecosystem of providers; JavaScript for Edge/Cloudflare Workers, Next.js apps, or browser-side agents. The concepts in this study guide are written in Python but transfer.

## When LangChain isn't the answer

The framework's cost is a dependency surface and a learning curve. Skip it when:

- You make **one prompt call with a fixed template** — `openai.chat.completions.create(...)` is two lines.
- You need **a feature LangChain doesn't expose** — the provider SDKs always ship new capabilities first.
- You want **maximum control over batching and rate limiting** — LangChain's abstractions can get in the way.

Reach for LangChain when you have composition (prompt + model + parser), retrieval, tool calling, or memory. Reach for LangGraph when you have branching, loops, or human-in-the-loop. Don't adopt either because it's the default.

## The v0 → v1 transition

LangChain v1 (late 2024 / 2025) was a substantial reorganization with breaking changes from the v0.x line:

- The package split described above (was: one giant `langchain` package).
- LCEL became the standard composition mechanism (was: bespoke chain classes).
- `AgentExecutor` and the legacy agents got soft-deprecated in favor of LangGraph's `create_react_agent`.
- Pydantic v2 became the default model schema (was: a v1/v2 toggle).

If you're reading older tutorials, code with `from langchain.agents import AgentExecutor` and `chain.run(...)` is v0-shaped. v1-shaped code uses `langchain-core`, `Runnable`s composed with `|`, and LangGraph for anything stateful.

## Install and minimal app

The shortest path from zero to a working LangChain call:

```bash
pip install langchain langchain-openai
export OPENAI_API_KEY=sk-...
```

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You translate English to {language}."),
    ("user", "{text}"),
])
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | model | parser
print(chain.invoke({"language": "French", "text": "Hello, world!"}))
```

Four primitives, one pipe operator, one `invoke()` call. The same chain has `.batch()`, `.stream()`, and async variants for free.

## Where LangSmith fits at install time

LangSmith tracing is **opt-in via environment variables** — no code change required.

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...
export LANGSMITH_PROJECT=my-app    # logical grouping in the LangSmith UI
```

With those set, every LangChain or LangGraph `invoke()` produces a hierarchical trace in the LangSmith dashboard: prompts, model calls, tool calls, latencies, token usage, errors. Turn it off in tests by unsetting `LANGSMITH_TRACING` or pointing at a separate project so production data isn't polluted.

This is the cheapest observability win in the ecosystem and worth wiring up on day one.
