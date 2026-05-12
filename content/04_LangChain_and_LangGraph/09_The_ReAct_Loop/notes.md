# The ReAct Loop

The simplest agent pattern that works, and still the default in 2026. Reason → Act → Observe, repeat until the model is ready to answer.

## Key Points

- **ReAct = Reason + Act** — model thinks, picks a tool, sees the output, repeats; final answer when no more tool calls.
- **Three phases per iteration** — reason (pick a tool), act (execute), observe (feed the result back).
- **`create_react_agent`** — LangGraph's prebuilt helper; replaces the legacy v0 `AgentExecutor`.
- **Loop termination** — exits when the model returns an `AIMessage` with no `tool_calls`.
- **Cap iterations** — always set a max so a stuck agent can't burn an unbounded budget.
- **Five failure modes** — infinite loops, tool-call hallucination, argument drift, premature finalization, excessive loop length.
- **Text-parsing ReAct is legacy** — native tool calling replaced the `Thought: / Action:` format.
- **When ReAct wins** — single-step debuggability, no rigid plan, cheap to iterate.
- **When NOT to use ReAct** — deterministic workflows, latency-critical endpoints, high-throughput batch.

## Example

A by-hand ReAct loop alongside the prebuilt `create_react_agent`, so you can see exactly what the helper is doing. Both end on a model response with no `tool_calls`.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression with +, -, *, /, parens."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"Error: invalid characters in {expression!r}"
    return str(eval(expression, {"__builtins__": {}}, {}))


@tool
def current_time(timezone: str = "UTC") -> str:
    """Return the current time in the given IANA timezone."""
    return datetime.now(ZoneInfo(timezone)).isoformat()


tools = [calculator, current_time]
tool_lookup = {t.name: t for t in tools}


# --- Hand-rolled ReAct loop ---
def react_manual(model, question: str, *, max_iters: int = 10) -> tuple[str, int]:
    """Returns (final_answer, number_of_iterations)."""
    bound = model.bind_tools(tools)
    messages = [
        SystemMessage(
            "You answer using the available tools. Always use the calculator "
            "for arithmetic; never compute it yourself."
        ),
        HumanMessage(question),
    ]

    for i in range(1, max_iters + 1):
        response: AIMessage = bound.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content, i

        for call in response.tool_calls:
            try:
                result = tool_lookup[call["name"]].invoke(call["args"])
            except Exception as e:
                result = f"Error: {e}"
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    return "[max iterations reached]", max_iters


# --- Prebuilt LangGraph ReAct agent ---
def react_prebuilt(model, question: str) -> str:
    agent = create_react_agent(model, tools)
    result = agent.invoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    question = "What's 17 * 23 plus 100, and what time is it in Tokyo right now?"

    answer, iters = react_manual(model, question)
    print(f"Manual    ({iters} iterations): {answer}")

    answer = react_prebuilt(model, question)
    print(f"Prebuilt agent                : {answer}")
```

What's worth noticing:

- **The system prompt sets policy** — "Always use the calculator for arithmetic" is the difference between a model that respects the tool and one that does mental math.
- **`max_iters=10`** — even with two simple tools this should finish in 2-3 iterations; the cap is insurance against a model that gets stuck.
- **Errors flow back to the model** — when a tool call raises, we send `"Error: ..."` as the `ToolMessage`. The model can react, fix args, or give up gracefully.
- **The prebuilt agent does the same thing** — it builds a two-node LangGraph (agent ↔ tools) with the same exit condition. Use the helper in production; write the loop once to understand what the helper is doing.
