# Spring Boot

Build web applications and HTTP APIs with Spring Boot 4, Spring Framework 7, and Java 25. The course follows the chapter order of *Learning Spring Boot 4*, fourth edition (Packt). The explanations, examples, and drills are original and use the Spring reference documentation for technical guidance. [Chapter structure](https://www.oreilly.com/library/view/learning-spring-boot/9781807427115/) · [Spring Boot documentation](https://docs.spring.io/spring-boot/) · [Spring Framework documentation](https://docs.spring.io/spring-framework/reference/)

## Run the Java examples

Install a Java 25 JDK. Generate a Maven project named `study` with the package `com.example.study`, either on [start.spring.io](https://start.spring.io) or with the command below. The examples were checked against Spring Boot 4.1.2.

```sh
curl -s https://start.spring.io/starter.zip -d type=maven-project -d javaVersion=25 \
  -d dependencies=web,thymeleaf,validation -d groupId=com.example -d artifactId=study \
  -d name=study -d packageName=com.example.study -o study.zip
unzip study.zip -d study && cd study
./mvnw spring-boot:run
```

Most Java examples are a complete replacement for `src/main/java/com/example/study/StudyApplication.java`. Keep the `package com.example.study;` line at the top and replace everything below it. An example without a `StudyApplication` class adds to the one named in its card. Test examples go in `src/test/java/com/example/study/`, and templates go in `src/main/resources/templates/`. Each topic's Notes tab names any extra starter it needs, such as Spring Data JPA or Spring Security.

The app listens on `http://localhost:8080`. Call the sample URLs with a browser or `curl`. Try each drill before reading its answer.

## Course plan

- [Part 0 · Spring fundamentals](#13_Spring_Boot/33_Spring_Project_Anatomy_and_Startup), topics 33–40: project anatomy and startup, beans and dependency injection, wiring, scopes and lifecycle, configuration values and profiles, proxies and AOP, transactions
- [Part 1 · Basics](#13_Spring_Boot/01_Core_Features_and_Autoconfiguration), chapter 1
- [Part 2 · Building an application](#13_Spring_Boot/03_Spring_MVC_Controllers_and_Templates), chapters 2–5
- [Part 3 · Releasing](#13_Spring_Boot/14_Profiles_YAML_and_Property_Overrides), chapters 6–8: configuration profiles, containers, native images and the AOT cache
- [Part 4 · Scaling](#13_Spring_Boot/19_Reactive_Programming_with_Project_Reactor), chapters 9–12: reactive web and data, virtual threads and HTTP service clients, messaging with Kafka
- [Part 5 · Observability](#13_Spring_Boot/26_Structured_Logging_and_Metrics), chapter 13: structured logs, metrics, and tracing
- [Part 6 · Spring AI](#13_Spring_Boot/28_Spring_AI_ChatClient_Prompts_and_Tools), chapter 14: ChatClient, tools, RAG, MCP, and AI security
- [Part 7 · What's new in Spring Boot 4](#13_Spring_Boot/31_Whats_New_in_Spring_Boot_4), chapter 15: every change since Boot 3 and how to migrate
- [Beyond the book](#13_Spring_Boot/32_Beyond_the_Book) · Spring Modulith, Spring Batch, GraphQL, WebSocket, Spring Cloud basics, and CRaC

New to Spring? Start with [Part 0](#13_Spring_Boot/33_Spring_Project_Anatomy_and_Startup), which covers the Spring Framework basics the book assumes. Otherwise start with [topic 1](#13_Spring_Boot/01_Core_Features_and_Autoconfiguration). The whole course, Part 0, Parts 1 to 7, and Beyond the book (topics 1–40), is available. Chapters 2 to 5, 7 to 9, and 11 to 14 are split into several topics each.

## Changes since Spring Boot 3

- Topic 1: starters follow Boot 4's smaller modules, such as `spring-boot-starter-webmvc`, and Undertow is no longer supported. [Migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Topic 4: Jackson 3 replaces Jackson 2, with `tools.jackson` packages and `JsonMapperBuilderCustomizer`. [JSON](https://docs.spring.io/spring-boot/reference/features/json.html)
- Topic 5: Spring MVC and `RestClient` support API versioning, and the APIs carry JSpecify null-safety annotations. [API versioning](https://docs.spring.io/spring-framework/reference/web/webmvc-versioning.html) · [Null safety](https://docs.spring.io/spring-framework/reference/core/null-safety.html)
- Topic 6: Spring Data JPA runs on Hibernate 7 and Jakarta Persistence 3.2. [SQL databases](https://docs.spring.io/spring-boot/reference/data/sql.html)
- Topics 8–10: Spring Security 7 requires the lambda DSL, and the OAuth client starter is `spring-boot-starter-security-oauth2-client`. [Spring Security 7](https://docs.spring.io/spring-security/reference/7.0/whats-new.html)
- Topics 12–13: JUnit 6, `@MockitoBean` instead of `@MockBean`, `RestTestClient`, per-technology test starters, and Testcontainers 2. [Testing](https://docs.spring.io/spring-boot/reference/testing/index.html)
- Topics 15–16: the embedded launch script and the classic jar loader are removed, liveness and readiness probes are on by default, and Flyway needs `spring-boot-starter-flyway`. [Migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- Topic 18: Java 25 makes the JVM AOT cache easier to create and adds method profiles. [JEP 514](https://openjdk.org/jeps/514)
- Topics 20–22: WebFlux tests use `spring-boot-starter-webflux-test`, and Boot combines several `TaskDecorator` beans. [Task execution](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html)
- Topic 23: `@ImportHttpServices` registers HTTP service clients configured under `spring.http.serviceclient.*`, and Spring Framework 7 adds `@Retryable` and `@ConcurrencyLimit` to the core. [HTTP service clients](https://docs.spring.io/spring-boot/reference/io/rest-client.html#io.rest-client.httpservice) · [Resilience](https://docs.spring.io/spring-framework/reference/core/resilience.html)
- Topics 24–25: Kafka needs `spring-boot-starter-kafka`, and Spring Kafka 4 serializes JSON with Jackson 3. [Kafka](https://docs.spring.io/spring-boot/reference/messaging/kafka.html)
- Topics 26–27: `spring-boot-starter-opentelemetry` bundles the OpenTelemetry bridge and OTLP exporters, and the AOP starter is now `spring-boot-starter-aspectj`. [Tracing](https://docs.spring.io/spring-boot/reference/actuator/tracing.html)
- Topics 28–30: Spring AI 2.0 is the line built for Spring Boot 4. [Spring AI](https://docs.spring.io/spring-ai/reference/)
