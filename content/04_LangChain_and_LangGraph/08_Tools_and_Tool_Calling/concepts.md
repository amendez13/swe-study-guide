## What "tool calling" means

The LLM doesn't run your code — it **emits a structured request** to run it. The contract:

1. You give the model a list of tools, each with a name, description, and JSON schema for its arguments.
2. The model, when it decides a tool is needed, returns an `AIMessage` containing one or more `tool_calls` — structured records with `name`, `args`, and `id`.
3. Your code finds the matching tool, executes it with the args, and returns a `ToolMessage` referencing the `tool_call_id`.
4. The model sees the tool result and continues, often calling more tools or producing a final answer.

The model never directly invokes anything; it asks, and your code decides whether/how to fulfill the request. This separation is the entire safety story for tool use.

## The `@tool` decorator

The canonical way to turn a Python function into a tool. The function signature becomes the tool's JSON schema; the docstring becomes its description.

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city, e.g. "Paris" or "Tokyo".
    """
    return weather_api.fetch(city)
```

The docstring matters: it's what the model sees, and a vague docstring leads to misuse. Treat tool docstrings as prompt engineering — they're prompts in disguise.

Type hints matter too: `city: str` becomes `"type": "string"` in the schema; `count: int` becomes `"integer"`. For richer types (constrained values, structured args), use a Pydantic model.

## Binding tools to a model

Tools become available to the model by `bind_tools(...)`:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
model_with_tools = model.bind_tools([get_weather, get_time, search_web])

response = model_with_tools.invoke("What's the weather in Paris?")
# response.tool_calls = [{"name": "get_weather", "args": {"city": "Paris"}, "id": "..."}]
```

`bind_tools` doesn't execute anything — it just tells the model which tools exist. The execution loop is your responsibility (or LangGraph's `ToolNode`, covered below).

## Executing tool calls

The minimal hand-rolled loop:

```python
from langchain_core.messages import HumanMessage, ToolMessage

tools_by_name = {t.name: t for t in [get_weather, get_time]}

messages = [HumanMessage("What's the weather in Paris and what time is it?")]
while True:
    response = model_with_tools.invoke(messages)
    messages.append(response)
    if not response.tool_calls:
        break                  # final answer
    for call in response.tool_calls:
        result = tools_by_name[call["name"]].invoke(call["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
```

This is what `create_react_agent` does for you, plus error handling and max-iteration limits. Write the loop by hand once to understand it; use the helper afterward.

## LangGraph's `ToolNode`

In LangGraph, tool execution is a prebuilt node you can drop into a graph:

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([get_weather, get_time])

# Inside a graph
graph.add_node("tools", tool_node)
graph.add_edge("tools", "agent")    # back to the model after running tools
```

`ToolNode` reads `tool_calls` from the last `AIMessage` in state, executes them, and writes the `ToolMessage`s back to state via the `add_messages` reducer. It handles parallel tool calls, errors, and structured outputs without you writing the plumbing.

## Pydantic arg schemas for richer tools

For tools that take more than a couple of primitives, declare the args as a Pydantic model and pass it as `args_schema`:

```python
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, ge=1, le=20)
    region: Literal["us", "eu", "asia"] | None = None

@tool(args_schema=SearchArgs)
def search(query: str, max_results: int = 5, region: str | None = None) -> list[dict]:
    """Search the web. Filter by region when relevant."""
    return search_api.query(query, max_results=max_results, region=region)
```

The Pydantic schema flows to the model as JSON Schema with validators (`ge=1`, `le=20`, enum values for `region`). The model sees the constraints and respects them — usually.

## Tool errors and recovery

Tools fail: APIs go down, args are wrong, rate limits hit. Three policies for handling that:

- **Surface to model** — return the error as the tool's output (`return f"Error: {e}"`). The model can react, retry with different args, or fall back. This is the default in `ToolNode`.
- **Raise to caller** — re-raise the exception; the agent loop exits and the user sees the error. Right when the failure is unrecoverable (auth missing, bug in code).
- **Retry transparently** — wrap the tool in `.with_retry()` so transient failures don't leak to the model.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def flaky_api_call(query: str) -> str:
    """..."""
    return external_api.fetch(query)
```

A tool that can never fail is rare. Decide the policy at tool-definition time, not in scattered try/except.

## Built-in toolkits

LangChain ships ready-made tool collections under `langchain-community.tools` and `langchain.agents.tools`:

- **Search** — Tavily, SerpAPI, DuckDuckGo, Bing, Google
- **Web scraping** — `BeautifulSoupTransformer`, `PlaywrightURLLoader`
- **Code execution** — `PythonREPLTool`, `ShellTool` (with sandboxing!)
- **SQL** — `QuerySQLDataBaseTool`, `InfoSQLDatabaseTool`
- **Filesystem** — `ReadFileTool`, `WriteFileTool`, `ListDirectoryTool`
- **Calendar / email / Slack** — workflow integrations

A "toolkit" is just a list of related tools. Use them as starting points — most production agents replace generic toolkits with a curated set of tools that match the exact job.

## Function calling vs JSON mode vs ReAct text parsing

Three eras of how the model decides to use a tool, in order of preference:

- **Function/tool calling** (current) — provider-native, structured. The response has a dedicated `tool_calls` field. Reliable and well-supported. Use this.
- **JSON mode** — provider returns JSON conforming to a schema; you parse the JSON to figure out what tool to call. Workable, more brittle than tool calling.
- **ReAct text parsing** (legacy) — model emits free text like `Thought: ... / Action: get_weather / Action Input: Paris`, and you regex it out. The original 2022/2023 approach; superseded by tool calling. You'll see it in older tutorials; don't reach for it in new code.

`bind_tools` automatically picks the best available mechanism for the provider; you mostly don't have to think about which is in use.

## Tool safety

Tools cross the boundary from "the model talks" to "the model does things in the world." That changes the threat model:

- **Untrusted args** — the model can produce surprising or adversarial args (especially under prompt injection). Validate at the tool boundary as if it were user input.
- **Side-effecting tools** — anything that writes (send_email, delete_file, charge_card) needs guardrails: human approval, dry-run mode, idempotency keys, allowlists. Don't put `rm` in an agent's toolkit.
- **Code execution** — `PythonREPLTool` and shell tools need real sandboxes (Docker, gVisor, restricted Python interpreters), not just prompt-level warnings.
- **Resource limits** — set timeouts, max iterations, max cost. An agent in a tool loop can burn money fast.

See [Security and Safety](../21_Security_and_Safety/) for the broader threat model. The short version: a tool that performs irreversible actions should always have a human in the loop or a deterministic policy gate between the model's decision and the action.
