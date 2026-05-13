# Encapsulation and Information Hiding

Encapsulation is how an object protects itself. Information hiding is how the rest of the system avoids depending on details it should not know. Together they let you change internals without breaking callers.

## Key Points

- **Controlled access** — objects should manage how their important state is read and changed.
- **Information hiding** — callers should depend on behavior, not storage details.
- **Public fields are risky** — direct mutation bypasses validation and invariants.
- **Methods are guarded entry points** — domain actions like `withdraw()` are better than raw field writes.
- **Privacy tools help, but design matters more** — `private` and `_name` conventions support a clear API; they do not replace one.
- **Expose capabilities, not representation** — let callers ask for meaning, not internal layout.
- **Encapsulation localizes change** — rule updates land in one object instead of many callers.
- **Avoid boilerplate for its own sake** — encapsulation is for protecting meaning, not for wrapping every field automatically.

## Example

```python
class EmailAddress:
    def __init__(self, value: str) -> None:
        self._value = self._normalize(value)

    def _normalize(self, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value:
            raise ValueError("invalid email")
        return value

    def value(self) -> str:
        return self._value
```

`EmailAddress` hides normalization and validation behind one clean abstraction. Callers do not need to remember trimming, lowercasing, or `@` checks because the object that owns the data owns the rule.
