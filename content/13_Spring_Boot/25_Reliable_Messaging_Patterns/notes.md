# Reliable Messaging Patterns

Keep messages flowing when consumers fail: retries, dead-letter topics, idempotency, and the outbox.

## Key points

- `DefaultErrorHandler` retries in place; bound the retries and skip exceptions that can never succeed.
- `DeadLetterPublishingRecoverer` moves exhausted records to `<topic>-dlt`; monitor and replay them.
- `@RetryableTopic` retries without blocking the partition but gives up ordering.
- Idempotent consumers record processed event ids in the same transaction as the change.
- The outbox table publishes events reliably after a database commit; choose messaging only when you need its decoupling.

## Example

Make the [notifier](#13_Spring_Boot/24_Event_Driven_Messaging_with_Kafka/concepts/consume-events-with-a-kafka-listener) fail for one address, register the [dead-letter error handler](#13_Spring_Boot/25_Reliable_Messaging_Patterns/concepts/send-poison-messages-to-a-dead-letter-topic), and watch the record arrive in the DLT.

```java
@KafkaListener(topics = "employee-events", groupId = "notification-service")
void onHired(EmployeeHired event) {
    if (event.email().endsWith("@invalid")) {
        throw new IllegalStateException("mail server rejected " + event.email());
    }
    System.out.println("Welcome email to " + event.email());
}
```

```sh
curl -X POST 'http://localhost:8080/api/employees?id=8&name=Bob&email=bob@invalid'
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic employee-events-dlt --from-beginning
```
