# Multi-Agent Systems

When one agent's prompt can't carry the load, you split into multiple. The patterns are well-trodden; the cost is real. Pick deliberately.

## Key Points

- **Why multi-agent** — clearer responsibilities, smaller surface area; same logic as microservices.
- **Supervisor pattern** — hub-and-spoke; supervisor routes to specialists. The most common topology.
- **Hierarchical teams** — supervisors of supervisors; useful when domains have natural nesting.
- **Swarm / peer-to-peer** — agents hand off directly; harder to control, occasionally the right shape.
- **State strategy** — shared state is simple but error-prone; scoped per-agent state is cleaner.
- **Message passing** — append, tag with `name=`, or summarize between handoffs to avoid context blowup.
- **Compiled subgraphs as nodes** — each sub-agent is independently testable and replaceable.
- **Coordination patterns** — pipeline, router, parallel + aggregator, iterative loop, negotiation.
- **Risks compound** — prompt injection between agents, error multiplication, cost explosion, debugging difficulty.
- **When NOT** — most "multi-agent" needs can be solved by one well-prompted agent with multiple tools.

## Example

A supervisor-pattern research-and-write graph: a researcher subagent gathers sources, a writer subagent drafts an answer, the supervisor decides when the task is done. Each subagent is a compiled subgraph.

```python
from typing import Literal
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


# --- Top-level state ---
class OverallState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    findings: list[str]
    draft: str
    next: str           # which agent runs next


# --- Researcher subagent ---
@tool
def search(query: str) -> str:
    """Search for facts."""
    return f"[stub: results for {query!r}]"


researcher = create_react_agent(
    ChatOpenAI(model="gpt-4o-mini", temperature=0),
    tools=[search],
    state_modifier=SystemMessage(
        "You are a researcher. Gather 3-5 concise findings related to the "
        "question. Return them as a numbered list. Do not write prose."
    ),
)


def researcher_node(state: OverallState) -> dict:
    result = researcher.invoke({"messages": [HumanMessage(state["question"])]})
    findings_text = result["messages"][-1].content
    findings = [
        line.strip()
        for line in findings_text.split("\n")
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-"))
    ]
    return {
        "findings": findings,
        "messages": [AIMessage(findings_text, name="researcher")],
    }


# --- Writer subagent ---
writer_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def writer_node(state: OverallState) -> dict:
    if not state.get("findings"):
        return {"messages": [AIMessage("No findings yet — researcher should run first.",
                                       name="writer")]}
    findings = "\n".join(f"- {f}" for f in state["findings"])
    response = writer_model.invoke([
        SystemMessage(
            "You are a writer. Produce a two-paragraph answer grounded in the "
            "findings below. Cite them by number where appropriate."
        ),
        HumanMessage(f"Question: {state['question']}\n\nFindings:\n{findings}"),
    ])
    return {"draft": response.content, "messages": [AIMessage(response.content, name="writer")]}


# --- Supervisor ---
class Routing(BaseModel):
    next: Literal["researcher", "writer", "FINISH"] = Field(
        description="Who should act next. FINISH when the draft is good enough."
    )
    reason: str


supervisor_model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Routing)


def supervisor_node(state: OverallState) -> dict:
    summary = (
        f"Question: {state['question']}\n"
        f"Findings count: {len(state.get('findings', []))}\n"
        f"Draft present: {bool(state.get('draft'))}"
    )
    decision: Routing = supervisor_model.invoke([
        SystemMessage(
            "Route work between two subagents:\n"
            "- 'researcher' gathers findings (run first, or when more facts needed)\n"
            "- 'writer' produces the final draft (run after findings exist)\n"
            "- 'FINISH' when a draft is present and acceptable\n"
        ),
        HumanMessage(summary),
    ])
    return {"next": decision.next, "messages": [AIMessage(decision.reason, name="supervisor")]}


def route(state: OverallState) -> str:
    return END if state["next"] == "FINISH" else state["next"]


# --- Graph ---
graph = StateGraph(OverallState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("writer", writer_node)

graph.add_edge(START, "supervisor")
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route,
    {"researcher": "researcher", "writer": "writer", END: END},
)

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({
        "question": "What's the difference between asyncio and multiprocessing in Python?",
        "messages": [],
        "findings": [],
        "draft": "",
        "next": "",
    })

    print("=== Final draft ===")
    print(result["draft"])
    print()
    print("=== Supervisor / subagent trace ===")
    for m in result["messages"]:
        name = getattr(m, "name", "system")
        preview = (m.content or "").strip()[:100]
        print(f"[{name:10}] {preview}")
```

What's worth noticing:

- **Hub-and-spoke topology.** Every subagent returns to the supervisor; the supervisor decides what's next. No subagent talks to another directly.
- **Subagent isolation.** `researcher` is a compiled `create_react_agent` with its own tools; `writer` is a single LLM call. Both are nodes in the orchestrator but their internals are independent.
- **`name=` on `AIMessage`.** Each message in the trace is tagged with who said it. In a real UI, that's how you'd render "Researcher found 4 sources" vs "Writer drafted the answer."
- **Structured routing.** The supervisor uses `with_structured_output(Routing)` instead of free-text parsing. `next` is `Literal["researcher", "writer", "FINISH"]` — no ambiguity, no parsing failures.
- **State stays small.** `findings` is a list of short strings; the writer summarizes them rather than carrying every retrieved doc. In a real research agent, raw retrievals would live in a vector store and `findings` would be IDs or short citations.

If this topology grows past 3-4 specialists, consider hierarchical teams: a "research team" supervisor of its own and a "writing team" supervisor, with the top-level supervisor coordinating them. Past that, the system is probably trying to be too much; refactor toward fewer, sharper agents.
