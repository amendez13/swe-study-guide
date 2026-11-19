# Reactive Programming with Project Reactor

Learn the non-blocking model behind Spring WebFlux and the Reactor types that express it.

## Key points

- Blocking code holds a thread while it waits; non-blocking code frees the thread and continues in a callback.
- Reactive Streams adds backpressure: subscribers `request(n)` items, so a slow consumer sets the pace.
- `Mono` emits zero or one item and `Flux` zero to many; nothing runs until something subscribes.
- `flatMap` runs inner calls concurrently, `concatMap` keeps order, and `zip` combines independent results.
- Never block an event-loop thread; wrap unavoidable blocking calls with `subscribeOn(Schedulers.boundedElastic())`.

## Example

Generate a project with `-d dependencies=webflux`. Reactor comes with the WebFlux starter. Paste this into `StudyApplication` and run it to see items flow with a delay and an error fallback.

```java
import java.time.Duration;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import reactor.core.publisher.Flux;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }

    @Bean
    CommandLineRunner demo() {
        return args -> Flux.just("Dune", "Emma", "", "Ulysses")
                .delayElements(Duration.ofMillis(200))
                .map(t -> {
                    if (t.isEmpty()) throw new IllegalArgumentException("blank title");
                    return t.toUpperCase();
                })
                .onErrorResume(e -> Flux.just("fallback: " + e.getMessage()))
                .doOnNext(t -> System.out.println(Thread.currentThread().getName() + " " + t))
                .blockLast();
    }
}
```
