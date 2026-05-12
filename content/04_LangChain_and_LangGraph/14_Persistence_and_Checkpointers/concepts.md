## Why persistence

Without persistence, a graph forgets everything between invocations. That's fine for a one-shot RAG query but fatal for:

- **Multi-turn conversations** — the graph needs to know what was said before.
- **Long-running workflows** — the graph might run for minutes; you need to survive process restarts.
- **Human-in-the-loop** — the graph pauses, a human reviews, the graph resumes; that "resume" requires the prior state.
- **Time travel and replay** — debug an agent by rewinding to a prior step and re-running.

Persistence in LangGraph means **saving the full state after every step**, keyed by a thread ID. Resume with the same thread and the graph continues from where it left off.

## Checkpointers

A checkpointer is a pluggable persistence layer with one job: read and write `Checkpoint` objects (full state snapshots + metadata) keyed by `(thread_id, checkpoint_id)`.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

Every step of the graph triggers a write. Every `.invoke()` (or `.get_state()`) triggers a read. The checkpointer is the entire durability story for LangGraph state.

## In-memory checkpointer

`MemorySaver` keeps checkpoints in a Python dict — easy to set up, gone on restart. Perfect for development, tests, and notebooks.

```python
from langgraph.checkpoint.memory import MemorySaver
app = graph.compile(checkpointer=MemorySaver())
```

Don't use it in production. The moment your process dies, every in-flight conversation is gone with no recovery path.

## SQLite checkpointer

`SqliteSaver` persists to a single SQLite file. Good for single-process production apps, demos that should survive restarts, and CLI tools.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = graph.compile(checkpointer=checkpointer)
```

Survives restarts; doesn't scale to multiple replicas (SQLite is single-writer). Use it when "one server" is the production architecture.

## Postgres checkpointer

`PostgresSaver` is the production default for any deployment with more than one replica:

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    checkpointer.setup()    # create the schema (run once)
    app = graph.compile(checkpointer=checkpointer)
```

Properties that make it production-worthy: ACID writes, concurrent multi-instance reads, point-in-time backups (via your DB's normal backup tooling), and it's a database you already operate.

Async variant: `AsyncPostgresSaver` for async graphs. Pair with `asyncpg` as the driver.

## Threads and `thread_id`

A **thread** groups all the checkpoints for one logical conversation or workflow. The `thread_id` is your identifier — typically a user ID, a session ID, or a task UUID.

```python
config = {"configurable": {"thread_id": "user-42-chat"}}

# First call — fresh thread
app.invoke({"messages": [HumanMessage("Hi")]}, config=config)

# Second call — same thread_id, continues the conversation
app.invoke({"messages": [HumanMessage("What did I just say?")]}, config=config)
```

Same `thread_id` = same memory. Different `thread_id` = independent conversation.

In a web app, a sensible scheme is `f"user:{user_id}:chat:{chat_id}"` so you can scope memory at the right grain and clean up later.

## Reading state with `get_state()`

You can inspect the current state of a thread without running the graph:

```python
snapshot = app.get_state(config={"configurable": {"thread_id": "user-42"}})

print(snapshot.values)          # the state dict
print(snapshot.next)             # which node(s) would run next
print(snapshot.config)           # the config used
print(snapshot.metadata)         # step number, source, parents
```

Useful for showing a "where is my task" status in a UI, for debugging stuck workflows, and for HITL flows where you display state to a human and wait for their decision.

## History and time travel

Checkpointers store every step, not just the latest. `get_state_history()` returns the full sequence:

```python
for snapshot in app.get_state_history(config):
    print(f"step {snapshot.metadata['step']}: next={snapshot.next}")
```

To rewind, get an old snapshot's config and use it as the resume point:

```python
old_snapshot = next(
    s for s in app.get_state_history(config)
    if s.metadata["step"] == 3
)

# Resume from step 3 — re-run from there
app.invoke(None, config=old_snapshot.config)

# Or rewrite state and resume
app.update_state(
    config=old_snapshot.config,
    values={"messages": [...]},
)
app.invoke(None, config=...)
```

This is what enables debugging interactively: rewind to where things went wrong, change state, see what the graph does differently. The same machinery powers human-in-the-loop "edit and resume" workflows.

## Resuming from interrupts

When a graph is paused at a breakpoint (covered in [Human-in-the-Loop](../16_Human-in-the-Loop/)), the checkpointer holds the paused state. Resume by calling `.invoke(None, config=...)` with the same thread:

```python
# First invoke — runs until the interrupt
app.invoke({"input": "x"}, config={"configurable": {"thread_id": "task-1"}})
# Graph is now paused. Human reviews state via get_state().

# Second invoke — resumes from where it paused
app.invoke(None, config={"configurable": {"thread_id": "task-1"}})
```

Passing `None` as the input is the convention for "continue from the saved state." Without a checkpointer, this can't work — there's nothing to resume from.

## Cleanup and TTL

Checkpoints accumulate. A long-running production app with many threads will grow the checkpointer table indefinitely unless you prune.

Strategies:

- **Application-level TTL** — periodic job that deletes threads older than N days.
- **Per-thread limits** — keep only the last N checkpoints per thread (the older ones are useful for time travel, but most apps don't need indefinite history).
- **Soft deletion** — flag instead of delete if you might need to recover.

There's no built-in TTL story; pick a policy and enforce it in operational code. Track checkpoint table size as a normal database metric so you notice when growth gets out of hand.
