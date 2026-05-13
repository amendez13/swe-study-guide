# Inheritance and Generalization

Inheritance is one of the most visible OOP features, but also one of the most misused. It works best when a subtype is genuinely a more specific version of a stable, meaningful parent concept and can safely honor the parent's expectations.

## Key Points

- **Inheritance models "is-a"** — the subtype should truly be a specialized version of the base type.
- **Generalization comes first** — the shared concept matters more than the language syntax.
- **Base classes should hold real shared behavior** — not just coincidental duplication.
- **Abstract classes are for incomplete shared concepts** — they define common structure without pretending to be fully instantiable.
- **Inheritance creates coupling** — subtypes inherit assumptions as well as code.
- **Reuse alone is not enough** — sharing code is a weak reason to force a hierarchy.
- **Subtypes must preserve expectations** — callers should be able to trust the parent contract.
- **Prefer shallow hierarchies** — deep trees make behavior harder to trace and reason about.

## Example

```python
class Notification:
    def send(self, message: str) -> None:
        raise NotImplementedError


class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")
```

This hierarchy works because `EmailNotification` and `SmsNotification` are both legitimate kinds of `Notification`, and callers can treat them through the shared `send()` contract.
