## Why HITL exists

Agents make mistakes. For high-stakes actions — sending email, executing trades, modifying production data, refunding a customer — the difference between a useful agent and a dangerous one is a human review step before the agent takes the action.

Human-in-the-loop (HITL) in LangGraph means **the graph pauses, a human inspects state, the human approves or edits, the graph resumes**. The full state is persisted (via a checkpointer), so the human can take an hour or a week — the graph just waits.

Three patterns dominate:

1. **Approve / reject** — "the agent wants to delete this row; OK?"
2. **Edit and resume** — "the agent drafted this email; let me fix it before sending."
3. **Provide missing input** — "the agent needs the customer's preferred date; please collect it."

## Static breakpoints with `interrupt_before` / `interrupt_after`

The simplest HITL: declare at compile time which nodes should pause execution.

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["send_email"],     # pause before send_email runs
)
```

Run the graph: it executes up to `send_email`, then returns control. The state is checkpointed. A human can call `app.get_state(config)` to see what would happen next.

To resume:

```python
# Inspect first
snapshot = app.get_state(config)
print(snapshot.values["draft"])
print(snapshot.next)        # ("send_email",) — the paused node

# Approve and resume
app.invoke(None, config=config)    # None = continue from checkpoint
```

Static breakpoints are great when "always pause before this action" is the rule. They require a checkpointer — without persistence, there's nowhere to save the paused state.

## Editing state before resume

A human can modify state before resuming with `update_state`:

```python
# The agent drafted an email; the human wants to tweak it
app.update_state(
    config,
    {"draft": "Hi Alice,\n\nHere's the updated subject line..."},
)

# Resume — send_email now sees the edited draft
app.invoke(None, config=config)
```

`update_state` writes a new checkpoint with the edited values applied via the schema's reducers. The graph picks up from there.

This is what powers "edit the agent's draft before it sends" UIs — the agent does 80% of the work, the human does final polish, the action is taken with the polished version.

## Dynamic breakpoints with `interrupt()`

Sometimes the pause condition depends on state — "only pause if this transaction is over $1000." That's a **dynamic breakpoint**: a node calls `interrupt()` to halt execution mid-run with a payload describing what it wants from the human.

```python
from langgraph.types import interrupt

def approve_payment(state):
    if state["amount"] > 1000:
        decision = interrupt({
            "question": "Approve large payment?",
            "amount": state["amount"],
            "to": state["recipient"],
        })
        if not decision["approved"]:
            return {"status": "rejected"}
    return {"status": "approved"}
```

When `interrupt()` raises, LangGraph captures the payload and pauses. The human responds via `Command(resume=...)`:

```python
from langgraph.types import Command

# First invocation — hits the interrupt
app.invoke(input, config=config)

# Get the interrupt payload, show to human, get decision
interrupts = app.get_state(config).interrupts
# show interrupts[0].value to the human...

# Resume with the human's response
app.invoke(Command(resume={"approved": True}), config=config)
```

The function call to `interrupt(payload)` returns the resume value when the graph picks back up. From the node's perspective it looks like one ordinary function call — but in reality it's split across two `.invoke()` cycles separated by an arbitrary wait.

## Time travel

Checkpointers store every step, not just the latest. Time travel = pick an earlier checkpoint and resume from it (covered in [Persistence and Checkpointers](../14_Persistence_and_Checkpointers/)).

For HITL, the usefulness is **branching**: if the agent's reasoning went down the wrong path 3 steps ago, you can rewind, optionally edit state, and let it run again from that point. The original branch is preserved as history — you didn't destroy it, you forked.

```python
history = list(app.get_state_history(config))
earlier = next(s for s in history if s.metadata["step"] == 3)

# Resume from step 3 with a corrected message
app.update_state(earlier.config, {"messages": [HumanMessage("Try X instead of Y")]})
app.invoke(None, config=earlier.config)
```

This is the killer feature for debugging agents during development: you don't have to start over to test a fix.

## Approval flows in production

A real approval workflow needs more than just the LangGraph primitives:

- **Notification** — when the graph pauses, a human needs to know. Email, Slack, in-app inbox.
- **Authentication** — verify the approver has permission for this action.
- **Audit trail** — record who approved what, when, with what payload.
- **Timeout policy** — if no human responds in 24h, default to reject (or notify a supervisor).
- **Bulk operations** — for high volume, approval UIs need to handle batches.

LangGraph gives you the pause/resume mechanism; the rest is application code around it. The checkpointer's `thread_id` is the obvious join key for an "approval queue" table.

## Streaming alongside interrupts

The HITL pattern composes with streaming. When you `astream` a graph and it hits an interrupt, the stream ends gracefully and the state is paused. After human response, a new `astream` call continues from where it stopped.

```python
async for event in app.astream(input, config, stream_mode="updates"):
    # ... stream progress ...
    pass    # the loop ends naturally when the interrupt fires

# Show interrupts to human, get decision

async for event in app.astream(Command(resume=decision), config, stream_mode="updates"):
    # ... continue streaming ...
    pass
```

This is what a polished chat UI does: stream tokens while the agent works, surface an approval card when it hits an interrupt, resume streaming after the user clicks "Approve."

## When to use HITL vs deterministic gates

Not every safety concern needs a human. The decision tree:

- **Reversible, low-stakes** — no gate; let the agent run.
- **Irreversible, high-stakes, predictable rules** — deterministic policy gate (a function that checks rules, no LLM, no human).
- **Irreversible, high-stakes, judgment calls** — HITL.
- **Catastrophic** — both: policy gate blocks the worst cases automatically, HITL covers the rest.

A deterministic gate ("never auto-refund > $500") is faster, cheaper, and more reliable than a human. Save HITL for the judgment calls where rules don't capture intent.

## HITL in tests

Testing graphs with interrupts is straightforward — drive them as a state machine:

```python
def test_payment_requires_approval(client):
    app.invoke({"amount": 5000, "recipient": "bob"}, config=config)

    snapshot = app.get_state(config)
    assert snapshot.interrupts                           # paused, as expected

    # Simulate human approval
    app.invoke(Command(resume={"approved": True}), config=config)

    final = app.get_state(config).values
    assert final["status"] == "approved"
```

Use a fresh `thread_id` per test (a `uuid4()` works) to keep tests isolated. With a `MemorySaver`, all of this is in-process and fast.
