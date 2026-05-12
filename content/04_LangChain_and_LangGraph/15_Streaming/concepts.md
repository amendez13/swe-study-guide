## What streams from a LangGraph application

A LangGraph `.stream()` call can emit three different kinds of events. Each consumer wants a different one:

- **State updates** — what changed in state after each node ran. Useful for progress UIs ("step 3 of 7: searching docs").
- **Full state values** — the entire state after each node ran. Useful for debugging and dashboards.
- **LLM tokens** — the partial AIMessage chunks as the model generates them. Useful for chat UIs streaming text to the user.

A naive `.invoke()` call returns the final state; you have to know which stream mode you want to get anything before that.

## `.stream()` and `.astream()`

The basic streaming API on any compiled graph. Pick the stream mode and iterate:

```python
for event in app.stream(input, config, stream_mode="updates"):
    print(event)
```

Sync vs async are interchangeable — `astream` for async event loops, `stream` for everything else. The async variant scales better when many concurrent streams are open (e.g., many simultaneous chat users).

## Stream mode: `"updates"`

The most common mode. Yields a `{node_name: state_diff}` dict each time a node finishes:

```python
for event in app.stream(input, stream_mode="updates"):
    # event = {"agent": {"messages": [AIMessage("...")]}}
    for node, update in event.items():
        print(f"{node} → {update}")
```

Each event tells you which node ran and what it changed. Perfect for a status feed ("Searching docs… Analyzing… Synthesizing…") or for an audit log.

The dict has exactly one key per event — the node that just finished. If multiple nodes ran in parallel, you get one event per node.

## Stream mode: `"values"`

Yields the entire state after each node, not just the diff:

```python
for event in app.stream(input, stream_mode="values"):
    # event = {"messages": [...], "iteration": 3, ...}
    last_message = event["messages"][-1]
```

More verbose than `"updates"` — same information, redundant across steps. Useful when downstream code wants the full state snapshot at each step (e.g., a debug viewer that renders state diagrams).

## Stream mode: `"messages"`

Yields **token chunks** from any LLM call inside the graph. This is what powers a chat UI that displays text as the model generates it:

```python
async for chunk, metadata in app.astream(input, stream_mode="messages"):
    if metadata["langgraph_node"] == "agent":      # only the user-facing node
        print(chunk.content, end="", flush=True)
```

`metadata["langgraph_node"]` tells you which node produced the chunk — useful when multiple nodes in the graph invoke LLMs and you only want to show the final answer's tokens to the user, not intermediate-step tokens.

## Multiple modes simultaneously

You can subscribe to multiple modes at once by passing a list. Each event is a `(mode, payload)` tuple:

```python
async for mode, payload in app.astream(
    input, stream_mode=["updates", "messages"]
):
    if mode == "updates":
        notify_progress(payload)
    elif mode == "messages":
        chunk, metadata = payload
        if metadata["langgraph_node"] == "agent":
            stream_to_user(chunk.content)
```

This is the production pattern for chat agents: stream tokens to the user for the visible response, and emit "step N: doing X" progress updates for any UI status bar.

## `astream_events` — fine-grained event stream

The most detailed observability primitive. Emits an event for every LangChain `Runnable` lifecycle moment: chain start/end, LLM start/stream/end, tool start/end, retriever start/end.

```python
async for event in app.astream_events(input, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        token = event["data"]["chunk"].content
        # ... stream token to UI ...
    elif kind == "on_tool_end":
        print(f"Tool {event['name']} returned: {event['data']['output']}")
```

Always pass `version="v2"` — the v1 schema is deprecated. Use `astream_events` when you need to wire fine-grained telemetry into a custom UI or observability system. For most chat UIs, `stream_mode="messages"` is enough.

## Streaming inside a graph node

The model invocation inside a node streams natively — LangGraph's `stream_mode="messages"` picks up the token chunks without any code change. But if you want to **forward** a stream out of a custom (non-model) node, you have to opt in:

```python
from langchain_core.runnables.config import get_stream_writer

def progress_node(state):
    writer = get_stream_writer()
    writer({"status": "starting"})
    # ... do work ...
    writer({"status": "halfway"})
    return {"some": "update"}
```

Then subscribe to `stream_mode="custom"` to receive these payloads. Useful for surfacing tool progress, sub-task counters, or partial intermediate results.

## Stream cancellation

Streams can be cancelled cleanly — break the iterator, or with async, raise `asyncio.CancelledError`. LangGraph stops the in-flight node at the next checkpoint and the partial state is preserved (so a HITL flow can pick up where it stopped).

In a web app: bind cancellation to the HTTP connection closing. When the user navigates away mid-response, you want to stop paying for tokens you'll never display.

## Choosing what to stream

A practical mapping:

| Use case | Mode |
|----------|------|
| Chat UI showing the final answer | `"messages"` filtered by final node |
| Status bar / progress feed | `"updates"` |
| Debug viewer showing state at each step | `"values"` |
| Custom telemetry pipeline | `astream_events(version="v2")` |
| Per-tool or per-node progress hooks | `"custom"` with `get_stream_writer` |
| Chat UI + progress in one consumer | `["updates", "messages"]` |

The mistake to avoid: streaming everything everywhere. Pick the minimal set of modes that the UI actually needs.
