# Messages and Collaboration

Objects are not interesting in isolation. They matter because one object can ask another to do the work it already owns, which keeps rules local and reduces the amount of internal detail any one caller needs to know.

## Key Points

- **Collaboration is the point** — useful systems are built from objects working together, not from isolated class definitions.
- **Messages express intent** — method calls are requests for action, not invitations to manipulate internals.
- **Tell, don't ask** — prefer `cart.add_item(product)` over reaching in and editing `cart.items` directly.
- **Responsibilities define edges** — objects should collaborate where their owned responsibilities naturally meet.
- **Avoid train wrecks** — long property/method chains often mean the caller knows too much about internal structure.
- **Keep the graph legible** — interactions are normal; uncontrolled interactions are the problem.
- **Fewer collaborators is simpler** — more dependencies widen the mental model required to understand one class.
- **The callee should own the rule** — ask the object that owns the rule to apply it.

## Example

```python
class Inventory:
    def reserve(self, product_id: str, quantity: int) -> None:
        print(f"Reserved {quantity} of {product_id}")


class Cart:
    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory
        self.items = []

    def add_item(self, product_id: str, quantity: int) -> None:
        self.inventory.reserve(product_id, quantity)
        self.items.append((product_id, quantity))
```

`Cart` does not reimplement inventory logic. It collaborates with `Inventory` through a clear message, and each object stays closer to its own responsibility.
