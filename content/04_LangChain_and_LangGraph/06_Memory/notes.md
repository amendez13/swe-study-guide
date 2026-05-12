# Memory

LLMs are stateless; "memory" is how you reinject prior turns into the prompt so the conversation can continue coherently. The art is picking the right strategy for the conversation length.

## Key Points

- **LLMs forget between calls** — each `.invoke()` gets only the messages you send.
- **Buffer memory** — send everything; only works for short conversations.
- **Window memory** — keep the last N turns via `trim_messages`; constant cost, loses old context.
- **Summary memory** — summarize older turns into one message; cheap, loses verbatim detail.
- **Vector-store memory** — embed and retrieve relevant turns; scales to thousands of turns.
- **LangGraph short-term memory** — graph state checkpointed under a `thread_id`; the canonical pattern.
- **LangGraph long-term memory** — `Store` abstraction for facts that persist across threads.
- **Choose by length** — under 10 turns: buffer. 10-50: window or summary. 50+: vector. Multi-session: long-term.
- **Test hygiene** — inject the memory store, reset between tests, use fresh thread IDs.

## Example

A LangGraph chatbot demonstrating both short-term memory (per-thread checkpointing) and long-term memory (cross-thread user profile):

```python
from typing_extensions import Annotated, TypedDict
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.store.memory import InMemoryStore

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class State(TypedDict):
    messages: Annotated[list, add_messages]      # short-term: appended per turn


def chat_node(state: State, *, store) -> dict:
    # Pull long-term profile out of the cross-thread store
    profile = store.get(
        namespace=("users", "alice"),
        key="preferences",
    )
    profile_text = "Unknown user." if profile is None else str(profile.value)

    response = model.invoke([
        SystemMessage(
            f"You are a helpful assistant. User profile: {profile_text}"
        ),
        *state["messages"],
    ])
    return {"messages": [response]}


# Build the graph
graph = StateGraph(State)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# Wire in short-term (per-thread) and long-term (cross-thread) stores
checkpointer = MemorySaver()
store = InMemoryStore()

# Seed Alice's profile in the long-term store
store.put(
    namespace=("users", "alice"),
    key="preferences",
    value={"language": "Python", "skill": "intermediate"},
)

app = graph.compile(checkpointer=checkpointer, store=store)


def chat(thread_id: str, text: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(text)]}, config=config)
    return result["messages"][-1].content


if __name__ == "__main__":
    # First session — thread A
    session_a = str(uuid4())
    print(chat(session_a, "Hi, what language should I use for a new web API?"))
    print(chat(session_a, "What did you suggest in your first message?"))
    #   ^ Sees the prior turn thanks to short-term memory under thread_id session_a

    # Second session — thread B, fresh conversation but same user
    session_b = str(uuid4())
    print(chat(session_b, "Hi again! Remember my preferences?"))
    #   ^ No short-term history, but long-term store still has Alice's profile
    #     so the system prompt still says "language: Python, skill: intermediate"
```

Two memory layers, two failure modes if you mix them up:

- Short-term memory is what makes "What did I just say?" work within one conversation.
- Long-term memory is what makes "What language do I prefer?" work across separate conversations.

For production, replace `MemorySaver()` with `PostgresSaver` and `InMemoryStore()` with `PostgresStore` so memory survives restarts and is shared across replicas. The graph code doesn't change.
