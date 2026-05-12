# Security and Safety

The threat model that's specific to LLM applications, and the defense-in-depth posture that makes them safe in production. Layered defenses; no single fix.

## Key Points

- **Threat model** — every byte that reaches the model is a potential instruction. The system prompt is suggestive, not authoritative.
- **Prompt injection** — attacker-controlled input overrides system instructions. No foolproof defense; limit blast radius.
- **Indirect prompt injection** — malicious instructions hidden in retrieved content; harder to defend.
- **Tool sandboxing** — bound what the model can do; code execution needs real isolation (Docker, gVisor, restricted interpreters).
- **Output validation** — schema + business rules before acting; never trust model output for high-stakes decisions.
- **Secrets handling** — env vars + secret managers; redact PII before it flows into LangSmith traces.
- **Resource limits** — token budget, iteration cap, rate limits, tool timeouts, concurrent-run cap.
- **PII and data residency** — provider contracts, redaction at the boundary, document data flows.
- **Adversarial users vs adversarial content** — two distinct threat models; both common.
- **Compliance audit** — your own event log, independent of LangSmith.
- **Defense-in-depth** — limit tools, validate output, HITL for irreversibles, source allowlists, budgets, redaction, audit log, incident response.

## Example

A defensive wrapper around a refund agent. Every primitive in the chapter shows up: a deterministic policy gate, output validation, tool sandboxing via allowlisting, PII redaction before tracing, per-request budget, and HITL escalation for edge cases.

```python
import re
from typing import Literal
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
from pydantic import BaseModel, Field


# --- 1. PII redaction before anything touches the model or the trace ---
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def redact(text: str) -> str:
    """Scrub obvious PII; real code would use a proper NER scrubber."""
    text = EMAIL_RE.sub("<email>", text)
    text = CARD_RE.sub("<card>", text)
    return text


# --- 2. Tool with sandboxed inputs ---
ALLOWED_REFUND_REASONS = {"defective", "wrong_item", "late_delivery", "duplicate_charge"}


@tool
def lookup_order(order_id: str) -> dict:
    """Look up an order. order_id must match the pattern 'ORD-' + 6 digits."""
    if not re.match(r"^ORD-\d{6}$", order_id):
        return {"error": "invalid order_id format"}
    # Real code: read-only DB query
    return {"id": order_id, "total": 89.99, "status": "delivered"}


# --- 3. Structured output for the model's proposal ---
class RefundProposal(BaseModel):
    order_id: str = Field(pattern=r"^ORD-\d{6}$")
    amount: float = Field(ge=0, le=10_000)
    reason: Literal["defective", "wrong_item", "late_delivery", "duplicate_charge"]
    rationale: str


# --- 4. Deterministic policy gate ---
def policy_gate(proposal: RefundProposal, order: dict) -> tuple[bool, str]:
    """Hard rules the model can't override."""
    if proposal.amount > order["total"]:
        return False, "amount exceeds order total"
    if proposal.amount > 500:
        return False, "over threshold — needs human approval"
    if proposal.reason not in ALLOWED_REFUND_REASONS:
        return False, "reason not allowed"
    return True, "auto-approved"


# --- 5. State with budget tracking ---
class State(TypedDict):
    messages: Annotated[list, add_messages]
    order_id: str
    proposal: RefundProposal | None
    policy_decision: str | None
    tokens_used: int
    final_outcome: str | None


model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(RefundProposal)


# --- Nodes ---
def propose_refund(state: State) -> dict:
    # Budget check
    if state["tokens_used"] > 10_000:
        return {"final_outcome": "rejected: budget exceeded"}

    order = lookup_order.invoke({"order_id": state["order_id"]})
    if "error" in order:
        return {"final_outcome": f"rejected: {order['error']}"}

    # Redact user-facing content before it reaches the model
    safe_messages = [
        type(m)(content=redact(m.content)) if hasattr(m, "content") else m
        for m in state["messages"]
    ]

    proposal: RefundProposal = model.invoke([
        SystemMessage(
            "You propose refunds based on the customer's claim. "
            "Use only the four allowed reasons. Never invent order IDs — "
            "use the order_id provided in state."
        ),
        *safe_messages,
        HumanMessage(f"Order: {order}. Propose a refund."),
    ])
    return {
        "proposal": proposal,
        "tokens_used": state["tokens_used"] + 500,    # stub; real code reads usage_metadata
    }


def gate(state: State) -> dict:
    if state.get("final_outcome"):
        return {}
    order = lookup_order.invoke({"order_id": state["order_id"]})
    ok, reason = policy_gate(state["proposal"], order)
    return {"policy_decision": reason, "final_outcome": None if not ok else "auto-approved"}


def needs_approval(state: State) -> str:
    if state.get("final_outcome"):
        return END
    return "human_approval"


def human_approval(state: State) -> dict:
    decision = interrupt({
        "type": "refund_review",
        "proposal": state["proposal"].model_dump(),
        "policy_note": state["policy_decision"],
    })
    if decision.get("approved"):
        return {"final_outcome": f"approved by {decision.get('approver')}"}
    return {"final_outcome": f"rejected by {decision.get('approver')}: {decision.get('reason', '')}"}


# --- Graph ---
graph = StateGraph(State)
graph.add_node("propose", propose_refund)
graph.add_node("gate", gate)
graph.add_node("human_approval", human_approval)

graph.add_edge(START, "propose")
graph.add_edge("propose", "gate")
graph.add_conditional_edges("gate", needs_approval, {"human_approval": "human_approval", END: END})
graph.add_edge("human_approval", END)

app = graph.compile(checkpointer=MemorySaver())
```

What's worth noticing:

- **PII redaction before the model.** `redact()` runs on every message before it reaches `model.invoke()` — so traces, prompts, and downstream tool calls all see scrubbed text.
- **Tool input is validated.** `lookup_order` rejects malformed order IDs with a regex check, even though the agent's prompt also tells it the format. Defense in depth.
- **Structured output for proposals.** `RefundProposal` has `Field(pattern=...)` and `Literal[...]` so the model can't propose an "unstructured" refund. The Pydantic schema is enforced by the provider's function-calling primitive.
- **Deterministic policy gate.** `policy_gate()` is normal Python — no LLM, no judgment call. It checks the proposal against rules the model is not in charge of (amount cap, reason allowlist, order-total ceiling).
- **HITL for the edge cases.** Anything the policy doesn't auto-approve goes to a human via `interrupt()`. The agent never auto-issues a large or unusual refund.
- **Budget tracking.** `tokens_used` is a state field; the first node bails out if the budget is exceeded. Real code would update it from `response.usage_metadata`.

A real system layers on more: rate limits at the API edge, source allowlists for any RAG, an audit log table separate from the LangSmith trace, monitoring alerts on the rejection rate. The core principle stays the same: the model proposes; deterministic code and humans decide.
