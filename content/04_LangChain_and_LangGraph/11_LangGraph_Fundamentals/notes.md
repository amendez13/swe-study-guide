# LangGraph Fundamentals

The orchestration layer that handles what LCEL can't: cycles, stateful branching, persistence, and pausing. Once you internalize state + nodes + edges, every LangGraph application is a variation on a single template.

## Key Points

- **Why LangGraph** — cycles, branching on state, pause/resume, per-conversation persistence. Things chains can't express.
- **`StateGraph` vs `MessageGraph`** — `StateGraph` for any state shape; `MessageGraph` only for pure-message graphs.
- **Nodes** — pure functions `State → dict`; the returned dict is merged into state.
- **Edges** — `add_edge(a, b)` always traverses; `add_conditional_edges(a, fn, mapping)` picks dynamically.
- **`START` and `END`** — sentinel entry and exit nodes; every graph needs both reachable.
- **`compile()` returns a `Runnable`** — same interface as everything else; composes into LCEL.
- **Two-node ReAct graph** — the entire pattern behind every framework agent in 10 lines.
- **Subgraphs** — a compiled graph is a `Runnable`, so it can be a node in another graph.

## Example

A two-node ReAct agent built from scratch — the same thing `create_react_agent` produces, but written out so every primitive is visible:

```python
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# 1. State schema — the contract for the whole graph
class State(TypedDict):
    messages: Annotated[list, add_messages]    # add_messages = append reducer


# 2. Tools
@tool
def calculator(expression: str) -> str:
    """Evaluate arithmetic."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"Error: bad chars in {expression!r}"
    return str(eval(expression, {"__builtins__": {}}, {}))


tools = [calculator]


# 3. Nodes
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)


def agent_node(state: State) -> dict:
    """Call the model with the current message history."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}            # add_messages appends


tool_node = ToolNode(tools)                    # prebuilt; executes tool_calls


# 4. Router — picks the next node based on state
def route(state: State) -> str:
    last: AIMessage = state["messages"][-1]
    return "tools" if last.tool_calls else END


# 5. Build the graph
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")               # after tools, go back to agent
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({
        "messages": [
            SystemMessage("Always use the calculator for arithmetic."),
            HumanMessage("What's 17 * 23 + 100?"),
        ]
    })

    # Print the trace
    for m in result["messages"]:
        kind = type(m).__name__
        preview = (m.content or "").strip()[:80]
        print(f"{kind:14} {preview}")
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                print(f"               → tool_call: {tc['name']}({tc['args']})")
```

What's worth noticing:

- **The state schema is the whole contract.** Add a key to `State` and every node can read/write it. The schema is what makes the graph debuggable — you can `pprint(result)` and see exactly what happened.
- **`add_messages` is a reducer.** Returning `{"messages": [response]}` doesn't replace the message list; it appends. Without that annotation, every node would clobber the prior messages.
- **The router is a separate function.** Its job is to read state and return a string. That string maps to an actual next-node via the mapping passed to `add_conditional_edges`.
- **`END` is special.** It's a sentinel that returns control to the caller of `.invoke()`. Routing to `END` is how the graph terminates.
- **Compiled graph is a `Runnable`.** `app.invoke(...)`, `app.batch(...)`, `app.stream(...)` all work. So does `another_graph.add_node("sub", app)` — graphs compose.

Once this shape is in your head, every more complex LangGraph application — multi-agent systems, self-improving agents, deep-research workflows — is just more nodes, more state keys, and more conditional edges. The fundamental primitives don't change.
