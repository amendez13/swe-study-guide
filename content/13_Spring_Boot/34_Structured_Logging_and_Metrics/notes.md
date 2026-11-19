# Structured Logging and Metrics

Make a Spring Boot service observable with JSON logs, Prometheus metrics, and business metrics.

## Key points

- Logs explain, metrics alert, and traces locate; a shared trace id links them.
- Micrometer's Observation API turns each instrumented operation into a metric and a span.
- `logging.structured.format.console=ecs` writes JSON logs; ship them from stdout to Loki.
- `micrometer-registry-prometheus` exposes `/actuator/prometheus`; enable histograms for percentiles.
- Keep metric tags low-cardinality; put ids on spans and logs instead.

## Example

Generate a project with `-d dependencies=web,actuator,prometheus`. Add the [HiringMetrics service](#13_Spring_Boot/34_Structured_Logging_and_Metrics/concepts/custom-business-metrics) and an endpoint that calls it. Then read the metric.

```java
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
class HireController {
    private final HiringMetrics metrics;

    HireController(HiringMetrics metrics) {
        this.metrics = metrics;
    }

    @PostMapping("/api/hires")
    void hire(@RequestParam String department) {
        metrics.hired(department);
    }
}
```

```sh
curl -X POST 'http://localhost:8080/api/hires?department=sales'
curl -s http://localhost:8080/actuator/prometheus | grep employees_hired
```
