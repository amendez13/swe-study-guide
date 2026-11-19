# Virtual Threads — Drills

Predict the result before running the example.

## Predict the bottleneck

An app enables virtual threads and keeps the default Hikari pool of 10 connections. Each request runs one query that takes 100 ms. About how many requests per second can it serve, and what changed compared with platform threads?

```properties
spring.threads.virtual.enabled=true
```

**Answer**

About 100 per second: 10 connections, each free 10 times per second. Virtual threads remove the thread limit, so thousands of requests can now wait at the same time, but they all wait for one of 10 connections. The pool, or the database behind it, is the limit. Raise the pool only as far as the database can serve. See [virtual threads in a Spring Boot app](#13_Spring_Boot/22_Virtual_Threads/concepts/virtual-threads-in-a-spring-boot-app).

## Find the lost error

Nightly exports sometimes fail, but the controller always returns 202 and nobody notices. Why, and how do you make the failure visible?

```java
@Async
void export(String isbn) {
    exporter.write(isbn); // sometimes throws IOException wrapped in UncheckedIOException
}

@PostMapping("/api/exports/{isbn}")
ResponseEntity<Void> start(@PathVariable String isbn) {
    try {
        exportService.export(isbn);
    } catch (RuntimeException ex) {
        return ResponseEntity.internalServerError().build();
    }
    return ResponseEntity.accepted().build();
}
```

**Answer**

`export` runs on another thread after the controller has returned, so the `catch` never sees the exception. For a `void` `@Async` method, Spring passes it to the `AsyncUncaughtExceptionHandler`, which only logs it. Return `CompletableFuture<Void>` and record failures with `whenComplete`, or register a handler through `AsyncConfigurer` that stores the failure and raises an alert. See [handle errors in concurrent tasks](#13_Spring_Boot/22_Virtual_Threads/concepts/handle-errors-in-concurrent-tasks).
