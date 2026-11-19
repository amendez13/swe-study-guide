# Event-Driven Messaging with Kafka

Decouple services with events: an employee service publishes hires to Kafka and a notification service reacts.

## Key points

- Asynchronous messaging removes time coupling at the cost of eventual consistency.
- Events are past-tense facts with an id and timestamp; treat them as versioned contracts.
- Aim for at-least-once delivery with idempotent consumers.
- Keys choose partitions; order holds only within a partition, and partitions cap consumer parallelism.
- Boot 4 uses `spring-boot-starter-kafka`; `KafkaTemplate` publishes and `@KafkaListener` consumes.

## Example

Start Kafka with the [compose file](#13_Spring_Boot/24_Event_Driven_Messaging_with_Kafka/concepts/kafka-fundamentals), add `spring-boot-starter-kafka` and the producer and consumer from this topic, then publish an event from an endpoint.

```java
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
class HireController {
    private final EmployeeEvents events;

    HireController(EmployeeEvents events) {
        this.events = events;
    }

    @PostMapping("/api/employees")
    void hire(@RequestParam long id, @RequestParam String name, @RequestParam String email) {
        events.hired(EmployeeHired.of(id, name, email));
    }
}
```

```sh
docker compose up -d kafka
./mvnw spring-boot:run
curl -X POST 'http://localhost:8080/api/employees?id=7&name=Ada&email=ada@example.com'
```
