# Microservices and System Decomposition

A monolith is one process until a hot path or a team that needs its own release says a piece should leave. The cut follows a business capability, and the service that decides a fact writes the row. Tiers are the layers inside a deploy. Events, discovery, a vendor adapter, and a saga are how those deploys meet without sharing a database.

## Key Points

- **Monolith or microservices** — one process is the start. A service earns its network hop when it must ship or scale on its own. The Y-axis of the scale cube is that split.
- **When to decompose** — split a hot domain, or a team that needs its own release. Pieces that always ship together stay one service. A tidier diagram is not a reason. A modular monolith keeps the boundary inside one process until a deploy or a scale limit needs a hop.
- **Service boundaries** — one business capability per service, with its own meaning of the words it uses. A database service or a validation service is a shared bottleneck. Two services that always ship together are one service.
- **Data ownership** — the owner writes the row. Callers store an id. A shared table couples the deploys through one schema.
- **Multi-tier architecture** — presentation, application, and data are layers inside a deploy. They do not decide how many services you have. A process that keeps a session or an open socket is stateful.
- **Event-driven architecture** — publish a fact and let others react when the caller can leave. A yes-or-no the response needs stays a call. The bus, the queue test, and the outbox stay in message queues. A request id on the event is how logs follow it.
- **Service discovery** — the caller reads a registry, a balancer sits on one address, or a sidecar does both the lookup and the certificate. The public gateway is the browser's front door, not that registry.
- **Third-party integration** — one adapter speaks the vendor. Time the call out. A slow vendor stays off the page once the member can leave, and the refresh can wait on a queue.
- **Saga pattern** — each local step has a compensating write, run in reverse if a later step fails. An orchestrator calls the steps, or each service reacts to the last event. A saga does not prepare-and-commit across databases.

## Example

A ceramics guild shares kilns. Shelf rows, firing weeks, and glaze batches start in one process. The holiday week saturates kiln scheduling. The clay buyer wants a Tuesday release. Piece 18 is held, week 12 is booked, and the glaze reserve then fails.

```python
def split(reason: str) -> str:
    if reason in {"hot-firing", "clay-team"}:
        return "split"
    return "keep"


def writer(table: str) -> str:
    return {"shelves": "shelf", "weeks": "firing", "batches": "glaze"}[table]


def hop(step: str) -> str:
    if step == "kiln-free":
        return "sync"
    return "event"


def undo(failed: str) -> list[str]:
    if failed == "glaze":
        return ["cancel-week", "release-shelf"]
    return []


print(
    split("hot-firing"),
    split("tidier-diagram"),
    writer("shelves"),
    hop("kiln-free"),
    hop("stage-shelves"),
    undo("glaze"),
)
# split keep shelf sync event ['cancel-week', 'release-shelf']
```

`hot-firing` leaves as its own service. A tidier diagram keeps the rest together. The shelf service is the only writer of shelf rows, and the kiln service stores `piece_id`. "Is the kiln free" stays on the request, because the page is that answer. Staging shelves after the week is saved is an event. The bus, the decision to queue, and the outbox row for that first event stay in Message Queues and Async Processing. A failed glaze reserve cancels the week and releases the shelf, in that order. One coordinator calls those steps while the guild is a single team that has to read the failure path. The clay supplier sits behind an adapter. Confirming week 12 does not call the supplier. The kiln service finds the shelf service by reading the registry, because both are code the guild ships and the path has no room for an extra hop. Callers written in several languages would use one stable address, and a balancer would pick the instance. A certificate on every hop would be a sidecar instead. The member's browser stops at the gateway.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — The Scale Cube, the Y-axis split by function. Stateless vs. Stateful Services and the Shared Session Store.
- [Load Balancing](../04_Load_Balancing/) — Load Balancing Algorithms. Server-side discovery uses a balancer and does not pick the algorithm.
- [Networking and Communication](../10_Networking_and_Communication/) — API Gateway, and WebSockets and SSE. The gateway is the browser's front door. An open socket is state in one process.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — the bus, When to Queue, and Transactional Outbox. Events and choreography ride the bus. The first event may need the outbox.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Two-Phase Commit (2PC). A saga compensates after a local commit. It does not run that protocol.
- [Observability](../25_Observability/) — Centralized Logs. Put a request id on the event and search for it there.
