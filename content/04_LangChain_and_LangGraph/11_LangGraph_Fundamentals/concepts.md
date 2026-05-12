## Why LangGraph

LCEL handles linear and DAG composition cleanly. It does not handle:

- **Cycles** — loops where the next step depends on the result of the previous, like a ReAct agent.
- **Branching on accumulated state** — "if we've retried 3 times, give up; otherwise try again."
- **Pausing and resuming** — human-in-the-loop, breakpoints, time travel.
- **Persistence per conversation** — checkpointing the whole workflow under a thread ID.

LangGraph is the orchestration layer for those cases. It models an application as a **graph of nodes that read and write a shared state object**, and gives you cycles, branching, persistence, and HITL as first-class features.

The mental shift: stop thinking about chains as "data flows through a pipeline" and start thinking about graphs as "nodes mutate state, edges decide what runs next."

## `StateGraph` and `MessageGraph`

The two main graph classes:

- **`StateGraph`** — works with arbitrary typed state (a `TypedDict` or Pydantic model). Use this in 99% of cases — it scales to any application shape.
- **`MessageGraph`** — a convenience shortcut for graphs whose entire state is a message list. Equivalent to `StateGraph` with `State = {messages: list[BaseMessage]}`. Cleaner for pure chatbots; outgrown the moment you need any non-message state.

```python
from typing_extensions import Annotated, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    iteration: int

graph = StateGraph(State)
```

The state schema is the entire contract for your graph. Every node receives the current state and returns updates; every edge inspects state to pick the next node.

## Nodes

A node is a function (or `Runnable`) from `State → State`. The signature is:

```python
def node(state: State) -> dict:
    return {"some_key": new_value}
```

The returned dict is merged into the existing state via the schema's reducers (covered in [State and Reducers](../12_State_and_Reducers/)). A node can return:

- A partial dict — updates only the keys that changed.
- An empty dict `{}` — no-op, but useful as a pass-through.
- `None` is equivalent to `{}`.

Async variants work too — `async def node(state) -> dict`.

```python
def call_model(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}     # add_messages appends this to existing messages

graph.add_node("agent", call_model)
```

Naming the node matters: it shows up in LangSmith traces and in conditional-edge routing.

## Edges

Edges connect nodes. Two kinds:

- **Regular edges** (`add_edge(from, to)`) — always traverse from `from` to `to` when `from` finishes.
- **Conditional edges** (`add_conditional_edges(from, router_fn, mapping)`) — call `router_fn(state)` after `from` finishes, use the returned key to pick the next node.

```python
graph.add_edge("agent", "tools")    # always: agent → tools

def route(state) -> str:
    return "tools" if state["messages"][-1].tool_calls else END

graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
```

The mapping in `add_conditional_edges` is required and is what wires the router's string return value to actual destination nodes.

## `START` and `END` sentinel nodes

Special markers that bookend the graph:

- **`START`** — entry point. Every graph has at least one `add_edge(START, "first_node")`.
- **`END`** — exit. Returning from `END` returns control to the caller of `.invoke()`.

```python
from langgraph.graph import START, END

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
```

You can have multiple edges into `START` (rare) or multiple edges to `END` (common — many exit conditions). What you can't have is a node that's unreachable from `START` or has no path to `END`; both are validation errors at compile time.

## Compiling the graph

`graph.compile()` validates the structure and returns a `Runnable` — the same `Runnable` interface as everything else in LangChain, so the compiled graph composes into LCEL chains, has `.invoke`/`.batch`/`.stream`/`.astream_events`, and works as a node inside another graph.

```python
app = graph.compile()

result = app.invoke({"messages": [HumanMessage("Hi")], "iteration": 0})
```

`compile()` also accepts:

- `checkpointer=...` — turn on persistence (see [Persistence and Checkpointers](../14_Persistence_and_Checkpointers/)).
- `interrupt_before=[...]`, `interrupt_after=[...]` — pause execution at named nodes for HITL.
- `debug=True` — log every state transition; useful for development.

## The two-node ReAct graph

The simplest non-trivial LangGraph, and the entire pattern underlying every agent in the framework:

```python
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

def call_model(state):
    return {"messages": [model.bind_tools(tools).invoke(state["messages"])]}

def route(state):
    return "tools" if state["messages"][-1].tool_calls else END

graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})

app = graph.compile()
```

That's `create_react_agent` from scratch in 10 lines. Understanding this graph means understanding what every LangGraph agent is doing under the hood.

## The mental model: state and transitions

Every LangGraph application boils down to two questions:

1. **What does the state look like?** Define the `TypedDict` / Pydantic schema. This is the contract.
2. **What transitions are allowed?** Add nodes (state transformations) and edges (which transition runs next).

If you're stuck designing a graph, draw it on paper. Boxes for nodes, arrows for edges, and a list of state keys on the side. A graph that's hard to draw is usually a graph that's wrong.

## Subgraphs and composition

A compiled graph is a `Runnable`, which means it can be a node inside another graph:

```python
research_app = research_graph.compile()
draft_app = draft_graph.compile()

orchestrator = StateGraph(OuterState)
orchestrator.add_node("research", research_app)
orchestrator.add_node("draft", draft_app)
orchestrator.add_edge("research", "draft")
```

The outer graph passes its state into the subgraph and merges the subgraph's output back in. This is how complex agents get built — each capability (research, draft, review) is its own self-contained graph, composed by an orchestrator. See [Multi-Agent Systems](../18_Multi-Agent_Systems/) for the full pattern.
