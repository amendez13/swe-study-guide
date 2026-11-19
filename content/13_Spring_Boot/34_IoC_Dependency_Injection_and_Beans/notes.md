# IoC, Dependency Injection, and Beans

Understand the idea Spring is built on: objects declare what they need, and the container creates and connects them.

## Key points

- Inversion of control moves the choice and creation of collaborators out of the class.
- Constructor injection makes dependencies required, visible, and easy to replace in tests.
- A bean is an object the container creates and manages; an object made with `new` is not one.
- The `ApplicationContext` holds the bean definitions and instances.
- Missing, ambiguous, or circular dependencies fail at startup.

## Example

Add an interface, one implementation, and a service that needs it. Then print what the context created.

```java
import java.util.List;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;

interface BookRepository {
    List<String> titles();
}

@Repository
class InMemoryBookRepository implements BookRepository {
    public List<String> titles() {
        return List.of("Emma", "Dune");
    }
}

@Service
class BookService {
    private final BookRepository books;

    BookService(BookRepository books) {
        this.books = books;
    }

    List<String> sortedTitles() {
        return books.titles().stream().sorted().toList();
    }
}
```

In `main`, call `context.getBean(BookService.class).sortedTitles()` as in [the application context](#13_Spring_Boot/34_IoC_Dependency_Injection_and_Beans/concepts/the-application-context). Then remove `@Repository` and read the startup failure.
