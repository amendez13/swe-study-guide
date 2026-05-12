# Persistence, Components, and Distributed OO

Object models become more interesting and more difficult once objects must be stored, reconstructed, and coordinated across process boundaries. This is where identity, component boundaries, and remote-call costs stop being abstract concerns.

## Key Points

- **Persistence changes the game** — storage requirements introduce identity, reconstruction, and lifecycle concerns.
- **Stable identity matters** — persisted entities usually need IDs that survive reloads.
- **Components are larger boundaries** — real systems group related objects into modules and subsystems.
- **Remote is different from local** — network calls bring latency, failure, retries, and serialization.
- **Make remote cost visible** — do not pretend distributed calls are ordinary cheap method calls.
- **Serialization flattens behavior** — rich objects often become plain data at storage and transport boundaries.
- **Boundaries reduce leakage** — components help keep persistence and transport concerns contained.
- **Think operationally** — class design is only part of the story once systems become real.

## Example

```python
class Order:
    def __init__(self, order_id: str, customer_id: str, status: str) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.status = status

    def to_record(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status,
        }


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

print(order.to_record())
```

This example shows the two-way pressure persistence creates. `Order` is still a domain object with meaning, but it also needs a stable identity and a transport/storage shape. Once that object crosses storage or network boundaries, those mechanics become part of the design.
