# RestClient and HTTP Service Clients

Call other HTTP services from a blocking app, with declarative clients, timeouts, retries, and concurrency limits.

## Key points

- `RestClient` is the synchronous client; on virtual threads its blocking calls are cheap.
- `retrieve()` throws on 4xx and 5xx; map statuses with `onStatus` and always set timeouts.
- HTTP service interfaces declare a remote API with `@GetExchange`, `@PostExchange`, and friends.
- Boot 4 registers them with `@ImportHttpServices` and configures groups under `spring.http.serviceclient.*`.
- Spring Framework 7 adds `@Retryable` and `@ConcurrencyLimit`; retry only idempotent calls.

## Example

Run two copies of the app: one serves reviews, the other calls it through the [ReviewClient interface](#13_Spring_Boot/23_RestClient_and_HTTP_Service_Clients/concepts/declare-an-http-service-interface). Add this controller to the serving copy and start it on port 8082.

```java
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
class ReviewSource {
    @GetMapping("/reviews/{isbn}")
    List<Review> reviews(@PathVariable String isbn) {
        return List.of(new Review(isbn, 5, "Loved it"), new Review(isbn, 3, "Long"));
    }
}
```

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--server.port=8082
```

In the calling copy, register the group as shown in [register HTTP service clients in Boot 4](#13_Spring_Boot/23_RestClient_and_HTTP_Service_Clients/concepts/register-http-service-clients-in-boot-4) and expose `ReviewService.reviews` through a controller.
