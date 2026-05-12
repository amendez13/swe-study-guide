# State and Reducers

The data contract behind every LangGraph application. Get the schema right and the graph almost designs itself; get it wrong and nothing else works.

## Key Points

- **State schema** — `TypedDict` or Pydantic model declaring every key the graph touches.
- **Reducer** — `(existing, new) → merged`; controls how each node's update combines with state.
- **Default reducer is replace** — fine for scalars, wrong for accumulating collections.
- **`Annotated[T, reducer]`** — attach a reducer to a field in the schema.
- **`add_messages`** — append messages, dedupe by ID, accept raw dicts. The 95% case for chat graphs.
- **Multiple schemas** — separate `input_schema` / `output_schema` from internal state to hide scratch data.
- **Custom reducers** — pure functions; common patterns are union, keep-last-N, max.
- **State is immutable** — never mutate the state argument; always return a partial dict.
- **Read state in nodes** — `state["key"]` or `state.get("key", default)`.
- **Keep state small** — store references to bulk data, not the data itself; split into subgraphs when growing.

## Example

A multi-source research graph that exercises three reducer flavors: `add_messages` (append), a custom set union (deduped citation tracking), and a custom max-keeper (best confidence score across parallel branches).

```python
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


# --- Reducers ---
def union(existing: set, new: set) -> set:
    """Set union — order-independent dedupe."""
    return (existing or set()) | (new or set())


def keep_max(existing: int, new: int) -> int:
    """Keep the maximum across all updates."""
    if existing is None:
        return new
    return max(existing, new)


# --- Schemas ---
class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    answer: str
    confidence: int                                  # 0-100
    sources: set[str]                                 # deduplicated URLs


class GraphState(InputState, OutputState):
    """Internal state — accumulating fields use reducers."""
    messages: Annotated[list, add_messages]          # append messages
    sources: Annotated[set[str], union]              # union across nodes
    confidence: Annotated[int, keep_max]             # max across parallel branches


# --- Nodes ---
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def search_internal(state: GraphState) -> dict:
    # Pretend we hit the internal docs and got URLs + a confidence score
    return {
        "messages": [AIMessage("Internal docs: found policy doc.")],
        "sources": {"intranet://policy-42"},
        "confidence": 60,
    }


def search_web(state: GraphState) -> dict:
    return {
        "messages": [AIMessage("Web search: found two articles.")],
        "sources": {"https://example.com/a", "https://example.com/b"},
        "confidence": 75,
    }


def synthesize(state: GraphState) -> dict:
    # state["messages"] contains both searches' outputs (appended via add_messages)
    # state["sources"] is the union of both source sets
    # state["confidence"] is the max of both individual scores
    return {
        "answer": f"Synthesized answer using {len(state['sources'])} sources.",
    }


# --- Graph (parallel fan-out, then synthesis) ---
graph = StateGraph(
    state_schema=GraphState,
    input_schema=InputState,
    output_schema=OutputState,
)
graph.add_node("internal", search_internal)
graph.add_node("web", search_web)
graph.add_node("synthesize", synthesize)

graph.add_edge(START, "internal")
graph.add_edge(START, "web")                          # parallel — both run
graph.add_edge("internal", "synthesize")
graph.add_edge("web", "synthesize")
graph.add_edge("synthesize", END)

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({"question": "What's the refund policy?"})
    print(f"Answer:     {result['answer']}")
    print(f"Confidence: {result['confidence']}")     # 75 — max of (60, 75)
    print(f"Sources:    {sorted(result['sources'])}")
    # Caller sees only the OutputState keys — no `messages`, no internal scratch
```

What's worth noticing:

- **Three reducers, three flavors.** `add_messages` for appending; custom `union` for deduplicated set merge; custom `keep_max` for "best score wins." Each picked for the data's semantics.
- **Parallel nodes update the same keys.** `search_internal` and `search_web` both write `sources` and `confidence`. The reducers merge their contributions — without reducers, the second-to-finish would overwrite the first.
- **The caller sees only `OutputState`.** No `messages` in the output dict, no internal scratch — the graph hides what isn't the API.
- **State stays small.** We track URLs, not the full retrieved text. Bulk data would live in a vector store or object storage and be looked up by URL.

When designing a new graph, the order to think through is: input schema → output schema → what mutable fields need reducers → nodes → edges. Get the data shape right and the rest follows.
