# Spring Project Anatomy and Startup

Know what is in a Spring Boot project and what happens between `main` and the first request.

## Key points

- Spring Framework provides the container; Spring Boot adds starters, autoconfiguration, and an embedded server.
- Keep every class in the main class's package or below, or scanning misses it.
- `@SpringBootApplication` combines configuration, autoconfiguration, and component scanning.
- Startup prepares the environment, loads definitions, refreshes the context, calls runners, then publishes `ApplicationReadyEvent`.
- Startup fails fast on wiring errors, before the app takes traffic.
- Maven builds from `pom.xml` in phases; `spring-boot-starter-parent` manages versions, and the Boot plugin repackages an executable jar.
- Gradle is the task-based alternative, with `bootRun` and `bootJar`; use the wrapper (`./mvnw`, `./gradlew`) either way.

## Example

Generate the project from the [course setup](#13_Spring_Boot/09_Core_Features_and_Autoconfiguration), add the [startup configuration](#13_Spring_Boot/01_Spring_Project_Anatomy_and_Startup/concepts/run-code-at-startup), and pass an option to see it in the runner's output.

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--verbose
```
