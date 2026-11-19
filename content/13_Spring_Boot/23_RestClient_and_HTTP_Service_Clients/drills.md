# RestClient and HTTP Service Clients — Drills

Predict the result before running the example.

## Predict the duplicate orders

A service calls a payment API with the method below. The payment service is slow and sometimes answers after the client's 2-second read timeout. What can go wrong?

```java
@Retryable(maxRetries = 3, delay = 500)
Payment charge(ChargeRequest request) {
    return payments.charge(request); // @PostExchange("/charges")
}
```

**Answer**

The customer can be charged more than once. A timeout does not mean the request failed: the payment service may finish the first charge, and each retry sends a new one. Retry only idempotent calls, or make the call idempotent by sending an idempotency key that the payment service uses to ignore duplicates. See [retry and limit calls with Spring Framework 7](#13_Spring_Boot/23_RestClient_and_HTTP_Service_Clients/concepts/retry-and-limit-calls-with-spring-framework-7).

## Write a service interface

The inventory service has `GET /stock/{isbn}` returning `{"isbn":"1","count":3}` and `PUT /stock/{isbn}` taking the same JSON. Write an HTTP service interface for it and register it in a group named `inventory` with base URL `http://localhost:8083`.

**Answer**

```java
record Stock(String isbn, int count) {}

@HttpExchange("/stock")
interface InventoryClient {
    @GetExchange("/{isbn}")
    Stock stock(@PathVariable String isbn);

    @PutExchange("/{isbn}")
    void update(@PathVariable String isbn, @RequestBody Stock stock);
}

@Configuration
@ImportHttpServices(group = "inventory", types = InventoryClient.class)
class InventoryConfig {
}
```

```properties
spring.http.serviceclient.inventory.base-url=http://localhost:8083
```

See [register HTTP service clients in Boot 4](#13_Spring_Boot/23_RestClient_and_HTTP_Service_Clients/concepts/register-http-service-clients-in-boot-4).
