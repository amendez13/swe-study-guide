# RestClient and HTTP Service Clients

## Call services with RestClient

`RestClient` is Spring's synchronous HTTP client with a fluent API. It shares the message converters of Spring MVC, so JSON bodies map to records with Jackson 3. Boot autoconfigures a `RestClient.Builder` with those converters and any customizers. Inject the builder, set a base URL, and build one client per downstream service.

On virtual threads a blocking `RestClient` call is cheap: the request's thread unmounts while it waits for the response. That makes `RestClient` the natural client for a Spring MVC app with `spring.threads.virtual.enabled=true`. Use `WebClient` only in WebFlux code. `RestTemplate` still works but receives no new features.

```java
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

record Price(String isbn, int cents) {}

@Component
class PricingClient {
    private final RestClient client;

    PricingClient(RestClient.Builder builder) {
        this.client = builder.baseUrl("http://localhost:8081").build();
    }

    Price price(String isbn) {
        return client.get().uri("/prices/{isbn}", isbn).retrieve().body(Price.class);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html#rest-restclient)

## Handle HTTP errors and timeouts

By default `retrieve()` throws `HttpClientErrorException` for 4xx and `HttpServerErrorException` for 5xx responses. `onStatus` maps a status to your own exception, such as turning a 404 into `Optional.empty()` or a domain exception. Use `exchange` when you need full control over the response.

Every remote call needs a timeout, or a slow service holds requests forever. Boot configures the underlying HTTP client from `spring.http.clients.*` properties. Under virtual threads a stuck call does not use up a platform thread, but it still holds a database connection or a user waiting for a page.

```properties
spring.http.clients.connect-timeout=2s
spring.http.clients.read-timeout=5s
```

```java
import org.springframework.http.HttpStatusCode;

Price priceOrThrow(String isbn) {
    return client.get().uri("/prices/{isbn}", isbn)
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError, (request, response) -> {
                throw new UnknownBookException(isbn);
            })
            .body(Price.class);
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/io/rest-client.html)

## Declare an HTTP service interface

An HTTP service interface describes a remote API as a Java interface. Annotate methods with `@GetExchange`, `@PostExchange`, and the other exchange annotations, and use `@PathVariable`, `@RequestParam`, and `@RequestBody` as in a controller. Spring creates a proxy that turns each call into an HTTP request through `RestClient`.

The interface replaces hand-written client code with a declaration. It is also easy to replace in tests, because callers depend on an interface. Return types decide how much detail the caller gets: the body, a `ResponseEntity`, or `Optional`-like handling through error mapping.

```java
import java.util.List;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.GetExchange;
import org.springframework.web.service.annotation.HttpExchange;
import org.springframework.web.service.annotation.PostExchange;

record Review(String isbn, int stars, String text) {}

@HttpExchange("/reviews")
interface ReviewClient {
    @GetExchange("/{isbn}")
    List<Review> forBook(@PathVariable String isbn, @RequestParam(defaultValue = "10") int limit);

    @PostExchange
    Review add(@RequestBody Review review);
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html#rest-http-interface)

## Register HTTP service clients in Boot 4

Changed in Boot 4: you no longer build proxies by hand with `HttpServiceProxyFactory`. Spring Framework 7's `@ImportHttpServices` registers interfaces as beans in a named group, and Boot configures each group's client from properties such as the base URL and timeouts. Inject the interface wherever it is needed.

Groups let several interfaces for one service share settings. A `RestClientHttpServiceGroupConfigurer` bean can customize a group's builder in code, for example to add an authentication header or a request interceptor.

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.service.registry.ImportHttpServices;

@Configuration
@ImportHttpServices(group = "reviews", types = ReviewClient.class)
class ClientConfig {
}
```

```properties
spring.http.serviceclient.reviews.base-url=http://localhost:8082
spring.http.serviceclient.reviews.read-timeout=3s
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/io/rest-client.html#io.rest-client.httpservice)

## Retry and limit calls with Spring Framework 7

Remote calls fail transiently: a dropped connection, a 503 during a deployment. Changed in Spring Framework 7: retry and concurrency limits are part of the core framework. `@Retryable` retries a method with a back-off, and `@ConcurrencyLimit` caps how many calls run at once. Enable both with `@EnableResilientMethods`. Boot 3 apps needed the separate Spring Retry project.

Retry only idempotent operations, such as GETs, or a timed-out POST may create a second record. `@ConcurrencyLimit` is a natural partner of virtual threads: with no thread pool to bound concurrency, it stops thousands of virtual threads from flooding a small downstream service.

```java
import java.util.List;
import org.springframework.resilience.annotation.ConcurrencyLimit;
import org.springframework.resilience.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpServerErrorException;

@Service
class ReviewService {
    private final ReviewClient reviews;

    ReviewService(ReviewClient reviews) {
        this.reviews = reviews;
    }

    @Retryable(includes = HttpServerErrorException.class, maxRetries = 3, delay = 200, multiplier = 2)
    @ConcurrencyLimit(20)
    List<Review> reviews(String isbn) {
        return reviews.forBook(isbn, 10);
    }
}

// Add @EnableResilientMethods to a configuration class.
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/resilience.html)
