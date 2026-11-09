## Clarify the behaviors

An object-oriented design interview is asking whether you can turn a fuzzy description into a small set of types that do the work. Start with the actions the system must support and the rules that constrain them, before you name classes. A library that only checks books out is a different design from one that also reserves copies, charges fines, and notifies waitlists.

```text
Ask first:
  Who uses this, and what do they do?
  Which rules can the system refuse to break?
  What is explicitly out of this conversation?
```

## Name the core types

Read the actions and underline the nouns that own data or decisions. A type earns a name when it has state that changes, or when several actions only make sense together on that state. A one-off number or a label is usually a field, not a class. Prefer a handful of types you can draw over a taxonomy you cannot finish.

## Give each type one job

Each type should be the only place that knows how to perform its job. The checkout desk should ask a `Copy` whether it can be borrowed; it should not reach into the copy's fields and decide itself. If a method needs private details from three different types, the responsibility is in the wrong place. Say the job in one sentence. If the sentence needs "and" for two unrelated reasons, split the type.

## Show how objects collaborate

Draw the call, not only the boxes. For one concrete scenario, name who sends the message, who answers, and what comes back. Collaboration is the design: a `Loan` is created by the desk, points at a `Patron` and a `Copy`, and is the object later asked to close. If you cannot narrate that path, the class list is still a glossary.

```text
Patron asks Desk to borrow a title
  Desk finds an available Copy
  Desk opens a Loan(patron, copy, due)
  Copy remembers that it is out
```

## Prefer composition

Use a field when one object is built out of another. A `Playlist` has tracks; it is not a kind of track. Inheritance fits when the subtype really is the parent and can stand in for it without surprising the caller. Reaching for a subclass so you can reuse a few methods usually means the shared part should be a collaborator instead. Composition keeps the varying piece replaceable.

## Use an interface where the implementation varies

Name an interface for the capability callers actually need, and keep the concrete type behind it. A notifier might be email today and a queue tomorrow; the loan logic should depend on "send this reminder," not on a mail library. In an interview, one interface with two short implementations is enough to show the seam. Do not introduce an interface that has only one implementation and no stated reason to vary.

## Narrate one scenario

Pick the most important use case and walk it with the objects you defined. Mention the state before, the messages, and the state after, including the failure you were asked about (no copies left, patron over the limit). One walked scenario is more convincing than a second page of classes. If the walk needs a type you never named, add that type and say why.

## Stop before the framework

Leave out persistence, UI widgets, and generic base classes unless the interviewer asks. The design is done for this round when the core types, their jobs, and one scenario are clear, and when you have said what you would revisit if the requirements grew. Extra machinery hides the decisions the interview is trying to see.
