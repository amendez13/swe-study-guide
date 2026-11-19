# What's New in Spring Boot 4 — Drills

Predict the result before running the example.

## Predict the missing migrations

A team upgrades from Boot 3.5 to Boot 4. The POM keeps `org.flywaydb:flyway-core` and drops nothing else. The app starts, but the new `V7__add_isbn.sql` migration never runs and Hibernate then fails validation. Why?

**Answer**

In Boot 4, Flyway's autoconfiguration lives in its own module, brought in by `spring-boot-starter-flyway`. With only the Flyway library on the classpath, nothing runs the migrations. Add the starter, or use `spring-boot-starter-classic` while migrating. See [modular jars and renamed starters](#13_Spring_Boot/31_Whats_New_in_Spring_Boot_4/concepts/modular-jars-and-renamed-starters).

## Upgrade the test class

Update this Boot 3 test so it compiles and runs on Boot 4.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class BookApiTests {
    @Autowired TestRestTemplate rest;
    @MockBean BookRepository books;

    @Test
    void listsBooks() {
        assertThat(rest.getForEntity("/api/books", String.class).getStatusCode().is2xxSuccessful()).isTrue();
    }
}
```

**Answer**

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureRestTestClient
class BookApiTests {
    @Autowired RestTestClient client;
    @MockitoBean BookRepository books;

    @Test
    void listsBooks() {
        client.get().uri("/api/books").exchange().expectStatus().isOk();
    }
}
```

`@MockBean` was removed in favor of `@MockitoBean`, and the test client is no longer provided without an annotation. Moving to `RestTestClient` is the Boot 4 style; adding `@AutoConfigureTestRestTemplate` would also keep the old client working. Add `spring-boot-starter-webmvc-test` for the test support. See [security and testing](#13_Spring_Boot/31_Whats_New_in_Spring_Boot_4/concepts/security-and-testing).
