# Tools and Tool Calling

How the model "does things in the world" — by emitting structured requests that your code chooses whether to fulfill. The single most important LLM-application feature after basic generation.

## Key Points

- **The model never executes** — it emits `tool_calls`; your code runs them and returns `ToolMessage` results.
- **`@tool` decorator** — turns a Python function into a tool; signature → JSON schema, docstring → description.
- **`bind_tools`** — registers tools with a model so it knows what's available.
- **Manual execution loop** — read `tool_calls`, run them, append `ToolMessage`s, loop until no tool calls.
- **`ToolNode`** — LangGraph's prebuilt tool-executor node; drop it into a graph and you're done.
- **Pydantic arg schemas** — for tools with complex args; constraints flow into the model's JSON Schema.
- **Error handling policy** — surface to model, raise to caller, or retry transparently; pick at definition time.
- **Built-in toolkits** — search, scraping, code, SQL, filesystem; useful starting points.
- **Function calling beats text parsing** — modern providers expose native tool calling; legacy ReAct text parsing is brittle.
- **Tool safety** — validate args, sandbox code execution, gate side-effecting tools with approval or policy.

## Example

A research assistant that has three tools (web search, calculator, current time), wired into a LangGraph ReAct agent so you can see both the manual loop and the prebuilt path:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


# --- Tool definitions ---
@tool
def web_search(query: str) -> str:
    """Search the web and return top result snippets. Use for current events
    or facts that change over time."""
    # In real code: call Tavily, SerpAPI, etc.
    return f"[stub search results for: {query!r}]"


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression. Supports +, -, *, /, parens.
    Do not use for general code execution."""
    # In real code: a sandboxed evaluator, not eval()
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"Error: invalid characters in {expression!r}"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"


@tool
def current_time(timezone: str = "UTC") -> str:
    """Return the current time in the given IANA timezone (e.g. 'UTC',
    'America/New_York', 'Asia/Tokyo')."""
    try:
        return datetime.now(ZoneInfo(timezone)).isoformat()
    except Exception as e:
        return f"Error: {e}"


tools = [web_search, calculator, current_time]
tool_lookup = {t.name: t for t in tools}


# --- Path 1: hand-rolled loop (instructive) ---
def run_manual(model, question: str, max_iters: int = 5) -> str:
    model_with_tools = model.bind_tools(tools)
    messages = [HumanMessage(question)]
    for _ in range(max_iters):
        response = model_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for call in response.tool_calls:
            result = tool_lookup[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return "[max iterations reached]"


# --- Path 2: prebuilt ReAct agent (production path) ---
def run_agent(model, question: str) -> str:
    agent = create_react_agent(model, tools)
    result = agent.invoke({"messages": [HumanMessage(question)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    question = "What's 17 * 23, and what time is it in Tokyo?"

    print("Manual loop:")
    print(run_manual(model, question))
    print()
    print("LangGraph agent:")
    print(run_agent(model, question))
```

Both paths reach the same answer; one teaches you how the loop works, the other is what you ship.

What's worth noticing:

- **Tool docstrings carry intent** — `"Use for current events"`, `"Do not use for general code execution"`. The model reads these.
- **Calculator validates its input** — a 5-line allowlist guards against the model emitting `os.system(...)`. Always validate at the tool boundary.
- **Each tool returns a string** — even `current_time` formats the `datetime`. `ToolMessage.content` is text; non-string returns get stringified, which can lose precision.
- **Max iterations** — the manual loop caps at 5. The prebuilt agent does the same internally. Always cap the loop; an agent that won't stop is a bigger problem than one that gives up early.
