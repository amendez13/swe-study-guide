## Agent vs chain

A **chain** runs a fixed sequence of steps; an **agent** chooses the sequence at runtime by picking among tools. Same primitives (model, prompts, tools); different control flow.

- **Chain** — `prompt | retriever | model | parser`. Always the same path, regardless of input. Deterministic, fast, cheap.
- **Agent** — model picks `search` or `calculator` or `terminate` per turn, possibly looping. Adaptive, slow, expensive.

Use a chain when the steps are known. Use an agent when they aren't — when the right action depends on what the previous one returned.

The mistake teams make: reaching for an agent because it's the impressive thing. Most "agent" use cases are really chains in disguise, and a chain version would be 5x cheaper, 5x faster, and easier to debug.

## Agent prompt structure

An agent's system prompt has three jobs:

1. **Role and persona** — who the agent is acting as. ("You are a customer-support assistant for Acme.")
2. **Tool guidance** — when to use each tool, when not to. Critical for steering the agent's choices.
3. **Output expectations** — format, tone, what counts as a complete answer.

```python
SYSTEM = """You are a research assistant for Acme employees.

Tools:
- web_search: use for facts that change (news, current events). Don't use for arithmetic.
- internal_docs: use first for Acme-specific questions (policies, products).
- calculator: always use for arithmetic — never compute it yourself.

If a question is outside Acme's domain and not a current event, answer from
general knowledge without calling tools. Be concise; cite sources when you
use web_search or internal_docs.
"""
```

A good agent system prompt does the work of debugging-by-prompt: every behavior you wish the agent had, you state explicitly here.

## `AgentExecutor` (legacy)

The v0.x way to run agents. It accepted an agent (a `Runnable` that returns either a tool call or a final answer) and a tool list, and ran the loop with retries and parsing.

```python
# Legacy — you'll see this in older code
from langchain.agents import AgentExecutor, create_openai_tools_agent

agent = create_openai_tools_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, max_iterations=10)
executor.invoke({"input": "What's the weather in Paris?"})
```

Replaced in LangChain v1 by `create_react_agent` from LangGraph. `AgentExecutor` still works but is soft-deprecated; new code should use the LangGraph form.

## `create_react_agent` — the modern path

LangGraph's prebuilt ReAct agent — covered in detail in [The ReAct Loop](../09_The_ReAct_Loop/). Three lines from zero to working agent:

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, tools)
result = agent.invoke({"messages": [HumanMessage("...")]})
```

Under the hood it's a two-node graph (agent ↔ tools), but you don't need to think about that to use it. When you outgrow the prebuilt — different exit conditions, parallel tool calling, structured intermediate state — you drop down to a hand-built `StateGraph` (see [LangGraph Fundamentals](../11_LangGraph_Fundamentals/)).

## Choosing between agent types

LangChain/LangGraph supports several agent styles. The two that matter:

- **ReAct** (`create_react_agent`) — the default. Reasoning + tool calling in a single loop. Use for 95% of cases.
- **Plan-and-Execute** — the agent writes a multi-step plan upfront, then executes each step. Better for long, well-decomposed tasks (research reports, code refactors); worse when reality disagrees with the plan mid-execution.

Older typed agents (`OpenAI Functions Agent`, `Structured Chat Agent`, `XML Agent`) exist for historical reasons; they're all flavors of "ReAct with a different tool-call serialization." Modern tool-calling providers make these distinctions irrelevant.

## Cost and latency reality

An agent that runs 5 iterations costs 5× the LLM calls of a single chain. Concretely:

- A chain with one `gpt-4o-mini` call: ~500ms, ~$0.0002.
- A 5-iteration agent: ~3 seconds, ~$0.001 — plus tool execution time.
- A 15-iteration agent with `gpt-4o`: 20+ seconds, ~$0.05 per request.

For interactive UI: agents feel slow because they are slow. Streaming intermediate steps (covered in [Streaming](../15_Streaming/)) makes the wait tolerable; nothing makes it fast.

For batch jobs: every multiplication by N is real money. Don't run agents at scale without a budget on iterations per task and an alert when it exceeds.

## Bounding the loop

Three guardrails every production agent needs:

- **`max_iterations`** — hard cap on tool calls; the agent gives up after N. Default to 10–15 for general use, lower for predictable tasks.
- **`recursion_limit`** (LangGraph) — max graph steps; defends against subgraph loops.
- **Per-task budget** — track cumulative tokens or cost and abort when exceeded. Useful when iteration count is too coarse.

```python
agent.invoke(
    {"messages": [HumanMessage(question)]},
    config={"recursion_limit": 25},
)
```

A runaway agent costs real money in real time. Caps are non-negotiable in production.

## Agents and structured output

Agents can produce structured final answers, not just text. Configure the response schema once and the agent returns the validated object on the last step:

```python
class Answer(BaseModel):
    summary: str
    confidence: Literal["low", "medium", "high"]
    sources: list[str]

agent = create_react_agent(model, tools, response_format=Answer)
result = agent.invoke({"messages": [...]})
typed_answer: Answer = result["structured_response"]
```

Useful when downstream code needs typed fields, not free-form text. Combine with the patterns from [Output Parsing and Structured Output](../04_Output_Parsing_and_Structured_Output/).

## When to write your own agent loop

Reach past the prebuilt when you need any of:

- **Custom loop conditions** — exit when a budget is hit, not just when tools stop being called.
- **Parallel branches** — different sub-agents working on different aspects of the task.
- **Human approval steps** — pause before specific tools (covered in [Human-in-the-Loop](../16_Human-in-the-Loop/)).
- **Multi-stage state** — distinct phases (research, draft, review) with different tool sets per phase.
- **Sub-graph composition** — agents within agents, with their own state.

For each of these, build a `StateGraph` by hand instead. The prebuilt agent is for "model + tools + a default loop"; once you need to customize the loop, you're past its scope.
