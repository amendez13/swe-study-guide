# Self-Improving Agent Patterns

How an agent gets better at one task by criticizing its own output and trying again. Different patterns target different failure modes.

## Key Points

- **Within-task improvement** — generator + critic loops; the model's weights don't change.
- **Reflection** — generator/critic alternation; the workhorse pattern.
- **Reflexion** — reflection with structured, persistent memory of past mistakes.
- **ReAct** — the foundational pattern; tool results are implicit feedback.
- **Corrective RAG (CRAG)** — grade retrieved chunks; rewrite query and retry when poor.
- **Self-RAG** — full Pareto: gate retrieval, grade chunks, grade generation, grade usefulness.
- **Adaptive RAG** — classify the question type first, route to a different strategy per type.
- **Plan-and-Execute** — write a plan upfront, execute step by step, replan when reality diverges.
- **Match pattern to failure mode** — most mistakes pick the wrong remedy.
- **Cost** — every critique step is another LLM call; measure quality lift via evals before adopting.
- **Hygiene** — bound the loop, structure critiques as Pydantic, persist for inspection.

## Example

A reflection-loop essay writer with a structured critique schema, bounded iterations, and an early exit when the critic says "good enough":

```python
from typing import Literal
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# --- Structured critique ---
class Critique(BaseModel):
    verdict: Literal["accept", "revise"]
    issues: list[str] = Field(
        default_factory=list,
        description="Specific things the writer should fix. Empty if accepting.",
    )
    rationale: str


# --- State ---
class State(TypedDict):
    topic: str
    draft: str
    critiques: Annotated[list[Critique], lambda a, b: (a or []) + (b or [])]
    iteration: int


generator_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
critic_model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Critique)


# --- Nodes ---
def generate(state: State) -> dict:
    if not state["critiques"]:
        prompt = f"Write a 3-paragraph essay on: {state['topic']}"
    else:
        last = state["critiques"][-1]
        prompt = (
            f"Rewrite the essay below to address these issues: {last.issues}\n\n"
            f"Original draft:\n{state['draft']}"
        )

    response = generator_model.invoke([
        SystemMessage("You are a careful, concise essay writer."),
        HumanMessage(prompt),
    ])
    return {"draft": response.content, "iteration": state.get("iteration", 0) + 1}


def critique(state: State) -> dict:
    result: Critique = critic_model.invoke([
        SystemMessage(
            "Critique the essay below. If it's good (clear thesis, supported "
            "claims, no factual errors), set verdict='accept'. Otherwise, "
            "set verdict='revise' and list specific issues to fix."
        ),
        HumanMessage(state["draft"]),
    ])
    return {"critiques": [result]}


def route(state: State) -> str:
    """Continue revising unless we've accepted or hit the cap."""
    if state["iteration"] >= 4:
        return END
    last = state["critiques"][-1]
    return END if last.verdict == "accept" else "generate"


# --- Graph ---
graph = StateGraph(State)
graph.add_node("generate", generate)
graph.add_node("critique", critique)
graph.add_edge(START, "generate")
graph.add_edge("generate", "critique")
graph.add_conditional_edges("critique", route, {"generate": "generate", END: END})

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({
        "topic": "Why Python's GIL still matters in 2026",
        "draft": "",
        "critiques": [],
        "iteration": 0,
    })

    print(f"Final draft (after {result['iteration']} iterations):")
    print(result["draft"])
    print()
    print("Critique trail:")
    for i, c in enumerate(result["critiques"]):
        print(f"  Round {i + 1}: {c.verdict} — {c.rationale}")
        for issue in c.issues:
            print(f"    - {issue}")
```

What's worth noticing:

- **Structured critique.** The `Critique` Pydantic model forces the critic to emit `verdict` + `issues` instead of prose. Downstream code can act on `last.issues`; logging it gives you a clean trail of what got fixed when.
- **Bounded loop.** `state["iteration"] >= 4` is a hard cap. An agent that refines forever is failing differently than one that gives up — but both are failing.
- **Different temperatures for generator and critic.** The generator runs at 0.7 (creativity); the critic at 0 (consistent grading). Wrong temperatures here is a common source of degraded loops.
- **Accumulating critiques.** The `critiques` field has a list-append reducer; the full history of critiques is available to the generator on every retry (so it can avoid re-introducing already-fixed issues).
- **Early exit.** When the critic accepts, the loop ends — no need to refine a draft that's already good.

To upgrade this to a Reflexion pattern, add a `reflections` field that persists across multiple distinct invocations (not just iterations within one task), and have the generator consult prior task reflections before starting. The CRAG / Self-RAG / Adaptive-RAG variants are the same shape applied to retrieval instead of generation.
