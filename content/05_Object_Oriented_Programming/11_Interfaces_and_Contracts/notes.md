# Interfaces and Contracts

Interfaces let code depend on behavior instead of concrete implementation. That makes substitution easier, reduces coupling, and gives large systems cleaner seams between responsibilities.

## Key Points

- **Interfaces are promises** — they define supported operations without fixing one implementation.
- **Depend on capabilities** — callers should ask for what they need done, not who specifically does it.
- **Substitution is the payoff** — different implementations can satisfy the same caller.
- **Prefer focused contracts** — large catch-all interfaces usually mix concerns.
- **Stable behavior matters** — good interfaces form around concepts likely to survive implementation changes.
- **Testing gets easier** — fake implementations fit naturally when code already depends on contracts.
- **Contract changes are expensive** — interface design mistakes spread quickly.
- **Do not force interfaces everywhere** — add them where boundaries and substitution actually matter.

## Example

```python
class Notifier:
    def send(self, message: str) -> None:
        raise NotImplementedError


class EmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")
```

The caller depends on the `send()` contract, not on one transport. That is the core value of an interface.
