# WebFlux Controllers and Reactive Templates

## Create a reactive Spring Boot application

Spring WebFlux is Spring's non-blocking web framework, built on Reactor. Add `spring-boot-starter-webflux` instead of the Spring MVC starter, and Boot starts an embedded Reactor Netty server with a small pool of event-loop threads. If both starters are on the classpath, Boot picks Spring MVC, so keep only one unless you set `spring.main.web-application-type=reactive`.

The programming model looks familiar: `@RestController`, `@GetMapping`, `@RequestBody`, and validation all work. The difference is in the return types and in what the code may do. Handlers return `Mono` or `Flux`, and nothing in the request path may block. A WebFlux app pays off when it spends most of its time waiting on other services and the whole chain, down to the database driver, is non-blocking.

```sh
curl -s https://start.spring.io/starter.zip -d type=maven-project -d javaVersion=25 \
  -d dependencies=webflux,thymeleaf,validation -d groupId=com.example -d artifactId=study \
  -d name=study -d packageName=com.example.study -o study.zip
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/web/reactive.html)

## Serve data with a reactive GET

A handler that returns `Flux<Book>` lets WebFlux subscribe and write the items as they come. For `application/json`, the framework collects the flux into a JSON array before writing it. For a streaming media type such as `text/event-stream` or `application/x-ndjson`, it writes each item as soon as it is emitted, so a client sees the first rows before the last ones exist.

Return `Mono<ResponseEntity<Book>>` when the status depends on the result. `Mono.empty()` from a lookup means "not found", and `defaultIfEmpty` or `switchIfEmpty` turns that into a 404.

```java
import java.time.Duration;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
class BookController {
    private final BookStore store;

    BookController(BookStore store) {
        this.store = store;
    }

    @GetMapping("/api/books")
    Flux<Book> all() {
        return store.findAll();
    }

    @GetMapping(path = "/api/books/live", produces = MediaType.APPLICATION_NDJSON_VALUE)
    Flux<Book> live() {
        return store.findAll().delayElements(Duration.ofMillis(500));
    }

    @GetMapping("/api/books/{isbn}")
    Mono<ResponseEntity<Book>> one(@PathVariable String isbn) {
        return store.find(isbn)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webflux/controller/ann-methods/return-types.html)

## Consume data with a reactive POST

A `@RequestBody` parameter can be the plain type or a `Mono<Book>`. With `Mono<Book>`, the body is decoded only when the pipeline subscribes, so reading and saving form one non-blocking chain. `@Valid` works with both; a validation failure arrives as a `WebExchangeBindException`, which WebFlux turns into a 400 response.

Return the saved entity with a 201 and a `Location` header. A `Flux<Book>` body accepts a JSON array or a stream of objects and can save them one by one as they arrive.

```java
import jakarta.validation.Valid;
import java.net.URI;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import reactor.core.publisher.Mono;

@PostMapping("/api/books")
Mono<ResponseEntity<Book>> create(@Valid @RequestBody Mono<Book> body) {
    return body.flatMap(store::save)
            .map(b -> ResponseEntity.created(URI.create("/api/books/" + b.isbn())).body(b));
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webflux/controller/ann-methods/requestbody.html)

## Serve a reactive Thymeleaf template

WebFlux controllers can render views too. A `@Controller` method returns a view name or a `Rendering`, and model attributes may be `Mono` or `Flux`. Before rendering, WebFlux resolves each reactive attribute, so the template sees a plain list. The Thymeleaf starter detects WebFlux and configures its reactive view resolver.

For a large list, Thymeleaf can instead stream the page in chunks. Wrap the flux in `ReactiveDataDriverContextVariable` and the template is written as each batch of items arrives. Only one data-driver variable is allowed per template, and it must be iterated with `th:each`.

```java
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.reactive.result.view.Rendering;
import reactor.core.publisher.Mono;

@Controller
class BookPages {
    private final BookStore store;

    BookPages(BookStore store) {
        this.store = store;
    }

    @GetMapping("/books")
    Mono<Rendering> list() {
        return Mono.just(Rendering.view("books")
                .modelAttribute("books", store.findAll())
                .modelAttribute("count", store.findAll().count())
                .build());
    }
}
```

```html
<!-- src/main/resources/templates/books.html -->
<html xmlns:th="http://www.thymeleaf.org">
<body>
<h1><span th:text="${count}">0</span> books</h1>
<ul>
  <li th:each="book : ${books}" th:text="${book.title}">Title</li>
</ul>
</body>
</html>
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webflux-view.html#webflux-view-thymeleaf)

## Test with WebTestClient

`WebTestClient` is the reactive counterpart of `MockMvcTester`. `@WebFluxTest` starts only the WebFlux layer for the named controller and provides a client bound to it; collaborators are replaced with `@MockitoBean`. Assertions chain on the response: status, headers, and the body as JSON or as decoded objects.

For streaming endpoints, read the body as a `Flux` and check it with Reactor's `StepVerifier`, which subscribes, asserts each signal in order, and fails on unexpected items. Changed in Boot 4: the WebFlux test support lives in `spring-boot-starter-webflux-test`.

```java
import static org.mockito.BDDMockito.given;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webflux.test.autoconfigure.WebFluxTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.reactive.server.WebTestClient;
import reactor.core.publisher.Mono;

@WebFluxTest(BookController.class)
class BookControllerTests {
    @Autowired
    WebTestClient client;

    @MockitoBean
    BookStore store;

    @Test
    void missingBookIs404() {
        given(store.find("x")).willReturn(Mono.empty());
        client.get().uri("/api/books/x").exchange().expectStatus().isNotFound();
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.spring-webflux-tests)

## Create hypermedia reactively

Hypermedia responses carry links that tell the client what it can do next, such as a book's own URL and its author's. Spring HATEOAS supports WebFlux with `WebFluxLinkBuilder`. Building a link may need request data such as the host and context path, so the builder returns a `Mono<Link>` instead of a link.

Combine the link with the entity in the pipeline and return an `EntityModel`. Add `spring-boot-starter-hateoas`; it produces HAL JSON by default, with links under `_links`.

```java
import static org.springframework.hateoas.server.reactive.WebFluxLinkBuilder.linkTo;
import static org.springframework.hateoas.server.reactive.WebFluxLinkBuilder.methodOn;

import org.springframework.hateoas.EntityModel;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import reactor.core.publisher.Mono;

@GetMapping("/api/hal/books/{isbn}")
Mono<EntityModel<Book>> hal(@PathVariable String isbn) {
    Mono<org.springframework.hateoas.Link> self =
            linkTo(methodOn(BookHalController.class).hal(isbn)).withSelfRel().toMono();
    return Mono.zip(store.find(isbn), self, EntityModel::of);
}
```

[Spring HATEOAS docs](https://docs.spring.io/spring-hateoas/docs/current/reference/html/#server.link-builder.webflux)
