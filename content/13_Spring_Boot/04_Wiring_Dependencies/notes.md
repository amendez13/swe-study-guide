# Wiring Dependencies

Control which bean goes where: constructor injection, `@Autowired`, `@Primary`, `@Qualifier`, collections, and `ObjectProvider`.

## Key points

- Prefer constructor injection with `final` fields; one constructor needs no `@Autowired`.
- Field injection hides dependencies; setter injection suits optional ones with defaults.
- With several candidates, `@Primary` sets the default and `@Qualifier` picks one explicitly.
- `List<T>` or `Map<String, T>` injects every candidate, ordered by `@Order`.
- `ObjectProvider<T>` resolves lazily and handles missing or multiple beans.

## Example

Add the two [notifiers and OverdueService](#13_Spring_Boot/04_Wiring_Dependencies/concepts/several-candidates-primary-and-qualifier) with print statements in `send`. Start the app, then remove `@Primary` and read the startup failure that lists both candidates.

```sh
./mvnw spring-boot:run
```
