## Mutable objects can change after creation

A mutable object is one whose observable state can change over time. Carts gain items, accounts change balance, tasks change status.

Mutability is often necessary, but it increases the amount of state and timing a reader must reason about.

## Immutable objects stay stable

An immutable object does not change after it is created. If you want a different value, you create a new object instead.

This often makes code easier to reason about because the object cannot silently change underneath another caller.

## Immutability fits value-like concepts

Money, email addresses, dates, coordinates, percentages, and identifiers are often strong candidates for immutability. They usually represent values rather than workflows.

Mutable design for these kinds of concepts often adds risk without adding much value.

## Shared mutable state is where trouble starts

If multiple parts of the system can change the same mutable object, bugs become easier to write: unexpected updates, stale assumptions, race conditions, and hidden coupling.

That does not mean "never mutate." It means mutation should be intentional and scoped.

## Passing objects means sharing more than data

When you pass an object into a method, you pass identity and behavior too, not just a copy of primitive values. If the callee mutates that object, the caller may observe those changes later.

That is why parameter passing is not just a technical detail in OOP; it affects design semantics.

## Returning objects can preserve behavior

Returning a richer object is often better than flattening everything to primitives. If a method returns `Money`, `EmailAddress`, or `OrderSummary`, the caller gets behavior and meaning along with the data.

That keeps logic closer to the concepts it belongs to.

## Prefer immutable return values when practical

Returning immutable value objects is often safer because callers can use them freely without worrying about accidental cross-object mutation.

This is one reason value objects and immutability pair so well.

## Choose mutability based on the concept

Use mutability where the domain really has evolving state. Use immutability where the concept is best treated as a stable value. The right answer depends more on the model than on ideology.
