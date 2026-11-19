# Virtual Threads

Serve many concurrent blocking requests with Java's virtual threads, without rewriting code reactively.

## Key points

- Virtual threads unmount from their carrier while blocked, so waiting is cheap; CPU-bound work does not speed up.
- Java 24 and later no longer pin carriers in `synchronized` blocks (JEP 491).
- `spring.threads.virtual.enabled=true` moves Tomcat, `@Async`, `@Scheduled`, and listener containers to virtual threads.
- Without a thread pool, bound concurrency at the resources: connection pools and `concurrency-limit`.
- Async errors surface on `join` or in the `AsyncUncaughtExceptionHandler`, never in the caller's `catch`.

## Example

Add the [ThreadInfo controller](#13_Spring_Boot/30_Virtual_Threads/concepts/virtual-threads-in-a-spring-boot-app) and call it with and without the property. The thread name changes from a Tomcat worker to a `VirtualThread`.

```sh
./mvnw spring-boot:run
curl -s http://localhost:8080/api/thread
./mvnw spring-boot:run -Dspring-boot.run.arguments=--spring.threads.virtual.enabled=true
curl -s http://localhost:8080/api/thread
```
