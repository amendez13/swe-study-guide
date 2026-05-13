# Reusable Components and Patterns

Reusable components and patterns matter when the same design pressure shows up repeatedly. The goal is not clever abstraction for its own sake; it is reducing duplicated complexity while keeping the result understandable.

## Key Points

- **Reusable components should travel well** — clear inputs, outputs, and responsibilities matter more than generic cleverness.
- **Reuse stable concepts** — local quirks rarely make good reusable abstractions.
- **Patterns are named moves** — they provide shared vocabulary for common design shapes.
- **Strategy** — use when one behavior varies behind a stable interface.
- **Observer** — use when one object needs to notify interested listeners.
- **Facade** — use when callers need a simpler front door to a complex subsystem.
- **Singleton with caution** — global shared instances hide dependencies easily.
- **Legibility matters** — reusable code should still be easy to understand and adopt.

## Example

```python
class CsvExporter:
    def export(self, rows: list[dict]) -> str:
        return "\n".join(",".join(str(v) for v in row.values()) for row in rows)
```

This is a small reusable component because it owns one clear responsibility and can be reused without dragging in unrelated workflow logic.
