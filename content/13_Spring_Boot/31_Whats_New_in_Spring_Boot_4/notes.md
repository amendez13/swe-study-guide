# What's New in Spring Boot 4

Review everything that changed from Spring Boot 3, with links back to the topics that teach each feature.

## Key points

- Autoconfiguration is split into modules with matching starters; classic starters ease migration.
- Spring Framework 7 adds JSpecify null safety, `BeanRegistrar`, API versioning, HTTP service client registration, and core retry.
- Jackson 3 uses `tools.jackson` packages and immutable mappers.
- Hibernate 7, Spring Security 7, JUnit 6, Testcontainers 2, and `@MockitoBean` replace their predecessors.
- Upgrade to Boot 3.5 first, fix deprecations, then use the properties migrator and OpenRewrite.

## Example

Check an existing Boot 3 project for renamed properties. Add the migrator, start the app on Boot 4, and read the warnings it logs at startup.

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-properties-migrator</artifactId>
  <scope>runtime</scope>
</dependency>
```

```sh
./mvnw spring-boot:run 2>&1 | grep -A3 'property'
```
