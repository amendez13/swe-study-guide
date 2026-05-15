## Generic class

A class parameterized by one or more types. Instead of writing separate `IntList`, `StringList`, and `OrderList` classes, you write one `List<T>` that works with any type while the compiler enforces type safety — no casts needed.

```java
public class Box<T> {
    private T content;

    public void put(T item) { this.content = item; }
    public T get()          { return content; }
}

Box<String> stringBox = new Box<>();
stringBox.put("hello");
String s = stringBox.get();   // no cast — compiler knows it's String
```

## Generic method

A method that declares its own type parameters, independent of the enclosing class. Useful for utility methods that need to operate on arbitrary types.

```java
public class Collections {
    public static <T> List<T> singletonList(T item) {
        return List.of(item);
    }
}

List<Integer> nums = Collections.singletonList(42);   // T inferred as Integer
```

The type parameter `<T>` appears before the return type and is inferred from the argument.

## Bounded type parameters

Constraints on type parameters that guarantee the type supports certain operations. An upper bound (`<T extends Comparable<T>>`) says "T must implement Comparable," so you can safely call `compareTo()` inside the method.

```java
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}

int bigger = max(3, 7);         // works — Integer implements Comparable
String later = max("a", "z");   // works — String implements Comparable
```

Without the bound, the compiler would reject `a.compareTo(b)` because it can't guarantee `T` has that method.

## Wildcards

Flexible type arguments that allow methods to accept a range of parameterized types. Java provides three forms: `?` (unknown), `? extends T` (upper-bounded — read-only), and `? super T` (lower-bounded — write-only).

```java
// Upper bounded — can read T values out, but cannot add (except null)
public static double sum(List<? extends Number> nums) {
    double total = 0;
    for (Number n : nums) total += n.doubleValue();
    return total;
}

sum(List.of(1, 2, 3));       // List<Integer> accepted
sum(List.of(1.5, 2.5));      // List<Double> accepted
```

The mnemonic is PECS: Producer Extends, Consumer Super. If you read from it, use `extends`; if you write to it, use `super`.

## Type erasure

At compile time, Java verifies generic type safety. At runtime, the generic type information is erased — `List<String>` and `List<Integer>` are both just `List`. This is why you cannot do `new T()`, `instanceof List<String>`, or create a generic array.

```java
List<String> strings = new ArrayList<>();
List<Integer> ints   = new ArrayList<>();

// At runtime, both are just ArrayList — type parameter is erased
System.out.println(strings.getClass() == ints.getClass());   // true
```

Type erasure was a design choice for backwards compatibility with pre-generics Java code. The tradeoff is that certain runtime type checks are impossible.
