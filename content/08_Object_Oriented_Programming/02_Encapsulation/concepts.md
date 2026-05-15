## Access modifiers

Keywords that control which code can read or write a class's fields and methods. In Java there are four levels, from most restrictive to most open: `private` (same class only), package-private (same package, the default when no keyword is written), `protected` (same package plus subclasses), and `public` (everywhere).

```java
public class Order {
    private double total;          // only Order itself
    int itemCount;                 // package-private — same package
    protected String status;       // same package + subclasses
    public String getStatus() {    // everyone
        return status;
    }
}
```

The guiding rule is to start with `private` and widen access only when there is a concrete reason. Public fields almost always indicate a missing abstraction.

## Information hiding

The practice of exposing only the operations callers need and hiding the internal representation behind them. The payoff is freedom to change how the class works without breaking any code that uses it.

```java
// Clients call transfer() — they never touch the balance fields directly.
public class Account {
    private long balanceCents;

    public void transfer(Account to, long cents) {
        this.balanceCents -= cents;
        to.balanceCents   += cents;
    }
}
```

If `balanceCents` were public, every caller would depend on the fact that the balance is stored as a `long` in cents. Switching to a `BigDecimal` would break them all. With the field hidden, only `Account` needs to change.

## Getters and setters

Methods that provide controlled read and write access to private fields. A getter can compute a derived value rather than simply returning a stored field; a setter can enforce validation before allowing a change.

```java
public class Thermostat {
    private double celsius;

    public double getCelsius() {
        return celsius;
    }

    public double getFahrenheit() {       // derived — no backing field
        return celsius * 9.0 / 5.0 + 32;
    }

    public void setCelsius(double value) {
        if (value < -273.15) throw new IllegalArgumentException("Below absolute zero");
        this.celsius = value;
    }
}
```

Blindly generating a getter and setter for every field defeats the purpose of encapsulation. Only expose what callers genuinely need, and prefer behavior-rich methods (`deposit`, `withdraw`) over raw get/set when the operation has meaning in the domain.

## Interface vs. implementation

A class's interface is the set of public methods it exposes — the contract callers depend on. The implementation is the private internal logic that fulfills the contract. Encapsulation keeps the two independent so either can evolve without disturbing the other.

```java
// Interface: clients see only add() and contains()
public class WordSet {
    private List<String> words = new ArrayList<>();   // implementation detail

    public void add(String word) {
        if (!words.contains(word)) words.add(word);
    }

    public boolean contains(String word) {
        return words.contains(word);
    }
}
```

Switching the backing store from `ArrayList` to a `HashSet` changes the implementation but not the interface. No caller code breaks because no caller knew about the `List`.

## Immutability

An immutable object's state cannot change after construction. Once created, it stays the same for its entire lifetime. This makes immutable objects simpler to reason about, safe to share across threads without synchronization, and immune to aliasing bugs.

```java
public final class Money {
    private final String currency;
    private final long cents;

    public Money(String currency, long cents) {
        this.currency = currency;
        this.cents = cents;
    }

    public Money add(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException();
        return new Money(currency, cents + other.cents);   // returns a new object
    }

    public long getCents()      { return cents; }
    public String getCurrency() { return currency; }
}
```

The recipe: make the class `final` (prevent subclassing), make all fields `final` and `private`, provide no setters, and return new instances from any operation that would otherwise mutate state.

## Defensive copying

When an object stores or returns a mutable reference, an outsider can modify its internal state despite `private` fields. Defensive copying breaks that link by copying the data on the way in (constructor) and on the way out (getter).

```java
public final class Schedule {
    private final List<String> events;

    public Schedule(List<String> events) {
        this.events = new ArrayList<>(events);   // copy on the way in
    }

    public List<String> getEvents() {
        return Collections.unmodifiableList(events);  // protect on the way out
    }
}
```

Without the copy, a caller who holds a reference to the original list could add or remove entries and silently corrupt the `Schedule` object.
