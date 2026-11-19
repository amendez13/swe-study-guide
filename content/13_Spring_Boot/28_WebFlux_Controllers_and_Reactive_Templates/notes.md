# WebFlux Controllers and Reactive Templates

Build HTTP endpoints and server-rendered pages with Spring WebFlux, the non-blocking web stack.

## Key points

- `spring-boot-starter-webflux` runs on Reactor Netty; with both web starters present, Boot picks Spring MVC.
- Handlers return `Mono` or `Flux`; streaming media types such as NDJSON write each item as it arrives.
- `@RequestBody Mono<T>` keeps decoding and saving in one non-blocking pipeline.
- Reactive model attributes are resolved before rendering; `ReactiveDataDriverContextVariable` streams large pages.
- Test with `@WebFluxTest`, `WebTestClient`, and `StepVerifier`; Boot 4 puts them in `spring-boot-starter-webflux-test`.

## Example

Generate a project with `-d dependencies=webflux,thymeleaf`. Add this in-memory store next to the [GET controller](#13_Spring_Boot/28_WebFlux_Controllers_and_Reactive_Templates/concepts/serve-data-with-a-reactive-get), run it, and stream the books.

```java
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

record Book(String isbn, String title) {}

@Component
class BookStore {
    private final Map<String, Book> books = new ConcurrentHashMap<>(Map.of(
            "1", new Book("1", "Dune"), "2", new Book("2", "Emma"), "3", new Book("3", "Ulysses")));

    Flux<Book> findAll() {
        return Flux.fromIterable(books.values());
    }

    Mono<Book> find(String isbn) {
        return Mono.justOrEmpty(books.get(isbn));
    }

    Mono<Book> save(Book book) {
        books.put(book.isbn(), book);
        return Mono.just(book);
    }
}
```

```sh
curl -N http://localhost:8080/api/books/live
curl -i http://localhost:8080/api/books/9
```
