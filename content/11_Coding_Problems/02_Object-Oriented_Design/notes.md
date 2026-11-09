# Object-Oriented Design

This topic is an outline for designing a small system out loud: clarify the behaviors, name a few types, give each one a job, and walk a single scenario. The cards are the skeleton of the chapter, not a finished design catalog. Patterns and full examples come later; the point of this pass is the order of the conversation.

## Key Points

- **Clarify the behaviors** — list the actions and the rules you may not break before naming classes.
- **Name the core types** — a type owns changing state or a cluster of actions; a label is usually a field.
- **Give each type one job** — the type that holds the data should be the one asked to decide.
- **Show how objects collaborate** — narrate who calls whom for one concrete scenario.
- **Prefer composition** — "has a" is the default; inherit only when the subtype can stand in for the parent.
- **Use an interface where the implementation varies** — callers depend on the capability, not on today's concrete class.
- **Narrate one scenario** — state before, messages, state after, including one failure.
- **Stop before the framework** — skip storage and UI until someone asks, and say what you left out.

## Example

```text
Library checkout, scoped to "borrow a copy":

  Patron, Copy, Loan, Desk

  Desk.borrow(patron, title):
    copy = catalog.find_available(title)
    if copy is None: return "none available"
    if not patron.can_borrow(): return "over limit"
    return Loan.open(patron, copy)
```

The example is a sketch of the collaboration, not an implementation. The next pass should turn each type's job into fields and methods, and should add the second scenario (return a copy) only after this one is solid.
