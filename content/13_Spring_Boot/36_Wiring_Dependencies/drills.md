# Wiring Dependencies — Drills

Predict the result before running the example.

## Predict the ambiguous bean

A teammate adds `PushNotifier` next to `EmailNotifier`. Neither has `@Primary`. What happens at startup, and give two fixes.

```java
@Component
class EmailNotifier implements Notifier { /* ... */ }

@Component
class PushNotifier implements Notifier { /* ... */ }

@Service
class OverdueService {
    OverdueService(Notifier notifier) { }
}
```

**Answer**

Startup fails: `OverdueService` needs one `Notifier` and two beans match. Mark the usual one `@Primary`, or name the choice at the injection point with `@Qualifier("emailNotifier")`. If the service should notify through every channel, inject `List<Notifier>` instead. See [several candidates: @Primary and @Qualifier](#13_Spring_Boot/36_Wiring_Dependencies/concepts/several-candidates-primary-and-qualifier).

## Make an integration optional

`ShelfService` should publish an event to `AuditLog` when one is configured, and work normally when no `AuditLog` bean exists. Write the constructor and the method without a null check on a field injected with `@Autowired(required = false)`.

**Answer**

```java
@Service
class ShelfService {
    private final ObjectProvider<AuditLog> audit;

    ShelfService(ObjectProvider<AuditLog> audit) {
        this.audit = audit;
    }

    void shelve(String isbn) {
        // ... shelve the book ...
        audit.ifAvailable(log -> log.record("shelved " + isbn));
    }
}
```

`ObjectProvider` resolves the bean only when it is used, and `ifAvailable` runs the action only if a bean exists. See [optional and lazy dependencies with ObjectProvider](#13_Spring_Boot/36_Wiring_Dependencies/concepts/optional-and-lazy-dependencies-with-objectprovider).
