# Reactive Programming with Project Reactor — Drills

Predict the result before running the example.

## Predict what gets saved

The method below is called once. How many rows does it save, and why?

```java
import reactor.core.publisher.Mono;

void register(BookRepository books, Book book) {
    Mono<Book> saved = books.save(book);
    saved.map(Book::title).doOnNext(t -> System.out.println("Saved " + t));
}
```

**Answer**

None. A reactive repository's `save` returns a recipe, and nothing subscribes to it, so the insert never runs and nothing is printed. Return the `Mono` to a caller that subscribes, such as a WebFlux controller, or chain it into a pipeline that is returned. See [Mono and Flux](#13_Spring_Boot/19_Reactive_Programming_with_Project_Reactor/concepts/mono-and-flux).

## Keep the order of lookups

Write a method that turns a `Flux<String>` of ISBNs into a `Flux<Book>` by calling `catalog.find(isbn)`, which returns `Mono<Book>`. The books must come out in the same order as the ISBNs. Which operator do you use, and what does `flatMap` do differently?

**Answer**

```java
Flux<Book> books(Flux<String> isbns) {
    return isbns.concatMap(catalog::find);
}
```

`concatMap` subscribes to one lookup at a time and keeps the input order. `flatMap` runs the lookups concurrently and emits each book as soon as it arrives, so it is faster but can reorder the results. `flatMapSequential` runs them concurrently and still restores the order. See [compose asynchronous calls](#13_Spring_Boot/19_Reactive_Programming_with_Project_Reactor/concepts/compose-asynchronous-calls).
