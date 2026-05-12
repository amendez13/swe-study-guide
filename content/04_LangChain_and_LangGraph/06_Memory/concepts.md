## Why memory exists

LLMs are **stateless** between calls. A model has no recollection of a conversation across separate `.invoke()` calls — each call gets exactly the messages you send it.

What "memory" actually means in this ecosystem: a strategy for **what to include in the prompt** so the model can continue the conversation coherently. Every memory approach is a way of choosing which prior messages survive into the next call's context window.

This is why memory in LangChain/LangGraph isn't one feature; it's a family of trade-offs between fidelity, cost, and context-window pressure.

## Buffer memory — keep everything

The simplest strategy: send the entire transcript on every call. Easy to implement, easy to reason about, **doesn't scale**. After 20 turns of a conversation the prompt is huge, you're paying for every token of history on every call, and you'll eventually hit the model's context window.

```python
history = []

def chat(user_input: str) -> str:
    history.append(HumanMessage(user_input))
    reply = model.invoke(history)
    history.append(reply)
    return reply.content
```

Use for short conversations (under ~10 turns) and prototypes. Production needs one of the strategies below.

## Window memory — keep the last N

Truncate to the most recent N turns. Constant prompt size, predictable cost. Loses context older than the window.

```python
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    history,
    max_tokens=4000,
    strategy="last",
    token_counter=model,
    include_system=True,        # keep the system prompt even when trimming
    start_on="human",            # don't start the trimmed history with an AIMessage
)
```

`trim_messages` is the v1+ utility that replaces the legacy `ConversationBufferWindowMemory` class. Always `include_system=True` — the system prompt is rarely what you want to drop.

## Summary memory — keep a digest

When the conversation gets long, summarize older turns into a single message. Preserves gist; loses verbatim detail. Cheaper than buffer memory at the cost of a summarization call every N turns.

```python
def summarize_if_long(history: list, threshold: int = 20):
    if len(history) < threshold:
        return history
    older, recent = history[:-10], history[-10:]
    summary = summarizer.invoke(older).content
    return [SystemMessage(f"Conversation so far: {summary}")] + recent
```

The summarizer is itself a chain (prompt + model). The trade-off worth knowing: the more aggressive your summary, the more domain-specific details you lose. Tune by running evals on representative conversations.

## Vector-store memory — retrieve relevant turns

For very long conversations, embed each turn and store it in a vector database. At query time, retrieve the most relevant prior turns and inject them as context — like RAG, but the corpus is the user's own conversation history.

Scales to thousands of turns at the cost of two extra calls per request (embedding + retrieval) and a more complex setup. Worth it for long-running assistants where the conversation spans days or weeks.

## LangGraph short-term memory

In LangGraph, conversation history lives in the graph's **state** under a key like `messages`, and that state is checkpointed under a `thread_id`. "Short-term memory" = state within a single thread, persisted across invocations of the same graph.

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]

# ... build graph ...
app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "user-42"}}
app.invoke({"messages": [HumanMessage("Hi")]}, config=config)
app.invoke({"messages": [HumanMessage("What did I just say?")]}, config=config)
# Second call sees the first call's messages via the checkpointer
```

The `add_messages` reducer appends new messages to the existing list, so each `.invoke()` adds to the conversation rather than replacing it. Same `thread_id` = same conversation; different `thread_id` = fresh start.

## LangGraph long-term memory

Short-term memory is scoped to a thread; **long-term memory** is shared across threads. Useful for facts about a user that should persist when they start a new conversation — preferences, profile data, prior project context.

LangGraph exposes long-term memory through the `Store` abstraction:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Write
store.put(
    namespace=("users", "alice"),
    key="preferences",
    value={"language": "Python", "skill": "intermediate"},
)

# Read
profile = store.get(namespace=("users", "alice"), key="preferences")
```

Namespaces give you scoping (per-user, per-org, per-feature); keys identify individual records. `InMemoryStore` for dev; `PostgresStore` for production multi-instance deployments.

## Choosing a strategy

The right memory strategy depends on conversation length and what kind of recall you need:

| Conversation length | Strategy |
|--------------------|----------|
| Under ~10 turns | Buffer (just send everything) |
| 10–50 turns, ephemeral | Window with `trim_messages` |
| 10–50 turns, you need older context | Summary memory |
| 50+ turns, multi-session | Vector-store retrieval |
| Multi-session user facts | LangGraph long-term memory |

Don't reach for vector memory before you've tried summary; don't reach for summary before you've tried window. Complexity has costs — start simple.

## Memory and tests

Memory makes chains **stateful**, which makes them harder to test. Two rules:

1. **Make the memory store injectable.** Pass it in as a dependency rather than hardcoding `MemorySaver()` in the chain. Tests get an in-memory store; production gets Postgres.
2. **Reset between tests.** A leaked thread ID between tests is the same flake-source as a leaked DB row. Use a fresh `thread_id` per test (e.g., `str(uuid4())`).

The same rules apply for tools that the model uses through memory — make them fakeable, isolate them per test, never share state between tests.
