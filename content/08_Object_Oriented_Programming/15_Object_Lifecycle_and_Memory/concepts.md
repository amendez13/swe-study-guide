## Object creation and initialization

When `new` is called in Java, several things happen in order: memory is allocated on the heap, instance fields are set to default values (0, null, false), the constructor runs to initialize them properly, and a reference to the object is returned. Understanding this sequence prevents bugs from partially-initialized objects.

```java
public class Connection {
    private final String url;
    private boolean connected;

    public Connection(String url) {
        this.url = url;            // field initialization
        this.connected = false;    // explicit default
        connect();                 // careful: calling methods in constructor
    }
}
```

Calling overridable methods inside a constructor is risky: if a subclass overrides the method, the override runs before the subclass constructor — against a half-initialized object.

## Garbage collection

The JVM automatically reclaims memory from objects that are no longer reachable — no reference in the program can reach them. This eliminates manual `free()` calls but means you need to understand what "reachable" means: if you accidentally hold a reference (in a collection, a static field, or a listener), the object won't be collected.

```java
List<byte[]> cache = new ArrayList<>();
cache.add(new byte[10_000_000]);   // held in list → reachable → not collected
cache.clear();                      // reference removed → eligible for GC
```

Memory leaks in Java are not missing `free()` calls — they are forgotten references.

## Null reference

A reference that points to nothing. Calling a method on a null reference throws `NullPointerException`, one of the most common runtime errors. Java provides several defenses: `Optional<T>` for values that may be absent, null checks at boundaries, and the null-object pattern.

```java
// Fragile
String city = user.getAddress().getCity();   // NPE if address is null

// Defensive with Optional
Optional<String> city = Optional.ofNullable(user.getAddress())
                                .map(Address::getCity);
```

The best defense is making null impossible: use `final` fields initialized in the constructor, return empty collections instead of null, and push null checks to system boundaries.

## Aliasing

When multiple references point to the same object, they are aliases. A modification through one alias is visible through all others — this is expected behavior, but it becomes a bug source when developers assume they are working with independent copies.

```java
List<String> a = new ArrayList<>(List.of("x", "y"));
List<String> b = a;        // alias, not a copy

b.add("z");
System.out.println(a);     // [x, y, z] — surprise if you expected a copy
```

Mitigations include defensive copying, `Collections.unmodifiableList()`, and immutable types.

## Autoboxing and unboxing

Java automatically converts between primitives and their wrapper objects: `int` ↔ `Integer`, `double` ↔ `Double`, etc. This is convenient when working with generic collections (which cannot hold primitives), but has pitfalls.

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);      // true  — cached range -128 to 127

Integer c = 200;
Integer d = 200;
System.out.println(c == d);      // false — outside cache, different objects
System.out.println(c.equals(d)); // true  — correct value comparison
```

Performance pitfall: autoboxing inside a tight loop creates thousands of temporary wrapper objects. Use primitive types for performance-critical numeric work.
