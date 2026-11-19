# Distributed Tracing and Correlation — Drills

Predict the result before running the example.

## Find the broken trace

In Tempo, every request to the employee service ends at its outgoing call, and the mail gateway's spans appear in a separate trace. Both services export spans. What is the likely cause?

```java
@Component
class MailGateway {
    private final RestClient client = RestClient.create("http://localhost:8090");
}
```

**Answer**

`RestClient.create` builds a client without Boot's observation setup, so it sends no `traceparent` header and the gateway starts a new trace. Inject `RestClient.Builder` and build the client from it. See [propagate context across HTTP calls](#13_Spring_Boot/27_Distributed_Tracing_and_Correlation/concepts/propagate-context-across-http-calls).

## Connect the consumer to the producer

The notification service's spans never join the employee service's trace, although both export to Tempo and use `KafkaTemplate` and `@KafkaListener`. Which settings are missing, and in which service?

**Answer**

Set `spring.kafka.template.observation-enabled=true` in the producing employee service, so it writes the trace context into record headers. Set `spring.kafka.listener.observation-enabled=true` in the consuming notification service, so it continues the trace. Both are off by default. See [propagate context through Kafka](#13_Spring_Boot/27_Distributed_Tracing_and_Correlation/concepts/propagate-context-through-kafka).
