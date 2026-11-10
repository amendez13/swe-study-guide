# Microservices and System Decomposition

An online store starts as one process: catalog, cart, orders, payments, and inventory ship together. A piece leaves when it is the hot path or a team must release it alone, and the cut follows a business capability. The service that decides a fact writes the row. Tiers are the layers inside a deploy. Events, discovery, a vendor adapter, and a saga are how those deploys meet without sharing a database. Amazon's retail site and Netflix's streaming product are the large public versions of this split. The mechanisms below are the same ones a smaller store uses.

## Key Points

- **Monolith or microservices** — one process is the start. A function call becomes a network hop when that part must ship or scale on its own. The Y-axis of the scale cube is that split.
- **When to decompose** — split a hot domain, or a team that needs its own release. Pieces that always ship together stay one service. A tidier diagram leaves the code where it is. A modular monolith keeps the boundary inside one process until a deploy or a scale limit needs a hop.
- **Service boundaries** — one business capability per service, with its own meaning of the words it uses. Catalog's "available" means listed for sale. Inventory's "available" means units on hand. A database service or a validation service is a shared bottleneck. Two services that always ship together are one service.
- **Data ownership** — the owner writes the row. Callers store an id such as `product_id`. A shared table couples the deploys through one schema. A Tuesday column rename breaks Friday's writer, because a shared table has no API version.
- **Multi-tier architecture** — presentation, application, and data are layers inside a deploy. They do not decide how many services you have. A process that keeps a session or an open order-status socket is stateful.
- **Event-driven architecture** — publish a fact and let others react when the caller can leave. A yes-or-no the response needs stays a call. The stock check stays on the request. The receipt does not. The bus, the queue test, and the outbox stay in message queues. A request id on the event is how logs follow it.
- **Service discovery** — the caller reads a registry, a balancer sits on one address, or a sidecar does both the lookup and the certificate. Eight inventory instances can become seven, and the registry can list the dead one for about 30 seconds. The public gateway is the browser's front door.
- **Third-party integration** — one adapter speaks the vendor. A carrier with an 8 second tail does not fit a 300 ms place-order budget, so the page reads the last stored quote and the refresh waits on a queue.
- **Saga pattern** — each local step has a compensating write, run in reverse if a later step fails. A declined $42 charge releases the 2 reserved units, then cancels the order. An orchestrator calls the steps, or each service reacts to the last event. A saga commits locally and then compensates. Two-phase commit prepares and then commits across databases.

## Example

Catalog search saturates the store the week before a holiday sale, and the payments team wants a Tuesday release. Order 1842 is opened, 2 units of SKU 18 are reserved, and the $42 charge is then declined.

```python
def split(reason: str) -> str:
    if reason in {"hot-catalog", "payments-team"}:
        return "split"
    return "keep"


def writer(table: str) -> str:
    return {"products": "catalog", "stock": "inventory", "charges": "payments"}[table]


def hop(step: str) -> str:
    if step == "stock-available":
        return "sync"
    return "event"


def undo(failed: str) -> list[str]:
    if failed == "charge":
        return ["release-stock", "cancel-order"]
    return []


print(
    split("hot-catalog"),
    split("tidier-diagram"),
    writer("products"),
    hop("stock-available"),
    hop("send-receipt"),
    undo("charge"),
)
# split keep catalog sync event ['release-stock', 'cancel-order']
```

`hot-catalog` leaves as its own service, because search is the CPU that slows checkout and cloning the whole store would copy the quiet admin screens onto every extra machine. A tidier diagram keeps the rest together. Catalog is the only writer of product rows, and inventory stores `product_id`. "Does the warehouse have 2 units?" stays on the request, because the page is that answer. Sending the receipt after the order is saved is an event. The bus, the decision to queue, and the outbox row for that first event stay in Message Queues and Async Processing. A declined charge releases the stock and then cancels the order. One coordinator calls those steps while the store is a single team that has to read the failure path. The shipping carrier sits behind an adapter. Placing the order does not call the carrier: the page budget is 300 ms and the carrier's slow tail is 8 seconds, so checkout reads the last quote the adapter stored. Orders finds inventory by reading the registry, because both are code the store ships and the path has no room for an extra hop. Callers written in several languages would use one stable address, and a balancer would pick the instance. A certificate on every hop would be a sidecar instead. The shopper's browser stops at the gateway.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — The Scale Cube, the Y-axis split by function. Stateless vs. Stateful Services and the Shared Session Store.
- [Load Balancing](../04_Load_Balancing/) — Load Balancing Algorithms. Server-side discovery uses a balancer and does not pick the algorithm.
- [Networking and Communication](../10_Networking_and_Communication/) — API Gateway, and WebSockets and SSE. The gateway is the browser's front door. An open socket is state in one process.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — the bus, When to Queue, and Transactional Outbox. Events and choreography ride the bus. The first event may need the outbox.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — Two-Phase Commit. A saga compensates after a local commit. The prepare-and-commit protocol stays there.
- [Observability](../25_Observability/) — Centralized Logs. Put a request id on the event and search for it there.
