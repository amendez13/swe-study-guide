# Human-in-the-Loop

The mechanism that turns an autonomous agent into a supervised one. Pause, inspect, approve or edit, resume — with the full state preserved across an arbitrary wait.

## Key Points

- **Three HITL patterns** — approve/reject, edit-and-resume, provide-missing-input.
- **`interrupt_before` / `interrupt_after`** — static breakpoints at compile time.
- **`update_state`** — edit checkpointed state before resuming.
- **`interrupt()`** — dynamic mid-node pause; returns the resume value when the graph picks back up.
- **`Command(resume=...)`** — pass the human's decision back to the paused node.
- **Time travel** — rewind to any checkpoint; useful for debugging and branching.
- **Production approvals** need notification, auth, audit trail, timeout policy on top of the graph primitives.
- **Streaming + interrupts** compose — stream until the pause, surface to user, resume.
- **HITL vs deterministic gates** — use rules when rules suffice; reserve human judgment for judgment calls.

## Example

A payment-processing graph with a dynamic interrupt for large transactions. The same code shows the static breakpoint pattern, the dynamic `interrupt()` pattern, edit-before-resume, and a clean approval API.

```python
import uuid
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    amount: float
    recipient: str
    note: str
    status: str           # "pending" | "approved" | "rejected"
    approval_log: list


# --- Nodes ---
def validate(state: State) -> dict:
    if state["amount"] <= 0:
        return {"status": "rejected", "approval_log": ["validation failed"]}
    return {"status": "pending"}


def approve_payment(state: State) -> dict:
    """Dynamic interrupt: pause only for large payments."""
    if state["amount"] > 1000:
        decision = interrupt({
            "type": "large_payment_approval",
            "amount": state["amount"],
            "recipient": state["recipient"],
            "note": state["note"],
        })
        if not decision.get("approved"):
            return {
                "status": "rejected",
                "approval_log": [f"rejected by {decision.get('approver', 'unknown')}: {decision.get('reason', '')}"],
            }
        return {
            "status": "approved",
            "approval_log": [f"approved by {decision.get('approver', 'unknown')}"],
        }
    return {
        "status": "approved",
        "approval_log": ["auto-approved (under threshold)"],
    }


def execute(state: State) -> dict:
    if state["status"] != "approved":
        return {}
    return {"approval_log": state["approval_log"] + [f"sent ${state['amount']} to {state['recipient']}"]}


# --- Graph ---
graph = StateGraph(State)
graph.add_node("validate", validate)
graph.add_node("approve", approve_payment)
graph.add_node("execute", execute)
graph.add_edge(START, "validate")
graph.add_edge("validate", "approve")
graph.add_edge("approve", "execute")
graph.add_edge("execute", END)

app = graph.compile(checkpointer=MemorySaver())


# --- Approval workflow API ---
def submit_payment(amount: float, recipient: str, note: str) -> tuple[str, str]:
    """Submit a payment. Returns (thread_id, status).

    Status is 'approved' / 'rejected' for small payments; 'pending_approval'
    for ones that hit the interrupt.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(
        {"amount": amount, "recipient": recipient, "note": note,
         "status": "pending", "approval_log": []},
        config=config,
    )

    snapshot = app.get_state(config)
    if snapshot.interrupts:
        return thread_id, "pending_approval"
    return thread_id, result["status"]


def list_pending() -> list[dict]:
    """Walk all threads and surface the ones blocked on interrupts.

    A real implementation would query a sidecar table indexed by thread_id;
    this version is for illustration only.
    """
    return []


def resolve(thread_id: str, approved: bool, approver: str, reason: str = "") -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(
        Command(resume={"approved": approved, "approver": approver, "reason": reason}),
        config=config,
    )
    return result


if __name__ == "__main__":
    # Small payment — auto-approved
    tid, status = submit_payment(50, "alice@example.com", "lunch")
    print(f"Small payment: {status}")

    # Large payment — paused for approval
    tid, status = submit_payment(5000, "bob@example.com", "vendor invoice")
    print(f"Large payment: {status}")

    # Inspect the pending interrupt
    pending = app.get_state({"configurable": {"thread_id": tid}})
    print(f"Pending payload: {pending.interrupts[0].value}")

    # Resolve it
    final = resolve(tid, approved=True, approver="cfo@example.com")
    print(f"Final status: {final['status']}")
    print(f"Audit log:    {final['approval_log']}")
```

What's worth noticing:

- **`interrupt(payload)` is a function call** — from the node's perspective it looks ordinary, but it pauses the entire graph until `Command(resume=...)` arrives.
- **The same `thread_id` connects submission and resolution.** A web app would store the thread_id alongside the application's payment record so the approval UI can find the right interrupt.
- **The interrupt payload is structured** — `type`, `amount`, `recipient`, `note`. A UI uses `type` to render the right approval form.
- **The approval log lives in state.** That's your audit trail, automatically persisted by the checkpointer.
- **Tests are easy** — invoke, check `snapshot.interrupts`, simulate the approval with `Command(resume={...})`, assert the final state.

The pattern generalizes: any agent action with irreversible consequences gets an `if predicate: interrupt(...)` check. Below the threshold, the agent runs autonomously; above it, a human is in the loop. That's the entire safety primitive.
