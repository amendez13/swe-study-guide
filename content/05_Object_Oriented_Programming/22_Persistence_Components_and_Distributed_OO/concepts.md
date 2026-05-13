## Persistence changes the design

As soon as an object must outlive one process, persistence becomes part of the design whether you planned for it or not. An in-memory `Order` can assume it exists only right now; a persisted `Order` must survive reloads, restarts, schema changes, and partial failures.

That changes the questions you have to answer. How is the object identified? How is it reconstructed? What happens if the stored shape changes over time? What rules must still hold after loading it back from storage?

## Persisted objects need stable identity

A persisted entity usually needs an identity that survives process boundaries. That is why domain entities often carry explicit IDs like `order_id`, `user_id`, or `invoice_id`.

```python
class Order:
    def __init__(self, order_id: str, customer_id: str, status: str) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.status = status
```

Without stable identity, reloading the "same" object from the database becomes ambiguous. Persistence forces you to make identity concrete rather than treating it as a vague conceptual property.

## Loading an object is not the same as creating it fresh

When an object is created from user input, you usually validate and construct it from scratch. When it is loaded from storage, you are reconstructing prior state.

```python
row = {
    "order_id": "ord-1001",
    "customer_id": "cust-42",
    "status": "paid",
}

order = Order(
    order_id=row["order_id"],
    customer_id=row["customer_id"],
    status=row["status"],
)
```

That distinction matters because persistence creates a second creation path. Your model should make it clear whether the object is brand new, rehydrated from storage, or rebuilt from an external event.

## Components group objects into larger boundaries

In larger systems, classes rarely live alone. They cluster into components such as billing, inventory, notifications, auth, reporting, or scheduling. Those components become the larger units of ownership and change.

```python
# billing/
#   order.py
#   invoice.py
#   payment_gateway.py
#
# inventory/
#   stock_item.py
#   reservation.py
```

Thinking at the component level helps because many problems are not really "which class owns this?" but "which subsystem should this belong to?"

## Distributed objects are not local objects with more latency

Once a collaborator lives in another process or another machine, the call stops being an ordinary in-memory method call. Now failure, timeout, retries, serialization, network partitions, and partial success all become normal concerns.

```python
class PaymentGatewayClient:
    def charge(self, order_id: str, amount: float) -> dict:
        # Pretend this is an HTTP request to another service
        return {"order_id": order_id, "status": "charged", "amount": amount}
```

This looks like an object method, but it does not behave like one. It can fail for reasons local method calls never do.

## Remote calls should be visible in the model

If a method performs a network hop, the design should not hide that cost completely. Remote behavior affects naming, timeouts, retries, batching, error handling, and user expectations.

```python
class InventoryServiceClient:
    def reserve_items(self, order_id: str, items: list[dict]) -> dict:
        # Remote call: may timeout, retry, or fail independently
        return {"order_id": order_id, "reservation_status": "reserved"}
```

The more a remote call is disguised as an ordinary trivial getter or setter, the more likely callers are to use it carelessly. Good designs make operational cost visible enough that callers treat it with the right respect.

## Serialization flattens behavior

Persisting or transmitting an object usually means flattening it into data: rows, JSON, events, documents, or queue messages. That process strips away methods and keeps only the shape needed for storage or transport.

```python
class Order:
    def __init__(self, order_id: str, total: float) -> None:
        self.order_id = order_id
        self.total = total

    def to_record(self) -> dict:
        return {
            "order_id": self.order_id,
            "total": self.total,
        }
```

This is why rich objects and plain data structures coexist in real systems. Inside the domain you may want behavior-rich objects; at boundaries you often need flatter transport shapes.

## Boundaries protect components from each other

Strong component boundaries keep storage, transport, and domain concerns from leaking everywhere. If every domain object knows SQL details, queue-message formats, and HTTP retry semantics, the model becomes tightly coupled fast.

One practical pattern is to let a repository, gateway, or adapter deal with boundary mechanics so the domain model can stay focused on domain rules.

## Design locally, think operationally

A class can look perfectly clean in isolation and still be naive in production. The missing questions are operational: what happens when the object is saved twice, loaded with old data, retried after partial failure, or sent over the network to another service?

Good OOP in real systems means holding both views at once. Design the local object well, but also think about the persistence, component, and distributed environment that object has to survive in.
