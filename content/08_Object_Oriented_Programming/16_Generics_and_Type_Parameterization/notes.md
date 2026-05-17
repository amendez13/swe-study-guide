# Generics and Type Parameterization

Generics let you write classes and methods that work with any type while keeping compile-time type safety. Without generics, you would either duplicate code for each type or use `Object` everywhere and cast — losing safety and readability.

## Key Points

- **Generic class** — Parameterized by type (`Box<T>`). One implementation, type-safe usage for any `T`.
- **Generic method** — Declares its own type parameter before the return type. Useful for standalone utility methods.
- **Bounded type parameters** — `<T extends X>` constrains `T` to types that support specific operations, combining generics with polymorphism.
- **Wildcards** — `?`, `? extends T`, `? super T` for flexible method signatures. PECS: Producer Extends, Consumer Super.
- **Type erasure** — Generic types exist at compile time only; at runtime they are erased. This is why `new T()` and `instanceof List<String>` are illegal.

## Example

```java
public class Pair<A, B> {
    private final A first;
    private final B second;

    public Pair(A first, B second) {
        this.first = first;
        this.second = second;
    }

    public A getFirst()  { return first; }
    public B getSecond() { return second; }

    public <C> Pair<A, C> mapSecond(java.util.function.Function<B, C> fn) {
        return new Pair<>(first, fn.apply(second));
    }

    public static void main(String[] args) {
        Pair<String, Integer> entry = new Pair<>("age", 30);
        System.out.println(entry.getFirst() + " = " + entry.getSecond());

        Pair<String, String> mapped = entry.mapSecond(Object::toString);
        System.out.println(mapped.getSecond().getClass());  // String
    }
}
```

`Pair` is generic in two types; `mapSecond` adds a third type parameter for the transformation. The compiler enforces all type relationships — no casts, no runtime surprises.
