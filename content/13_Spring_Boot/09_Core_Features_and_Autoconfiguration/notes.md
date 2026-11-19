# Core Features and Autoconfiguration

Start with the [course setup](#13_Spring_Boot). This topic explains what happens between `SpringApplication.run` and a running app: the application context, the beans in it, and the autoconfiguration that fills the gaps you leave.

## Key points

- The application context creates and wires beans. `@SpringBootApplication` adds configuration, autoconfiguration, and component scanning from the main class's package.
- Define beans with stereotypes for your own classes and `@Bean` methods for objects you build in code.
- Autoconfiguration uses conditions, mostly `@ConditionalOnMissingBean`, so a bean you declare replaces Boot's default.
- Starters choose the libraries; Boot 4 has smaller, technology-specific starters and matching test starters.

## Example

Run the [backing-off example](#13_Spring_Boot/09_Core_Features_and_Autoconfiguration/concepts/autoconfiguration-backs-off) with the debug report enabled, then search the report for `JacksonAutoConfiguration`.

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--debug
curl -i http://localhost:8080/book
```
