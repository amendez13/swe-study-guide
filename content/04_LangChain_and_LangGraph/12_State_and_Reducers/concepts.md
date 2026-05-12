## State schema

The state schema is a `TypedDict` (or Pydantic model) that declares every key the graph reads or writes. It's the **type signature of the whole application** — and the most important design decision when building a graph.

```python
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]    # conversation
    iteration: int                              # safety cap
    sources: list[str]                          # accumulated citations
    final_answer: str | None                    # only set at the end
```

Two rules:

1. **Every node parameter and return value flows through this schema.** A node can only read keys the schema declares; updates to undeclared keys are silently dropped.
2. **Add keys deliberately.** A state schema with 15 keys is a sign the graph is doing too much — split into subgraphs (see [LangGraph Fundamentals](../11_LangGraph_Fundamentals/)).

## What "reducer" means in LangGraph

A reducer is a function `(current_value, new_value) → merged_value`. It controls how each node's partial update gets combined with the existing state.

The **default reducer is replacement** — `new` wins. For mutable collections (message lists, accumulating sets), replacement is almost always wrong: every node would clobber the previous one's work. That's what custom reducers fix.

```python
# Without a reducer (replace semantics):
state = {"messages": [HumanMessage("hi")]}
# node returns {"messages": [AIMessage("hello")]}
# resulting state: {"messages": [AIMessage("hello")]} — the HumanMessage is gone

# With add_messages reducer (append semantics):
# resulting state: {"messages": [HumanMessage("hi"), AIMessage("hello")]}
```

## `Annotated` for declaring reducers

Reducers are attached to a field via the `Annotated` type from `typing_extensions`:

```python
from operator import add
from typing_extensions import Annotated, TypedDict

class State(TypedDict):
    counter: Annotated[int, add]              # add together
    items: Annotated[list[str], operator.add]  # concatenate lists
    messages: Annotated[list, add_messages]    # append messages with id deduplication
```

The reducer function takes `(existing, update)` and returns the merged value. LangGraph applies it automatically whenever a node returns a value for that key.

Reducers must be **pure functions** — same inputs → same output, no side effects. They run during the graph's update pipeline and can be called multiple times.

## `add_messages` — the special-case reducer

The most-used reducer in the framework. It appends new messages to the existing list, but with two subtle behaviors:

- **ID-based deduplication** — if a new message has the same `id` as an existing one, it **replaces** instead of appending. Useful for human-in-the-loop edits where you're rewriting a prior message.
- **Handles raw dicts** — accepts `{"role": "user", "content": "..."}` and converts to typed `BaseMessage` instances.

```python
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Each node returns {"messages": [new_message]}
# add_messages appends — full transcript builds up turn by turn
```

For chat-shaped graphs, `add_messages` is what you want 95% of the time. Use a plain `list` (with default replace semantics) only when you genuinely want to overwrite the conversation each step — rare.

## Multiple schemas — input, output, internal

You can declare separate schemas for what the graph **accepts**, what it **returns**, and what it **carries internally**:

```python
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str
    sources: list[str]

class InternalState(InputState, OutputState):
    messages: Annotated[list, add_messages]
    iteration: int
    debug_trace: list[str]

graph = StateGraph(
    state_schema=InternalState,
    input_schema=InputState,
    output_schema=OutputState,
)
```

The caller sees only `InputState` going in and `OutputState` coming out. Internal scratch (iteration counter, debug breadcrumbs, intermediate messages) stays hidden. This is the same separation between request/response models and internal state that you'd use in a typed API.

## Custom reducers

Anything beyond the built-ins is just a function. Common patterns:

```python
def union(existing: set, new: set) -> set:
    return existing | new

def keep_last_n(n: int):
    def reducer(existing: list, new: list) -> list:
        return (existing + new)[-n:]
    return reducer

def max_value(existing: int, new: int) -> int:
    return max(existing, new)

class State(TypedDict):
    visited_urls: Annotated[set, union]
    recent_thoughts: Annotated[list, keep_last_n(5)]
    best_score: Annotated[int, max_value]
```

Use the smallest reducer that does the job — a complex reducer is a sign that two state fields are entangled and should be separated.

## State immutability

State updates are **never in-place**. A node receives a state snapshot, returns a dict of changes, and LangGraph constructs a new state with reducers applied. The node never mutates the state it received.

```python
# WRONG — mutates the state in place
def bad_node(state):
    state["messages"].append(new_message)    # silent corruption
    return state

# RIGHT — returns a partial update
def good_node(state):
    return {"messages": [new_message]}       # add_messages reducer appends
```

This is the rule that lets checkpointers work, lets time travel work, lets parallel branches work without races. Treat the state object as a frozen snapshot; never modify it.

## Reading state inside nodes

Nodes receive the **full current state** as their argument. Pull what you need:

```python
def agent_node(state: State) -> dict:
    messages = state["messages"]
    iteration = state.get("iteration", 0)

    if iteration >= 10:
        return {"final_answer": "[max iterations]"}

    response = model.invoke(messages)
    return {
        "messages": [response],
        "iteration": iteration + 1,
    }
```

Use `state.get("key", default)` for optional fields. With Pydantic state classes, you can use attribute access (`state.messages`) — both forms work.

## When state grows too big

State accumulates: messages, retrieved docs, tool results, debug traces. A long-running agent's state can balloon to MB-scale, which slows checkpointing and inflates LangSmith trace size.

Mitigations, in order of preference:

- **Don't store what you don't need.** Resist the urge to keep every intermediate result "just in case."
- **Use `trim_messages`** (see [Memory](../06_Memory/)) to cap message-list length.
- **Move bulk data out of state.** Store large blobs in a vector DB or object storage; keep references (IDs, URLs) in state.
- **Split into subgraphs.** The outer graph carries summary state; subgraphs carry their own working state that doesn't bubble up.

A clean state schema is a state schema you can fit in your head. If it's too big to remember, your graph is probably doing too much.
