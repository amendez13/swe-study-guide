# Application Layers and Modular Organization

Most backend API maintenance pain comes from code organization, not from individual HTTP calls. This topic covers how to keep routing, business rules, and persistence concerns separated enough that the system can grow without turning every edit into a cross-cutting refactor.

## Key Points

- **Handlers should stay thin** - Let the transport layer translate requests and responses instead of holding all business logic.
- **Service layers coordinate use cases** - They are useful when workflows span multiple steps or resources.
- **Repositories isolate storage details** - Query code and persistence concerns should not leak everywhere.
- **Modular routing scales better** - Group endpoints by feature or domain as the API grows.
- **Mapping is a real design step** - Public payloads often need translation into domain intent.
- **Dependency direction matters** - Keep upper layers depending on lower layers, not the reverse.

## Example

```python
class OrderRepository:
    def save(self, order: dict) -> dict:
        return {**order, "saved": True}


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def create_order(self, customer_id: int, total: int) -> dict:
        order = {"customer_id": customer_id, "total": total, "status": "created"}
        return self.repo.save(order)


service = OrderService(OrderRepository())
print(service.create_order(customer_id=7, total=120))
```

The example is small, but the boundary is the point: one layer shapes the workflow, and a lower layer handles persistence concerns.
