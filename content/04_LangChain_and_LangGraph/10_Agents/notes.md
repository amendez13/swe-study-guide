# Agents

The framework's name for "an LLM that picks its own next step." Most useful when steps aren't known upfront; most overused when they are.

## Key Points

- **Agent vs chain** — chains run fixed sequences; agents pick the sequence at runtime.
- **System prompt does heavy lifting** — role, tool guidance, output expectations. Most production tuning happens here.
- **`AgentExecutor` is legacy** — `create_react_agent` from LangGraph replaced it in v1+.
- **ReAct is the default agent type** — Plan-and-Execute for long decomposable tasks; historical agent classes are flavors of ReAct.
- **Cost scales with iterations** — a 5-step agent costs 5× a one-shot chain. Stream intermediate steps for UX.
- **Bound the loop** — `max_iterations`, `recursion_limit`, per-task budget. Required in production.
- **Structured final answers** — `response_format=Pydantic` makes the agent return a typed object.
- **Write your own loop** when you need custom exit conditions, parallel sub-agents, approval steps, or multi-stage state.

## Example

A research-assistant agent with a deliberately specific system prompt, structured final answer, iteration cap, and tool-cost discipline:

```python
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


# --- Tools ---
@tool
def web_search(query: str) -> str:
    """Search the public web for current events, news, or facts that change
    over time. Returns top result snippets. Do NOT use for arithmetic or
    Acme-internal questions."""
    return f"[stub web results for: {query!r}]"


@tool
def internal_docs(query: str) -> str:
    """Search Acme's internal knowledge base. Use first for Acme policy,
    product, or process questions."""
    return f"[stub internal docs for: {query!r}]"


@tool
def calculator(expression: str) -> str:
    """Evaluate arithmetic. Always use this for any computation — never
    compute it yourself."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"Error: bad chars in {expression!r}"
    return str(eval(expression, {"__builtins__": {}}, {}))


# --- Structured final answer ---
class Answer(BaseModel):
    summary: str = Field(description="One- to three-sentence answer.")
    confidence: Literal["low", "medium", "high"]
    sources: list[str] = Field(
        default_factory=list,
        description="Tool calls or URLs the answer is based on.",
    )


# --- System prompt does the steering ---
SYSTEM = """You are a research assistant for Acme employees.

Tool policy:
- internal_docs first for Acme policy, products, processes.
- web_search for current events or external facts.
- calculator for any arithmetic.
- No tool if the question is general knowledge that doesn't change.

Be concise. Cite which tool calls back each fact in your summary.
Confidence levels: 'high' = direct quote from a tool, 'medium' = synthesized
from multiple results, 'low' = inference without strong support."""


# --- Agent ---
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(
    model,
    tools=[web_search, internal_docs, calculator],
    response_format=Answer,
)


def ask(question: str) -> Answer:
    result = agent.invoke(
        {"messages": [SystemMessage(SYSTEM), HumanMessage(question)]},
        config={"recursion_limit": 15},          # hard cap
    )
    return result["structured_response"]


if __name__ == "__main__":
    a = ask("What's Acme's parental leave policy and how does it compare to the US average?")
    print(f"Summary:    {a.summary}")
    print(f"Confidence: {a.confidence}")
    print(f"Sources:    {a.sources}")
```

What's worth noticing:

- **Tool policy lives in the system prompt.** "internal_docs first" and "calculator for any arithmetic" steer the agent's choices; without that the model often skips the calculator and gets arithmetic subtly wrong.
- **`recursion_limit=15`** caps the loop. A question that requires more than 15 steps is probably one the agent shouldn't be answering anyway.
- **`response_format=Answer`** turns the final message into a Pydantic instance. Downstream code consumes `summary`, `confidence`, `sources` as typed fields, not parsed prose.
- **Confidence is part of the contract** — the prompt defines what each level means. Without that, the model would assign random values and you'd be back to vibes.

When this agent isn't enough — multi-stage research with separate planning, distinct review/approval phases, parallel sub-questions — you outgrow the prebuilt and build a `StateGraph` by hand. See [LangGraph Fundamentals](../11_LangGraph_Fundamentals/).
