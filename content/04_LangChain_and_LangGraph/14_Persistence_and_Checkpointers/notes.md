# Persistence and Checkpointers

How LangGraph applications survive restarts, continue across calls, and let you debug by rewinding. Persistence is what turns a one-shot graph into a stateful service.

## Key Points

- **Why persistence** — multi-turn conversations, long-running workflows, human-in-the-loop, time travel.
- **Checkpointer** — pluggable storage; writes state after every step, keyed by thread + checkpoint ID.
- **`MemorySaver`** — dev only; lost on restart.
- **`SqliteSaver`** — single-process production; survives restarts; doesn't scale to multiple replicas.
- **`PostgresSaver`** — multi-replica production; ACID, async variant available.
- **`thread_id`** — groups checkpoints into a logical conversation; same ID = same memory.
- **`get_state()`** — inspect current state without running the graph.
- **History and time travel** — `get_state_history()` returns every step; resume from any snapshot.
- **Resuming interrupts** — `app.invoke(None, config=...)` continues from a paused thread.
- **No built-in TTL** — checkpoints accumulate; prune at the application layer.

## Example

A persistent multi-turn chatbot using `SqliteSaver`, with a debug helper that walks the thread's history and demonstrates time-travel resumption:

```python
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def chat_node(state: State) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)


def build_app(db_path: str = "chats.db"):
    checkpointer = SqliteSaver.from_conn_string(db_path)
    return graph.compile(checkpointer=checkpointer), checkpointer


def chat(app, thread_id: str, text: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(text)]}, config=config)
    return result["messages"][-1].content


def print_history(app, thread_id: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    for snapshot in app.get_state_history(config):
        step = snapshot.metadata.get("step")
        next_nodes = snapshot.next or ["(done)"]
        msg_count = len(snapshot.values.get("messages", []))
        print(f"  step {step:>2}: next={next_nodes!s:<20} messages={msg_count}")


def time_travel_demo(app, thread_id: str) -> None:
    """Rewind to step 1 and re-run with a different question."""
    config = {"configurable": {"thread_id": thread_id}}
    history = list(app.get_state_history(config))
    # history[0] is the latest; pick an earlier one
    early = next(s for s in history if s.metadata["step"] == 1)

    # Resume from that checkpoint with a new user message
    app.invoke(
        {"messages": [HumanMessage("Wait, what's a class instead?")]},
        config=early.config,
    )


if __name__ == "__main__":
    app, _cp = build_app()

    # Session 1 — chat
    thread = "demo-thread-1"
    print(chat(app, thread, "Hi, can you explain Python decorators?"))
    print(chat(app, thread, "Can you show a small example?"))
    print(chat(app, thread, "Thanks. What did I ask first?"))
    # ^ Sees the prior turns; SqliteSaver gives us cross-call memory

    # Inspect the thread's history
    print("\nHistory:")
    print_history(app, thread)

    # Rewind and branch the conversation
    time_travel_demo(app, thread)
    print("\nHistory after time travel:")
    print_history(app, thread)

    # Simulate a process restart — fresh app instance, same DB file
    print("\nAfter 'restart':")
    app2, _cp2 = build_app()
    print(chat(app2, thread, "Are you still there?"))
    # ^ Still has the conversation history; the checkpointer survived restart
```

What's worth noticing:

- **`SqliteSaver` survives restart.** The second `build_app()` reuses the same DB file and continues the thread without state loss.
- **`thread_id` is the memory key.** Two different IDs = two independent conversations. One ID across days = one ongoing memory.
- **`get_state_history()` returns every step.** This is what powers debugging (which checkpoint had what data?) and time travel.
- **Time travel branches the thread.** Resuming from step 1 with new input doesn't erase steps 2-N — it creates a new branch in the checkpoint tree. You can still inspect the original.
- **Production change is one line.** Swap `SqliteSaver.from_conn_string("chats.db")` for `PostgresSaver.from_conn_string(DATABASE_URL)` and you're multi-replica capable. The application code is identical.
