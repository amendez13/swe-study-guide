# Abstraction

Abstraction is what makes OOP readable at scale. Once classes start doing real work, you need a way for other code to use them without understanding every internal detail. That is what a good abstraction buys you: a stable, meaningful surface over changing mechanics.

## Key Points

- **Selective hiding** — abstraction hides the details callers do not need while preserving the operations they do need.
- **Domain fit** — strong abstractions reflect the real concepts of the problem space, not just implementation accidents.
- **Public API over private mechanics** — callers should work with clear methods and meanings, not internal storage details.
- **Not just renaming** — a nice class name is not enough if callers still need to know the full implementation story.
- **Right level of detail** — abstractions fail when they are too low-level or so vague that they stop being useful.
- **Leaky abstractions** — if callers constantly need to understand the internals anyway, the abstraction is weak.
- **Abstract stable concepts** — build around concepts likely to survive implementation changes, not around temporary tooling details.
- **Intent over procedure** — good abstractions let callers express what they want done instead of scripting the steps themselves.
- **Abstraction vs encapsulation** — abstraction is about what callers see; encapsulation is about what callers can touch.

## Example

```python
class PasswordResetService:
    def request_reset(self, user) -> None:
        token = self._create_token(user)
        self._store_token(user, token)
        self._send_email(user.email, token)

    def _create_token(self, user) -> str:
        return f"reset-{user.id}"

    def _store_token(self, user, token: str) -> None:
        pass

    def _send_email(self, email: str, token: str) -> None:
        pass
```

The caller sees one clear abstraction: `request_reset(user)`. It does not need to know how tokens are generated, where they are stored, or how the email is sent. Those mechanics may change later, but the caller-facing intent stays stable.
