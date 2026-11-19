# Configuration Properties and Dependency Management

Keep settings outside the code and bind them to typed objects. Let Boot's bill of materials choose library versions that are known to work together.

## Key points

- Group related settings in a `@ConfigurationProperties` record and register it with `@ConfigurationPropertiesScan`.
- Validate properties with `@Validated` so a bad deployment fails at startup.
- Command-line arguments override system properties, which override environment variables, which override `application.properties`.
- Properties can switch beans on and supply their constructor input.
- Inherit from `spring-boot-starter-parent` and override a managed version through its property only when you must.

## Example

Run the [typed properties example](#13_Spring_Boot/10_Configuration_Properties_and_Dependency_Management/concepts/typed-custom-properties), then change the loan period without editing the file.

```sh
./mvnw -q package -DskipTests
STUDY_LIBRARY_LOANPERIOD=21d java -jar target/study-0.0.1-SNAPSHOT.jar
```
