# Event-Driven Messaging with Kafka

## Synchronous and asynchronous communication

In synchronous communication the caller sends an HTTP request and waits for the answer. That is simple and gives an immediate result, but it couples the services in time: if the called service is slow or down, the caller is too. A chain of five synchronous calls is only as available as its weakest link.

Asynchronous messaging puts a broker in the middle. The sender publishes a message and moves on; consumers process it when they can. A consumer outage delays the work instead of failing the request, and new consumers can join without changing the sender. The price is eventual consistency and a broker to run and monitor.

```java
// Synchronous: the order fails if notifications are down.
notificationClient.sendWelcome(employee.email());

// Asynchronous: the order succeeds; notifications catch up later.
kafka.send("employee-events", employee.id(), new EmployeeHired(employee.id(), employee.email()));
```

[Spring Kafka docs](https://docs.spring.io/spring-kafka/reference/)

## Events and messages

An event records a fact that already happened, named in the past tense: `EmployeeHired`, `OrderShipped`. The producer does not know or care who reacts. A command message asks one specific receiver to do something: `SendWelcomeEmail`. Events keep services loosely coupled; commands keep a direct dependency, only over a broker.

Design events as stable, versioned contracts. Include a unique event id, the time it happened, the entity's id, and the data consumers need, so they do not have to call back for details. Adding optional fields is safe; renaming or removing fields breaks consumers that are still running the old code.

```java
import java.time.Instant;
import java.util.UUID;

record EmployeeHired(UUID eventId, Instant occurredAt, long employeeId, String name, String email) {
    static EmployeeHired of(long employeeId, String name, String email) {
        return new EmployeeHired(UUID.randomUUID(), Instant.now(), employeeId, name, email);
    }
}
```

[Spring Kafka docs](https://docs.spring.io/spring-kafka/reference/kafka/serdes.html)

## Delivery semantics

At-most-once delivery may lose a message but never repeats it. At-least-once never loses a message but may deliver it twice, for example when a consumer crashes after processing but before committing its offset. Exactly-once processing is possible inside Kafka with transactions, but any side effect outside Kafka, such as an email or a database write, still needs care.

In practice, aim for at-least-once delivery with idempotent consumers. Producers wait for all in-sync replicas (`acks=all`, the default in current Kafka clients), and consumers commit offsets only after processing. Spring Kafka's listener container commits after the listener returns, so a failed listener leaves the offset uncommitted for a retry.

| Semantics | Lost messages | Duplicates | Typical use |
|---|---|---|---|
| At most once | Possible | No | Metrics you can afford to drop |
| At least once | No | Possible | Most business events |
| Exactly once | No | No, within Kafka | Kafka-to-Kafka stream processing |

[Apache Kafka docs](https://kafka.apache.org/documentation/#semantics)

## Kafka fundamentals

Kafka stores messages in topics. Each topic is split into partitions, and each partition is an ordered, append-only log replicated across brokers. A message's key chooses its partition, so all events for one employee land in one partition and stay in order. Messages are kept for a retention period, not deleted when read, so a new consumer can replay history.

Consumers join a consumer group. Kafka assigns each partition to one consumer in the group, so the group shares the work and the partition count caps its parallelism. Each group tracks its own offsets, so a notification service and an audit service each read every event independently. Kafka 4 runs without ZooKeeper, using its built-in KRaft consensus.

```yaml
# compose.yaml
services:
  kafka:
    image: apache/kafka:4.1.0
    ports:
      - "9092:9092"
```

[Apache Kafka docs](https://kafka.apache.org/documentation/#intro_concepts_and_terms)

## Produce events with KafkaTemplate

Changed in Boot 4: add `spring-boot-starter-kafka`. Boot 3 apps added the `spring-kafka` library directly. Boot then configures a `KafkaTemplate` from `spring.kafka.*` properties. Set JSON serialization for values; Spring Kafka 4 provides Jackson 3 based serializers. A `NewTopic` bean creates the topic at startup if it does not exist.

`send` returns a `CompletableFuture<SendResult>`. The send is asynchronous, so check the result to log failures. Use the entity id as the key to keep each entity's events in order. When a service must save to its database and publish an event, publishing after the commit can lose the event if the app crashes in between; the [transactional outbox](#13_Spring_Boot/25_Reliable_Messaging_Patterns/concepts/the-transactional-outbox) closes that gap.

```properties
spring.kafka.bootstrap-servers=localhost:9092
spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JacksonJsonSerializer
```

```java
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
class EmployeeEvents {
    private final KafkaTemplate<String, EmployeeHired> kafka;

    EmployeeEvents(KafkaTemplate<String, EmployeeHired> kafka) {
        this.kafka = kafka;
    }

    void hired(EmployeeHired event) {
        kafka.send("employee-events", String.valueOf(event.employeeId()), event)
                .whenComplete((result, ex) -> {
                    if (ex != null) System.err.println("Publish failed: " + ex.getMessage());
                });
    }

    @Bean
    static NewTopic employeeEventsTopic() {
        return TopicBuilder.name("employee-events").partitions(3).replicas(1).build();
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/messaging/kafka.html)

## Consume events with a Kafka listener

A `@KafkaListener` method receives each message from its topics. Boot creates the listener container, which polls Kafka, deserializes values, calls the method, and commits offsets. The `groupId` names the consumer group; two services with different group ids each get every event.

The JSON deserializer only creates classes from trusted packages, so list yours. To run several consumer threads, set `concurrency`, up to the topic's partition count. With virtual threads enabled, listener containers use them too.

```properties
spring.kafka.consumer.value-deserializer=org.springframework.kafka.support.serializer.JacksonJsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages=com.example.study
spring.kafka.consumer.auto-offset-reset=earliest
```

```java
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
class WelcomeNotifier {
    @KafkaListener(topics = "employee-events", groupId = "notification-service", concurrency = "3")
    void onHired(EmployeeHired event) {
        System.out.println("Welcome email to " + event.email());
    }
}
```

[Spring Kafka docs](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/listener-annotation.html)
