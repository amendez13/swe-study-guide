# Concurrency

Placeholder notes for Java Concurrency.

## Key Points

- `Thread` and `Runnable` are the low-level primitives; prefer higher-level abstractions
- `ExecutorService` manages a thread pool; submit `Callable` tasks and get `Future` results
- `synchronized` keyword and `ReentrantLock` protect shared mutable state
- `volatile` ensures visibility of a variable across threads without full mutual exclusion

## Example

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> result = pool.submit(() -> expensiveComputation());
System.out.println(result.get()); // blocks until done
pool.shutdown();
```
