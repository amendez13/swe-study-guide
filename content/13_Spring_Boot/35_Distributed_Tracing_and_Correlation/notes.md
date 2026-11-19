# Distributed Tracing and Correlation

Follow one request across services and Kafka, and jump between its traces, logs, and metrics.

## Key points

- A trace is a tree of spans sharing one trace id; sampling keeps the cost down.
- Boot 4's `spring-boot-starter-opentelemetry` exports spans over OTLP to a collector or Tempo.
- Only clients built from Boot's builders propagate `traceparent`.
- Enable Kafka template and listener observation to carry traces through topics.
- Trace ids in logs and exemplars in metrics link the three signals in Grafana.

## Example

Start the [otel-lgtm container](#13_Spring_Boot/34_Structured_Logging_and_Metrics/concepts/observability-architecture-with-spring-boot-4), add `spring-boot-starter-opentelemetry` and the [export settings](#13_Spring_Boot/35_Distributed_Tracing_and_Correlation/concepts/export-traces-to-grafana-tempo), add the [hiring metrics](#13_Spring_Boot/34_Structured_Logging_and_Metrics/concepts/custom-business-metrics) and the hiring endpoint from the previous topic's Notes tab, and send a few requests. Then open Grafana at `http://localhost:3000`, choose Explore and the Tempo data source, and search for the service.

```sh
docker compose up -d lgtm
./mvnw spring-boot:run
for i in 1 2 3; do curl -s -X POST 'http://localhost:8080/api/hires?department=sales'; done
```
