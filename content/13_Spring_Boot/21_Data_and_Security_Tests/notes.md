# Data and Security Tests

Check queries against a database and security rules against real requests, without starting the whole application.

## Key points

- `@DataJpaTest` loads only persistence, uses an embedded database, and rolls back each test.
- Testcontainers 2 with `@ServiceConnection` runs the same tests against real PostgreSQL in Docker.
- A test-side main class with container beans gives a ready database during development.
- Import the `SecurityFilterChain` into `@WebMvcTest` and test both allowed and denied callers.
- Request post processors set users, CSRF tokens, and OIDC logins per request.
- Method security can be tested by calling the secured bean directly.

## Example

Add `spring-boot-starter-data-jpa-test`, `spring-boot-starter-security-test`, `spring-boot-testcontainers`, `testcontainers-junit-jupiter`, and `testcontainers-postgresql` with test scope. Run the [repository tests](#13_Spring_Boot/21_Data_and_Security_Tests/concepts/repository-tests-with-datajpatest) and the [Testcontainers test](#13_Spring_Boot/21_Data_and_Security_Tests/concepts/testcontainers-with-a-real-database) with Docker running.

```sh
./mvnw test -Dtest='BookRepository*Tests'
./mvnw spring-boot:test-run
```
