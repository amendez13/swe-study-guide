# JSON APIs

## A REST controller

`@RestController` combines `@Controller` and `@ResponseBody`, so each handler's return value is written as the response body. A record or collection is written as JSON by the Jackson converter, which `spring-boot-starter-webmvc` includes. Use `@PathVariable` for an identifier in the URL and `@RequestParam` for optional filters in the query string.

Return `ResponseEntity` when the handler chooses the status code. Here a known identifier returns 200 with the book, and an unknown one returns 404 with an empty body. The [problem details card](#13_Spring_Boot/04_JSON_APIs/concepts/errors-as-problem-details) gives errors a structured body.

```java
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

record Book(long id, String title, int pages) {
}

@RestController
@RequestMapping("/api/books")
class BookApi {
    private final Map<Long, Book> books = Map.of(1L, new Book(1, "Refactoring", 448));

    @GetMapping("/{id}")
    ResponseEntity<Book> one(@PathVariable long id) {
        var book = books.get(id);
        return book == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(book);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann.html)

## Create a resource from a JSON body

`@RequestBody` reads the request body with the converter that matches `Content-Type`. For `application/json`, Jackson creates the record through its canonical constructor. Unknown properties are ignored by default, and malformed JSON results in a 400 response before the handler runs.

A creation endpoint returns 201 Created with a `Location` header for the new resource. `ServletUriComponentsBuilder` builds that URL from the current request, so it stays correct behind a different host or port. Keep request and response types separate when the client must not set some fields, such as the identifier.

```java
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

record NewBook(String title, int pages) {
}

record Book(long id, String title, int pages) {
}

@RestController
class BookApi {
    private final Map<Long, Book> books = new ConcurrentHashMap<>();
    private final AtomicLong ids = new AtomicLong();

    @PostMapping("/api/books")
    ResponseEntity<Book> create(@RequestBody NewBook input) {
        var book = new Book(ids.incrementAndGet(), input.title(), input.pages());
        books.put(book.id(), book);
        var location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(book.id()).toUri();
        return ResponseEntity.created(location).body(book);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/requestbody.html)

## Validate request records

Add Jakarta Bean Validation constraints to the record components and annotate the parameter with `@Valid`. Spring MVC validates the object after deserialization. A violation raises `MethodArgumentNotValidException`, which Spring MVC turns into a 400 response, so the handler only runs with valid input.

This needs `spring-boot-starter-validation`. Post `{"title":"","pages":0}` to see the rejection. With [problem details](#13_Spring_Boot/04_JSON_APIs/concepts/errors-as-problem-details) enabled, the body follows RFC 9457. Keep rules that need data, such as a duplicate title, in the service layer.

```java
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

record NewBook(@NotBlank String title, @Positive int pages) {
}

@RestController
class BookApi {
    @PostMapping("/api/books")
    @ResponseStatus(HttpStatus.CREATED)
    NewBook create(@Valid @RequestBody NewBook input) {
        return input;
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)

## Jackson 3 in Spring Boot 4

Boot 4 uses Jackson 3 for JSON. The library's group ID and packages moved from `com.fasterxml.jackson` to `tools.jackson`, and the main type to configure is `JsonMapper`. The annotations such as `@JsonProperty` and `@JsonIgnore` kept their `com.fasterxml.jackson.annotation` package, so most model classes compile unchanged.

Customize Boot's mapper with a `JsonMapperBuilderCustomizer` bean, which keeps Boot's defaults and `spring.jackson.*` properties, or replace it entirely with your own `JsonMapper` bean. Changed in Boot 4: `Jackson2ObjectMapperBuilderCustomizer` became `JsonMapperBuilderCustomizer`, `@JsonComponent` became `@JacksonComponent`, and `spring.jackson.read.*`/`write.*` moved under `spring.jackson.json.read`/`write`. Setting `spring.jackson.use-jackson2-defaults=true` restores Jackson 2 defaults during a migration.

```java
import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDate;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.jackson.autoconfigure.JsonMapperBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import tools.jackson.databind.SerializationFeature;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }

    @Bean
    JsonMapperBuilderCustomizer prettyJson() {
        return builder -> builder.enable(SerializationFeature.INDENT_OUTPUT);
    }
}

record Loan(@JsonProperty("book_title") String title, LocalDate due) {
}

@RestController
class LoanApi {
    @GetMapping("/api/loan")
    Loan loan() {
        return new Loan("Refactoring", LocalDate.of(2026, 12, 3));
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/features/json.html)

## Errors as problem details

RFC 9457 defines a JSON error body with `type`, `title`, `status`, `detail`, and `instance` fields. Spring represents it as `ProblemDetail`. Set `spring.mvc.problemdetails.enabled=true` to have Spring MVC's own exceptions, such as validation failures and unsupported media types, use this format with the `application/problem+json` content type.

Map your own exceptions in a `@RestControllerAdvice` class. An `@ExceptionHandler` method returns a `ProblemDetail`, and its status becomes the response status. Custom properties set with `setProperty` appear as extra JSON fields. Do not put stack traces or internal identifiers in `detail`.

```properties
spring.mvc.problemdetails.enabled=true
```

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

class BookNotFoundException extends RuntimeException {
    final long id;

    BookNotFoundException(long id) {
        super("No book with id " + id);
        this.id = id;
    }
}

@RestController
class BookApi {
    @GetMapping("/api/books/{id}")
    String one(@PathVariable long id) {
        throw new BookNotFoundException(id);
    }
}

@RestControllerAdvice
class ApiErrors {
    @ExceptionHandler
    ProblemDetail notFound(BookNotFoundException ex) {
        var problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Book not found");
        problem.setProperty("bookId", ex.id);
        return problem;
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html)
