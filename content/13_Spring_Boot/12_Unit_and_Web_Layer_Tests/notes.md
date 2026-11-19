# Unit and Web Layer Tests

Test at the cheapest level that can catch the bug: plain unit tests for logic, slices for the web contract, and a few full-application tests for wiring.

## Key points

- Boot 4 uses JUnit 6 with the same Jupiter API; each technology has a matching test starter.
- Domain logic needs no Spring context; pass in time and other inputs so tests can control them.
- `@WebMvcTest` with `MockMvcTester` and `@MockitoBean` checks routing, binding, validation, and JSON.
- Unit-test services with Mockito mocks; verify queries with a data slice instead.
- `@SpringBootTest` with `@AutoConfigureRestTestClient` runs the full app over HTTP.

## Example

Add the [web layer example](#13_Spring_Boot/12_Unit_and_Web_Layer_Tests/concepts/web-layer-tests-with-mockmvctester) to a project without the security starter, or see the next topic for security-aware tests. Run one test class, then the whole suite.

```sh
./mvnw test -Dtest=BookApiTests
./mvnw test
```
