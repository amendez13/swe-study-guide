# UML and Visual Modeling

UML is valuable when it helps you think more clearly about object structure, workflow, and lifecycle. It becomes noise when the diagram is more detailed than the design decisions it is supposed to clarify.

## Key Points

- **Use UML as a thinking tool** — its value is clarity, not ceremony.
- **Class diagrams show structure** — types and relationships.
- **Sequence diagrams show interaction order** — who calls whom during a scenario.
- **State diagrams show lifecycle** — useful for status-heavy objects.
- **Visual models catch issues early** — especially missing concepts and awkward ownership.
- **Keep diagrams close to code reality** — stale diagrams are decorative, not helpful.
- **Not every task needs a diagram** — model visually when ambiguity is real.
- **Focus on design questions** — ownership, transitions, and collaboration matter more than perfect notation.

## Example

```text
Order --> LineItem (one-to-many)
Order --> PaymentGateway (uses)
Order --> ReceiptService (uses)
```

Even a small sketch like this can clarify ownership versus collaboration before you commit to a larger implementation.
