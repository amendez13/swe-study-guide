# Cohesion, Coupling, and Separation of Concerns

These are the pressure gauges of object-oriented design. They tell you whether your classes hang together well internally, whether they depend too much on neighbors, and whether each concern has a reasonable place to live.

## Key Points

- **Cohesion** — how strongly the contents of a class belong to one idea.
- **Coupling** — how entangled one class is with the details of others.
- **Separation of concerns** — different kinds of work should land in different parts of the system.
- **High cohesion improves readability** — focused classes are easier to understand and name.
- **Low coupling improves replaceability** — collaborators can evolve with less breakage.
- **Mixed concerns are a warning sign** — unrelated changes landing in the same class usually means the boundary is wrong.
- **Conceptual integrity matters** — similar problems should be modeled in similar ways.
- **The goal is balanced design** — not zero coupling and not maximum fragmentation.

## Example

```python
class DiscountPolicy:
    def apply(self, total: float) -> float:
        return total * 0.9
```

This class is small, but it is cohesive: one reason to exist and one kind of change. If it also handled SQL writes and email notifications, cohesion would drop and change risk would rise.
