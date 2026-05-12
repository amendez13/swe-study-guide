## What ReAct is

ReAct (Yao et al., 2022) is the classic agent pattern: the model alternates between **reasoning** (thinking about the problem) and **acting** (calling a tool), interleaved with **observations** (the tool's output). The loop continues until the model decides it has enough information to produce a final answer.

```
Thought → Action → Observation → Thought → Action → Observation → … → Final Answer
```

It's the simplest agent that works, and it remains the default agent pattern in 2026 because it's well-understood, debuggable, and handles a remarkable range of tasks.

## Reason → Act → Observe

Each iteration of the loop has three phases:

- **Reason** — the model thinks aloud (or via tool-calling, picks a tool); it considers the question, what it knows, and what it needs.
- **Act** — the model emits a tool call, your code executes it.
- **Observe** — the tool's output (`ToolMessage`) is appended to the conversation and the model sees it on the next turn.

The "reasoning" used to mean an explicit `Thought:` text the model emitted (the original paper). Modern providers' tool calling makes the reasoning implicit — the model decides which tool to call without writing the thought aloud. Either way, the structure is the same.

## `create_react_agent` — the modern canonical helper

LangGraph's prebuilt ReAct agent. Three lines of setup for a working agent over a list of tools:

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
tools = [web_search, calculator, current_time]
agent = create_react_agent(model, tools)

result = agent.invoke({"messages": [HumanMessage("What's the temperature in Paris?")]})
print(result["messages"][-1].content)
```

Internally it builds a two-node LangGraph: an **agent** node that calls the model, a **tools** node that executes tool calls, and a conditional edge from agent → (tools OR END) based on whether the response has `tool_calls`. The whole loop is a 30-line graph; the helper saves you writing it.

This supersedes the v0.x `AgentExecutor` and `initialize_agent` paths. If you see those in tutorials, the tutorial is pre-LangGraph.

## Loop termination

The loop exits when the model emits an `AIMessage` with **no** `tool_calls` — at that point its content is the final answer. The exit condition lives in the conditional edge:

```python
def should_continue(state):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END
```

Two failure modes worth knowing:

- **No exit** — the model keeps calling tools forever. Cap with `max_iterations` or a step counter in state.
- **Premature exit** — the model gives up and answers without using a tool it should have used. Fix with better tool descriptions and prompt nudging ("Always use the calculator for arithmetic").

## When ReAct fails

The pattern is robust but not invincible. Known failure modes:

- **Infinite tool loops** — the model retries the same failing tool call with slightly different args. Cure: cap `max_iterations` (typically 5–15), surface tool errors as messages so the model can react.
- **Tool-call hallucination** — the model emits a tool call for a tool that doesn't exist or with args that don't match the schema. Cure: provider-side tool calling (vs ReAct text parsing) rejects invalid schemas; recent models rarely fabricate tool names.
- **Argument drift** — the model picks a tool but passes wrong args (city = "the user's city" instead of an actual city). Cure: better arg schemas with `Field(description=...)`, concrete examples in the tool docstring.
- **Premature finalization** — the model answers without using available info. Cure: stronger system prompt ("If the user asks for X, you must use tool Y"), or wrap with reflection.
- **Loop too long** — the agent finishes correctly but takes 12 tool calls when 3 would do. Cure: more capable model, better tool descriptions, or task-specific scaffolding.

Most production ReAct failures fall into one of these five buckets; debugging is largely a matter of recognizing which one and applying the corresponding fix.

## The original prompt format (legacy)

Before tool calling was a first-class provider feature, ReAct was implemented with **text parsing**:

```
You have access to: get_weather, calculator

Use this format:
Thought: I need to know the weather
Action: get_weather
Action Input: Paris
Observation: 18°C, partly cloudy
Thought: Now I can answer
Final Answer: It's 18°C and partly cloudy in Paris.
```

The framework regex'd `Action:` and `Action Input:` out of the model's text. Brittle: every change to the model's output style broke parsing. Tool calling replaced this in 2023–2024. You'll still see the `hwchase17/react` prompt template in older code; it's the legacy form and not recommended for new projects.

## Why ReAct dominates

Lots of fancier patterns exist (Tree of Thoughts, Plan-and-Execute, LATS, language agents). For most production work, ReAct still wins because it has three properties they lack:

- **Single-step reasoning** is easy to debug — each tool call is a discrete decision visible in the trace.
- **No upfront planning** — robust when the task changes shape mid-execution. Plan-and-Execute style agents commit to a plan early and struggle when reality disagrees.
- **Cheap to iterate** — improving a ReAct agent usually means improving prompts, descriptions, or tool implementations; rarely the agent loop itself.

Reach for fancier patterns when you have evidence ReAct is the bottleneck — not because the literature has more impressive names.

## When NOT to use ReAct

The loop's flexibility is also its cost: every iteration is an LLM call. Cases where it's the wrong tool:

- **Deterministic workflows** — if the steps are known, just write them as a chain. An agent is overkill for "summarize then translate."
- **Latency-sensitive endpoints** — a ReAct loop is multiple round trips. For real-time UI, single-call structured output is faster.
- **High-throughput batch jobs** — at scale, every saved LLM call multiplies into real money. Agent loops are 3–10x more expensive than direct chains.

A good rule of thumb: if you can write the steps as a fixed sequence, do that. Reach for ReAct when the sequence genuinely depends on intermediate results.
