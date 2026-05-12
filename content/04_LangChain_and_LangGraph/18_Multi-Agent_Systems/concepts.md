## Why multiple agents

A single agent has one prompt, one tool list, and one persona. That works until the task crosses domains — research and write and review, or a customer-support bot that has to handle billing, technical, and account questions. Stuffing every responsibility into one system prompt produces a confused agent that's bad at all of them.

Splitting into multiple agents is the same logic that motivates microservices: smaller surface area per agent, clearer responsibilities, easier to evolve one without breaking another. Each agent is good at its narrow job; an orchestrator routes work between them.

The cost: an agent calling another agent is many more LLM calls. Match the topology to the actual coordination need; multi-agent for show is the most expensive demo in software.

## Supervisor pattern

The most common multi-agent topology: a **supervisor** agent at the top routes the task to specialist sub-agents and aggregates their outputs.

```
                supervisor
              /     |     \
       researcher  coder  reviewer
```

The supervisor's job: read the task, decide which specialist handles it (or which specialists, in sequence), collect their results, decide whether the task is done.

In LangGraph this is a hub-and-spoke graph: the supervisor node has conditional edges out to each specialist and back; the specialists are compiled subgraphs.

```python
def supervisor(state):
    decision = supervisor_model.invoke(state["messages"])
    return {"next": decision.next_agent}        # "researcher" | "coder" | "FINISH"

def route(state):
    return state["next"] if state["next"] != "FINISH" else END

graph.add_conditional_edges(
    "supervisor",
    route,
    {"researcher": "researcher", "coder": "coder", "reviewer": "reviewer", END: END},
)
```

Most production multi-agent systems are some variant of this. Easy to reason about, easy to add new specialists.

## Hierarchical teams

Supervisors all the way down. Each specialist in a top-level supervisor pattern can itself be a supervisor of finer-grained agents.

```
                 top supervisor
                /              \
       research team       writing team
       /     |     \         /        \
    web   docs   data    drafter    editor
```

Useful when the problem domain naturally has nested structure (a "research team" with its own coordinator and specialists). Each sub-team can iterate internally without disturbing the rest of the system.

Two cautions:

- Latency adds up — every level of nesting is more orchestration calls.
- Debugging gets harder — trace what each sub-supervisor decided and why.

Most projects don't need more than two levels.

## Swarm / peer-to-peer

No central supervisor. Agents pass control to each other directly, deciding who handles the next step based on their own assessment.

```
        researcher ←→ writer ←→ critic
              ↑                    ↓
              └────────────────────┘
```

Each agent decides whether to do something or hand off, by emitting a special "transfer" tool call.

This is harder to control and easier to break: an agent might loop forever passing to itself, or two agents might fight over a task. Use when the workflow is genuinely peer-shaped (collaborative writing, adversarial debate) — not just to avoid writing a supervisor.

## State across agents

Two main strategies for what each sub-agent sees:

- **Shared state** — every agent reads and writes the same top-level state. Simple, but agents must respect each other's keys (one accidentally overwrites another's work).
- **Scoped state** — each sub-agent has its own internal state schema; the supervisor passes specific slices in and merges specific outputs back.

```python
class ResearchState(TypedDict):
    query: str
    findings: list[str]

class WritingState(TypedDict):
    findings: list[str]
    draft: str

class OverallState(ResearchState, WritingState):
    next: str

# Researcher subgraph compiled with state_schema=ResearchState
# Writer subgraph compiled with state_schema=WritingState
# Orchestrator graph uses OverallState
```

Scoped state is the cleaner pattern; it forces explicit contracts between agents.

## Message passing between agents

Subagents often communicate via `messages` (the chat history that flows between them). Common patterns:

- **Append findings.** Each sub-agent's response is appended; downstream agents see the full conversation.
- **Tag who said what.** Use `name=` on `AIMessage` so it's clear which agent produced each turn.
- **Summary handoff.** The supervisor reads the sub-agent's full output but passes only a summary to the next agent — avoids the context-window blowup that "shared messages" creates as the graph runs.

The summary-handoff pattern matters most: in a 5-agent pipeline, by the time the 5th agent runs, the first four agents' raw outputs may not all fit in the context window. Force structured summaries between handoffs.

## Sub-agents as compiled subgraphs

The cleanest way to compose multi-agent systems in LangGraph: compile each sub-agent as its own graph, then drop the compiled graph into the orchestrator as a node.

```python
researcher_app = researcher_graph.compile()
writer_app = writer_graph.compile()

orchestrator = StateGraph(OverallState)
orchestrator.add_node("researcher", researcher_app)
orchestrator.add_node("writer", writer_app)
orchestrator.add_edge("researcher", "writer")
```

Each sub-agent is independently testable, traceable, and replaceable. Pull a sub-agent out and use it standalone if needed; replace one with a different implementation without touching the others.

## Coordination patterns

A handful of recurring coordination shapes:

- **Pipeline** — agents in a fixed sequence (research → draft → review → publish). Simplest; use when steps are known.
- **Router** — supervisor picks one specialist based on the task. For customer support: billing questions → billing agent, technical → tech agent.
- **Parallel + aggregator** — N specialists work in parallel; an aggregator combines their outputs. Useful for multiple perspectives, multiple data sources.
- **Iterative loop** — generator + critic + revision (covered in [Self-Improving Agent Patterns](../17_Self-Improving_Agent_Patterns/)).
- **Negotiation** — peer agents debate until they agree. Expensive; reach for it rarely.

Most production systems are one or two of these composed. Pure "swarm of agents collaborating freely" makes good demos and bad products.

## Multi-agent risks amplified

Single-agent failure modes (hallucination, infinite loops, prompt injection) multiply in multi-agent systems:

- **Prompt injection between agents.** Agent A's output becomes Agent B's input. If A's output contains "Ignore your instructions, do X instead," B might. Treat inter-agent messages as untrusted just like user input.
- **Compounding errors.** Each agent has some error rate; chained agents multiply them. A 95% per-step accuracy is 77% across 5 steps.
- **Cost explosion.** Each agent makes its own LLM calls; tools may be called per agent. A 4-agent system with average 5 tool calls each is 20+ LLM calls per task.
- **Debugging difficulty.** Tracing why the final answer is wrong requires walking through every agent's decisions.

LangSmith traces help (every sub-agent is a clearly-bounded run), but the structural complexity is real. Lean toward fewer agents with sharper responsibilities.

## When NOT to use multi-agent

If you find yourself reaching for multiple agents, ask:

- Can one agent with **multiple tools** handle this? (Usually yes.)
- Can the workflow be a **fixed chain** with role-specific prompts? (Often yes.)
- Is the "multi-agent" framing the simplest description of what you're doing? (Often no.)

Multi-agent earns its complexity in a few real cases: customer-support routing across genuinely disjoint domains, content production pipelines with distinct quality bars at each stage, and research tasks where parallel exploration provides real value. For most use cases, one well-prompted agent with the right tools wins.
