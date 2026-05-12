# LLM Application Stack

The shape of a serious LLM application — what pieces it has, which library provides which, and how to wire them up so the moving parts stay composable.

## Key Points

- **Why a framework** — real apps need prompts + parsing + memory + retrieval + tools + branching + observability; you can build it yourself, or use primitives that already compose cleanly.
- **Three sibling libraries** — LangChain (primitives), LangGraph (stateful orchestration), LangSmith (observability). Most production apps use all three.
- **Package split (v1+)** — `langchain-core`, `langchain`, `langchain-community`, provider packages (`langchain-openai`, etc.), `langgraph`, `langsmith`. Pin them coherently.
- **Python and JavaScript parity** — same primitives, same `Runnable` interface, pick by runtime.
- **When not to use LangChain** — single fixed-prompt calls and cutting-edge provider features are better served by the provider SDK directly.
- **v0 → v1 transition** — packages split, LCEL became standard, legacy `AgentExecutor` superseded by LangGraph. Older tutorials are often v0-shaped.
- **Minimal app** — `prompt | model | parser` composed with the `|` operator gives you `.invoke()`, `.batch()`, `.stream()`, and async variants for free.
- **LangSmith is opt-in via env vars** — `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` enables tracing without code changes.

## Example

A complete, runnable minimal LangChain app that exercises every concept in this topic: typed messages, a prompt template, a chat model, an output parser, LCEL composition, and opt-in LangSmith tracing.

```python
# requirements.txt
# langchain==0.3.*
# langchain-openai==0.2.*
# langsmith==0.1.*

import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Observability is opt-in via env vars. Set these (or skip them) before importing.
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = "lsv2_..."
# os.environ["LANGSMITH_PROJECT"] = "intro-app"
# os.environ["OPENAI_API_KEY"] = "sk-..."


# 1. Prompt template — variables get filled at invoke time
prompt = ChatPromptTemplate.from_messages([
    ("system", "You translate English to {language}."),
    ("user", "{text}"),
])

# 2. Chat model — provider-specific, but exposes the common BaseChatModel interface
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. Output parser — coerce the model's AIMessage to a plain string
parser = StrOutputParser()

# 4. LCEL composition — every primitive is a Runnable, so | works
chain = prompt | model | parser


def main() -> None:
    # Sync invocation
    print(chain.invoke({"language": "French", "text": "Hello, world!"}))

    # Batch — built in for free
    outputs = chain.batch([
        {"language": "Spanish", "text": "Good morning!"},
        {"language": "Japanese", "text": "Where is the train station?"},
    ])
    for out in outputs:
        print(out)

    # Streaming — token by token
    for chunk in chain.stream({"language": "German", "text": "Goodnight."}):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
```

Four primitives, one pipe operator, three execution modes (`invoke`, `batch`, `stream`) — all without writing any concurrency or streaming plumbing. Add `LANGSMITH_TRACING=true` to the environment and every call shows up as a hierarchical trace in the LangSmith dashboard with no code change.

That's the smallest realistic LangChain app, and everything else in this study guide builds on it.
