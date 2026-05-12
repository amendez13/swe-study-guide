# Control Flow

How LangGraph expresses branching, looping, parallelism, and dynamic fan-out. The state schema tells you what data flows; control flow tells you which nodes run when.

## Key Points

- **Conditional edges** — `(router_fn, mapping)`; the workhorse for any decision in a graph.
- **Loops** — conditional edge pointing back to an earlier node; classic ReAct shape.
- **`recursion_limit`** — graph-level safety cap; hits raise `GraphRecursionError`.
- **Parallel execution** — multiple edges out of a node fan out; LangGraph joins before the downstream node runs.
- **`Send`** — dynamic fan-out at runtime; the framework's `map` primitive.
- **Subgraphs** — compiled graphs are `Runnable`s; nest them as nodes.
- **Static vs dynamic routing** — static for known topology, `Send` for variable-cardinality fan-out; mix as needed.
- **Implicit error edges** — exceptions end the graph by default; build explicit error paths into the topology for resilience.
- **Refactor signals** — many edges between two nodes, branchy routers, repeating patterns → extract subgraphs.

## Example

A research graph that uses **all five control-flow primitives**: a conditional edge for routing, a loop for retries, parallel fan-out for multi-source search, `Send` for per-document analysis, and a recovery edge on failure.

```python
import random
from typing_extensions import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


# --- State ---
def union(a: set, b: set) -> set:
    return (a or set()) | (b or set())


class State(TypedDict):
    query: str
    retries: int
    docs: Annotated[set[str], union]
    summaries: Annotated[list[str], lambda a, b: (a or []) + (b or [])]
    error: str | None
    final: str | None


# --- Nodes ---
def search_internal(state: State) -> dict:
    # Pretend to find some docs
    return {"docs": {"doc://policy", "doc://faq"}}


def search_web(state: State) -> dict:
    # 30% chance of transient failure to demonstrate the retry loop
    if random.random() < 0.3 and state["retries"] < 2:
        return {"error": "rate limited"}
    return {"docs": {"https://example.com/article-1", "https://example.com/article-2"}}


def gate(state: State) -> str:
    """Conditional edge — retry the web search or move on."""
    if state.get("error") and state["retries"] < 3:
        return "retry"
    if state.get("error"):
        return "fail"
    return "proceed"


def bump_retry(state: State) -> dict:
    return {"retries": state["retries"] + 1, "error": None}


def fan_out(state: State) -> list[Send]:
    """Dynamic Send — one analyze node per doc."""
    return [Send("analyze", {"doc": doc}) for doc in sorted(state["docs"])]


def analyze(state: dict) -> dict:
    """Sees only the slice that fan_out sent: {'doc': ...}."""
    return {"summaries": [f"Summary of {state['doc']}"]}


def synthesize(state: State) -> dict:
    return {"final": f"Combined {len(state['summaries'])} summaries."}


def fail(state: State) -> dict:
    return {"final": f"Gave up after {state['retries']} retries: {state['error']}"}


# --- Graph ---
graph = StateGraph(State)

# Parallel fan-out at the start
graph.add_node("search_internal", search_internal)
graph.add_node("search_web", search_web)
graph.add_edge(START, "search_internal")
graph.add_edge(START, "search_web")

# Conditional gate after web search
graph.add_node("bump_retry", bump_retry)
graph.add_node("fail", fail)
graph.add_conditional_edges(
    "search_web",
    gate,
    {"retry": "bump_retry", "fail": "fail", "proceed": "fan_out_marker"},
)
graph.add_edge("bump_retry", "search_web")    # loop back

# Static placeholder node that triggers the dynamic Send
graph.add_node("fan_out_marker", lambda s: {})

# Both branches must converge before fan_out can dispatch
graph.add_edge("search_internal", "fan_out_marker")

# Dynamic fan-out: one `analyze` per doc
graph.add_node("analyze", analyze)
graph.add_conditional_edges("fan_out_marker", fan_out, ["analyze"])

# Reduce
graph.add_node("synthesize", synthesize)
graph.add_edge("analyze", "synthesize")
graph.add_edge("synthesize", END)
graph.add_edge("fail", END)

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke(
        {"query": "refund policy", "retries": 0, "docs": set(), "summaries": []},
        config={"recursion_limit": 25},
    )
    print(result["final"])
```

What's worth noticing:

- **Parallel fan-out at `START`** — both searches run concurrently; the join happens at `fan_out_marker`.
- **Conditional retry loop** — `gate` decides between `retry → bump_retry → search_web` (loop) and `proceed`. Bounded by `state["retries"] < 3`.
- **Dynamic `Send` fan-out** — `analyze` runs once per document, in parallel, with each invocation seeing only its slice of state.
- **Graceful failure path** — `fail` is a real node with an edge to `END`, not an uncaught exception. The user always gets a typed `final` value.
- **`recursion_limit=25`** — safety net against accidentally-infinite loops; the graph as designed needs ~10 steps for the worst case.

Most production graphs are some combination of these five primitives. The skill is recognizing which one each control-flow need maps to — and resisting the temptation to invent a sixth.
