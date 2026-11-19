# Beyond the Book

## Modular monoliths with Spring Modulith

A modular monolith is one deployable application split into modules with clear boundaries, such as `catalog`, `loans`, and `notifications`. It keeps the simple deployment of a monolith while avoiding the tangle that grows when every class can call every other. Spring Modulith treats each direct subpackage of the application's main package as a module, and its internal subpackages as private.

A test with `ApplicationModules.of(...).verify()` fails when one module uses another module's internal types or when modules depend on each other in a cycle. Run it in CI and the architecture stays as designed. Modulith can also generate documentation diagrams of the modules and their dependencies.

```java
import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;

class ModularityTests {
    @Test
    void modulesRespectTheirBoundaries() {
        ApplicationModules.of(StudyApplication.class).verify();
    }
}
```

```text
com.example.study
├── catalog          (module; catalog.internal is private)
├── loans            (module)
└── notifications    (module)
```

[Spring Modulith docs](https://docs.spring.io/spring-modulith/reference/fundamentals.html)

## Events between Modulith modules

Modules should talk through events rather than direct calls, the in-process version of [event-driven messaging](#13_Spring_Boot/24_Event_Driven_Messaging_with_Kafka/concepts/events-and-messages). Publish a Spring application event and let other modules react with `@ApplicationModuleListener`, which runs after the publishing transaction commits, asynchronously, in its own transaction.

The Event Publication Registry stores each event with its listeners in the database and marks it complete when a listener succeeds, so a crash does not lose it; incomplete events can be resubmitted. Modulith can also externalize events to Kafka, which gives you a [transactional outbox](#13_Spring_Boot/25_Reliable_Messaging_Patterns/concepts/the-transactional-outbox) with little code.

```java
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.modulith.events.ApplicationModuleListener;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

record LoanCreated(long loanId, String email) {}

@Service
class LoanService {
    private final ApplicationEventPublisher events;

    LoanService(ApplicationEventPublisher events) {
        this.events = events;
    }

    @Transactional
    void lend(long loanId, String email) {
        // Save the loan, then publish.
        events.publishEvent(new LoanCreated(loanId, email));
    }
}

@Component
class LoanNotifications {
    @ApplicationModuleListener
    void on(LoanCreated event) {
        System.out.println("Loan confirmation to " + event.email());
    }
}
```

[Spring Modulith docs](https://docs.spring.io/spring-modulith/reference/events.html)

## Batch jobs with Spring Batch

Spring Batch processes large volumes of records in jobs: import a nightly file, recalculate fees, export a report. A job has steps; a chunk-oriented step reads items, processes them, and writes them in chunks, committing one transaction per chunk. If a job fails, a restart continues from the last committed chunk instead of starting over.

Spring Batch 6 ships with Boot 4. Its default job repository is in memory, which suits simple jobs. Configure a JDBC job repository to keep job history and restart failed runs. Boot runs jobs at startup unless `spring.batch.job.enabled=false`.

```java
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.infrastructure.item.support.ListItemReader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class FeeJobConfig {
    @Bean
    Step uppercaseTitles(JobRepository jobs) {
        return new StepBuilder("uppercaseTitles", jobs)
                .<String, String>chunk(100)
                .reader(new ListItemReader<>(java.util.List.of("dune", "emma")))
                .processor(String::toUpperCase)
                .writer(chunk -> chunk.forEach(System.out::println))
                .build();
    }

    @Bean
    Job titleJob(JobRepository jobs, Step uppercaseTitles) {
        return new JobBuilder("titleJob", jobs).start(uppercaseTitles).build();
    }
}
```

[Spring Batch docs](https://docs.spring.io/spring-batch/reference/)

## GraphQL APIs with Spring for GraphQL

GraphQL lets a client ask for exactly the fields it needs, across related objects, in one request. The server publishes a schema of types and queries. Spring for GraphQL maps the schema to annotated controllers: `@QueryMapping` handles a query field, and `@SchemaMapping` resolves a field on a type, such as a book's author.

Resolving a field per item can cause the N+1 problem: one query for the list, then one per item. `@BatchMapping` loads the field for all items in one call. Add `spring-boot-starter-graphql`, put the schema in `src/main/resources/graphql`, and enable the GraphiQL explorer in development.

```graphql
# src/main/resources/graphql/schema.graphqls
type Query {
  bookByIsbn(isbn: ID!): Book
}

type Book {
  isbn: ID!
  title: String!
  author: Author
}

type Author {
  name: String!
}
```

```java
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.SchemaMapping;
import org.springframework.stereotype.Controller;

record Book(String isbn, String title, String authorName) {}
record Author(String name) {}

@Controller
class BookGraphController {
    @QueryMapping
    Book bookByIsbn(@Argument String isbn) {
        return new Book(isbn, "Dune", "Frank Herbert");
    }

    @SchemaMapping
    Author author(Book book) {
        return new Author(book.authorName());
    }
}
```

[Spring for GraphQL docs](https://docs.spring.io/spring-graphql/reference/)

## WebSocket messaging with STOMP

HTTP is request and response; WebSocket keeps one connection open in both directions, so the server can push updates such as live availability or chat messages. Spring's WebSocket support usually runs STOMP over it, a simple messaging protocol with destinations, so controllers can handle messages like HTTP requests.

`@MessageMapping` handles messages that clients send to an application destination, and `@SendTo` broadcasts the return value to subscribers of a topic. The simple in-memory broker serves one instance; with several instances, relay to an external broker such as RabbitMQ so every client gets every message.

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.stereotype.Controller;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws");
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.setApplicationDestinationPrefixes("/app");
        registry.enableSimpleBroker("/topic");
    }
}

record Availability(String isbn, int copies) {}

@Controller
class AvailabilityController {
    @MessageMapping("/availability")
    @SendTo("/topic/availability")
    Availability update(Availability change) {
        return change;
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/websocket/stomp.html)

## Spring Cloud basics

Spring Cloud adds building blocks for systems of many services. Spring Cloud Gateway routes external requests to services and applies cross-cutting filters such as rate limiting and authentication. Spring Cloud Config serves configuration from a Git repository to every instance. Service discovery, with Eureka or the Kubernetes API, lets clients find instances by name instead of fixed URLs.

On Kubernetes, the platform already covers much of this: Services provide discovery, ConfigMaps and Secrets provide configuration, and an ingress or gateway routes traffic. Use Spring Cloud for what the platform lacks, and check that the release train matches your Boot version.

```yaml
# Spring Cloud Gateway routes (application.yaml of the gateway app)
spring:
  cloud:
    gateway:
      server:
        webflux:
          routes:
            - id: catalog
              uri: http://catalog:8080
              predicates:
                - Path=/api/books/**
```

[Spring Cloud docs](https://spring.io/projects/spring-cloud)

## Fast restarts with CRaC

Coordinated Restore at Checkpoint snapshots a warmed-up JVM and restores it in milliseconds. The [CRaC card in topic 18](#13_Spring_Boot/18_AOT_Cache_and_Fast_Startup/concepts/checkpoint-and-restore-with-crac) covers how Spring takes the checkpoint and the secret-handling risk. Beyond that, plan how checkpoints are built and stored: create them in CI on the same JDK build and CPU family as production, and treat the files as sensitive artifacts.

Pick CRaC only when warm startup matters more than portability, for example for services that scale from zero on demand. For most services, the [AOT cache](#13_Spring_Boot/18_AOT_Cache_and_Fast_Startup/concepts/the-java-aot-cache) gives a good share of the gain with fewer constraints.

```sh
java -XX:CRaCCheckpointTo=/opt/app/checkpoint -Dspring.context.checkpoint=onRefresh -jar app.jar
java -XX:CRaCRestoreFrom=/opt/app/checkpoint
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/integration/checkpoint-restore.html)
