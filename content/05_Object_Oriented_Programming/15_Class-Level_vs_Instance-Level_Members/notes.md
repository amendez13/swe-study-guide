# Class-Level vs Instance-Level Members

One of the most practical OOP distinctions is whether a piece of data or behavior belongs to each object or to the class as a whole. Getting this wrong creates surprising coupling or unnecessary ceremony.

## Key Points

- **Instance members are per-object** — they vary across objects and usually hold most domain state.
- **Class members are shared** — they belong to the type itself rather than to one instance.
- **Use shared state deliberately** — shared mutable values can create subtle coupling.
- **Static helpers are fine in moderation** — they are useful when no instance state is needed.
- **Do not hide object behavior in static methods** — if logic depends on object state, it usually belongs on the instance.
- **Class-level state affects testing and concurrency** — shared values are operationally more complex.
- **Match meaning to level** — choose instance or class scope based on what the concept really represents.

## Example

```python
class Session:
    timeout_seconds = 300

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.active = True
```

`timeout_seconds` is shared by the class, while `user_id` and `active` belong to each specific `Session` instance. That split works because one is type-level configuration and the others are per-object state.
