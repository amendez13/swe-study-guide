# WebFlux Controllers and Reactive Templates — Drills

Predict the result before running the example.

## Find the blocking call

Under load, this WebFlux endpoint answers slowly and other endpoints on the same server slow down too. What is wrong, and how do you fix it?

```java
@GetMapping("/api/books/{isbn}/summary")
Mono<String> summary(@PathVariable String isbn) {
    String text = restClient.get().uri("/summaries/{isbn}", isbn).retrieve().body(String.class);
    return Mono.just(text);
}
```

**Answer**

`RestClient` blocks, and the handler runs on a Netty event-loop thread. While it waits, every connection served by that thread waits too. Use the non-blocking `WebClient` and return its `Mono`: `return webClient.get().uri("/summaries/{isbn}", isbn).retrieve().bodyToMono(String.class);`. If the call must stay blocking, wrap it in `Mono.fromCallable(...).subscribeOn(Schedulers.boundedElastic())`. See [schedulers and blocking code](#13_Spring_Boot/19_Reactive_Programming_with_Project_Reactor/concepts/schedulers-and-blocking-code).

## Stream rows to the client

Change the endpoint below so that `curl -N` prints each book as soon as it is emitted, instead of one JSON array at the end.

```java
@GetMapping("/api/books/live")
Flux<Book> live() {
    return store.findAll().delayElements(Duration.ofMillis(500));
}
```

**Answer**

Declare a streaming media type: `@GetMapping(path = "/api/books/live", produces = MediaType.APPLICATION_NDJSON_VALUE)`. With plain `application/json`, WebFlux collects the flux into one array before writing. With NDJSON, or `text/event-stream`, it writes each object on its own line as it arrives. See [serve data with a reactive GET](#13_Spring_Boot/20_WebFlux_Controllers_and_Reactive_Templates/concepts/serve-data-with-a-reactive-get).
