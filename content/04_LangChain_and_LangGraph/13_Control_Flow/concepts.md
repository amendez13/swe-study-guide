## Conditional edges

The single most useful primitive in LangGraph after the state schema. A conditional edge calls a **router function** on state and uses its return value to pick the next node.

```python
def route(state) -> str:
    if state["iteration"] >= 10:
        return "give_up"
    if state["messages"][-1].tool_calls:
        return "tools"
    return "finalize"

graph.add_conditional_edges(
    "agent",
    route,
    {"tools": "tools", "finalize": "finalize", "give_up": END},
)
```

The router takes state, returns a string key; the mapping translates that key into a destination node. The mapping is required — it's also the only place that surfaces typos at compile time.

Use them everywhere there's a decision: tool-use vs answer, retry vs give up, escalate vs continue.

## Loops

A loop in LangGraph is **a conditional edge that points backwards** to an earlier node. The classic ReAct loop is two nodes (`agent` and `tools`) with a regular edge from `tools → agent` and a conditional edge from `agent → (tools | END)`.

```python
graph.add_edge("tools", "agent")         # always loop back
graph.add_conditional_edges(
    "agent",
    lambda s: "tools" if s["messages"][-1].tool_calls else END,
    {"tools": "tools", END: END},
)
```

A graph cycle is normal in LangGraph — that's the whole point. Just make sure the loop has an exit condition that will eventually be true, or the graph won't terminate.

## Bounding loops with `recursion_limit`

Every `.invoke()` accepts a `recursion_limit` in its config — the maximum number of steps the graph will run before giving up. Default is 25; raise for long-running workflows, lower for cheap defensive caps.

```python
app.invoke(
    {"messages": [...]},
    config={"recursion_limit": 50},
)
```

When the limit is hit, LangGraph raises `GraphRecursionError`. Catch it at the call site and decide whether to surface to the user, log, or fall back to a smaller answer.

Pair with state-level counters when you need finer-grained budgeting (token budget, retry budget) — `recursion_limit` is the blunt instrument; state counters are the precise one.

## Parallel execution

Multiple regular edges leaving a single node fan out — the named nodes execute **concurrently** and their state updates merge via reducers when they all finish.

```python
graph.add_edge(START, "search_internal")
graph.add_edge(START, "search_web")          # parallel branches
graph.add_edge("search_internal", "synthesize")
graph.add_edge("search_web", "synthesize")    # converges here
```

LangGraph waits for **all** incoming edges to a node before running it (a "join"). If `search_internal` finishes in 1s and `search_web` in 3s, `synthesize` runs at 3s with both results in state.

This is the canonical pattern for "run N retrievers in parallel" or "ask three judges and aggregate" — much cheaper than serializing them, with no extra glue.

## `Send` and map-reduce

Fixed parallel branches are great when you know the branches at graph-design time. For **dynamic** parallelism — "for each chunk in this list, call the model" — use `Send`:

```python
from langgraph.types import Send

def fan_out(state) -> list[Send]:
    return [
        Send("analyze", {"chunk": chunk})
        for chunk in state["chunks"]
    ]

graph.add_conditional_edges("split", fan_out, ["analyze"])
graph.add_edge("analyze", "reduce")
```

Each `Send` is a node invocation with its own scoped state slice. The `analyze` node runs once per chunk in parallel; their outputs merge into the parent state via reducers.

This is the LangGraph equivalent of `map`: variable fan-out at runtime, single converging reduce step. Used for chunked summarization, parallel-grading agents, and the "run the same sub-agent over a list of items" pattern.

## Subgraphs

A compiled graph is a `Runnable`, so it can be used as a node inside another graph. Subgraphs encapsulate complex workflows behind a clean state-transition.

```python
research_app = research_graph.compile()       # has its own internal state

orchestrator = StateGraph(OuterState)
orchestrator.add_node("research", research_app)
orchestrator.add_node("draft", draft_node)
orchestrator.add_edge("research", "draft")
```

How state flows in and out depends on schema compatibility:

- If the outer and inner schemas share keys, LangGraph passes the relevant slice in and merges relevant updates out.
- For schemas that don't share keys, write a thin adapter node that translates between them.

Subgraphs are the right tool when one workflow gets too big to fit in one head. Three subgraphs of 5 nodes each beats one graph of 15 nodes.

## Static vs dynamic routing

Two ways to express "pick the next node":

- **Static edges** — `add_edge(a, b)` and `add_conditional_edges(a, router, mapping)`. Wired at graph-build time; visible in the compiled topology and in LangSmith trace diagrams.
- **Dynamic routing via `Send`** — fan-out decided at runtime; the destination is computed from state.

Prefer static when the structure is fixed. Reach for `Send` when the number or shape of branches depends on the input data. Mixing both in one graph is normal — static for known topology, dynamic for variable-cardinality fan-out.

## Implicit error edges

By default, an exception in a node propagates out of the graph and ends execution. Two options when you want graceful failure:

- **Try/except inside the node** — catch the exception, write an error to state, route to a recovery node via a conditional edge.
- **Tool-style error handling** — for tools specifically, `ToolNode` catches exceptions and surfaces them as `ToolMessage` content so the agent can react.

```python
def safe_search(state):
    try:
        results = search_api(state["query"])
        return {"results": results, "search_error": None}
    except Exception as e:
        return {"results": [], "search_error": str(e)}

def route(state):
    return "fallback" if state["search_error"] else "use_results"
```

Building error paths into the graph topology — instead of leaving exceptions to bubble — is what production agents need to survive transient failures.

## When the graph itself is the wrong shape

A graph with 20+ nodes and dozens of conditional edges is hard to read and hard to debug. Symptoms that the topology is wrong:

- **Many edges between the same two nodes** — refactor into a wrapper node that handles the cases.
- **Routers with branchy logic inside them** — split into separate router functions per decision point.
- **State keys used by only two adjacent nodes** — those nodes could probably be one node.
- **Repeating subgraph patterns** — extract a subgraph and reuse it.

The most readable LangGraph applications have ~5–10 nodes at the top level and use subgraphs for depth. If you're past that, the next refactor is probably more valuable than the next feature.
