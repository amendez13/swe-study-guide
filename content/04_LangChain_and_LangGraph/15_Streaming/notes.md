# Streaming

How to surface progress and intermediate output from a LangGraph application instead of making the user wait for the final state. Picking the right stream mode is most of the work.

## Key Points

- **Three kinds of events** — state updates, full state values, LLM token chunks. Pick by consumer.
- **`stream_mode="updates"`** — node-by-node state diffs; the canonical progress feed.
- **`stream_mode="values"`** — full state at each step; for debug viewers and dashboards.
- **`stream_mode="messages"`** — LLM token chunks with `langgraph_node` metadata; what chat UIs use.
- **Multiple modes** — pass a list; events arrive as `(mode, payload)` tuples.
- **`astream_events(version="v2")`** — fine-grained event stream for custom telemetry; always v2.
- **Custom node streaming** — `get_stream_writer()` + `stream_mode="custom"` to forward your own payloads.
- **Cancellation** — break the iterator or raise `CancelledError`; bind to HTTP connection close in web apps.

## Example

A small agent that streams **both** node-by-node progress and LLM tokens to the user, simulating a chat UI that wants a status bar plus visible text:

```python
import asyncio
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    return f"22°C and sunny in {city}"


class State(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([get_weather])


def agent_node(state: State) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


def route(state: State) -> str:
    return "tools" if state["messages"][-1].tool_calls else END


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode([get_weather]))
graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})

app = graph.compile()


async def chat_stream(question: str) -> None:
    """Stream both progress updates and final-answer tokens to stdout."""
    input_state = {
        "messages": [
            SystemMessage("Be concise. Use the weather tool when asked about weather."),
            HumanMessage(question),
        ]
    }

    final_node_reached = False

    async for mode, payload in app.astream(
        input_state, stream_mode=["updates", "messages"]
    ):
        if mode == "updates":
            # payload is {node_name: state_diff}
            for node in payload:
                print(f"\n  ▶ {node}", end="", flush=True)
                if node == "agent":
                    # Final answer comes from the second `agent` call (after tools).
                    # A real UI would track this state more carefully; we use a flag.
                    pass

        elif mode == "messages":
            chunk, metadata = payload
            # Only stream tokens from the agent node, not from sub-LLMs (none here).
            # In production, also filter by "is this the final answer or an
            # intermediate tool-call thought?" — usually by checking metadata.
            if metadata.get("langgraph_node") == "agent":
                print(chunk.content or "", end="", flush=True)

    print()    # final newline


if __name__ == "__main__":
    asyncio.run(chat_stream("What's the weather in Paris and Tokyo?"))
```

Sample output (token stream interleaved with progress markers):

```
  ▶ agent
  ▶ tools
  ▶ agent It's 22°C and sunny in both Paris and Tokyo right now.
```

What's worth noticing:

- **`stream_mode=["updates", "messages"]`** gives both feeds in one consumer — no need to run two streams in parallel.
- **`metadata["langgraph_node"]`** filters which LLM's tokens reach the user. In a multi-step graph (research → draft → critic), you'd usually only want tokens from the user-facing final node.
- **`updates` shows the graph's choreography** — the agent runs, calls a tool, then runs again to produce the final answer. The user sees this as a status bar; you see it in the trace.
- **Cancellation** is implicit — break the `async for` and the in-flight node finishes, the graph state is saved (if a checkpointer is configured), and no further LLM calls happen. Wire this to `request.is_disconnected()` in a FastAPI route and you've built a polite chat backend.
