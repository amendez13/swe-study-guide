# Bean Scopes and Lifecycle

Know how many instances of a bean exist, how long they live, and when your setup and cleanup code runs.

## Key points

- Singleton is the default: one shared instance per context; prototype creates one per request for the bean.
- A prototype injected into a singleton is created once; use `ObjectProvider` for fresh instances.
- Singletons are shared across threads, so keep them stateless or use thread-safe types.
- `@RequestScope` and `@SessionScope` beans are injected through scoped proxies.
- `@PostConstruct` runs after injection; `@PreDestroy` runs at shutdown in reverse dependency order.

## Example

Add the [GenreCache](#13_Spring_Boot/05_Bean_Scopes_and_Lifecycle/concepts/postconstruct-and-predestroy) with a `BookRepository` bean, start the app, and stop it with Ctrl+C to see the destroy callback.

```sh
./mvnw spring-boot:run
# Press Ctrl+C: "Genre cache cleared" is printed during shutdown.
```
