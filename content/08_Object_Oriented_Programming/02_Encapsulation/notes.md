# Encapsulation

Encapsulation is about controlling access to an object's internals so that callers depend on what the object does, not on how it does it. When internal details are hidden behind a stable interface, the implementation can evolve freely and invariants stay protected.

## Key Points

- **Access modifiers** — `private`, package-private, `protected`, and `public` form a spectrum from most to least restrictive. Default to `private` and widen only when needed.
- **Information hiding** — Expose behavior, not data. Callers should never depend on field types or storage layout.
- **Getters and setters** — Useful when they add validation or compute derived values, but blindly generating them for every field is no better than making fields public.
- **Interface vs. implementation** — The public methods are the contract; the private internals can change without breaking callers.
- **Immutability** — Objects that cannot change after construction are inherently safe to share and easy to reason about.
- **Defensive copying** — Copy mutable data on the way in and protect it on the way out to prevent external code from corrupting internal state.

## Example

```java
public final class Wallet {
    private final String owner;
    private long balanceCents;

    public Wallet(String owner, long initialCents) {
        if (initialCents < 0) throw new IllegalArgumentException("Negative balance");
        this.owner = owner;
        this.balanceCents = initialCents;
    }

    public void deposit(long cents) {
        if (cents <= 0) throw new IllegalArgumentException("Must be positive");
        balanceCents += cents;
    }

    public void withdraw(long cents) {
        if (cents > balanceCents) throw new IllegalArgumentException("Insufficient funds");
        balanceCents -= cents;
    }

    public long getBalanceCents() { return balanceCents; }
    public String getOwner()      { return owner; }
}
```

All fields are private, the owner is immutable (`final`), and every mutating method validates its input before changing state. Callers use `deposit` and `withdraw` — they never touch `balanceCents` directly, so the invariant "balance is never negative" is guaranteed by the class, not by hoping every caller gets it right.
