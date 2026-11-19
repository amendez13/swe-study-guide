# Spring Data JPA Basics — Drills

Predict the result before running the example.

## Predict whether the change is saved

Both methods change the page count of a book that exists, and neither calls `save`. Which change reaches the database? Assume the methods are called from a controller.

```java
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import org.springframework.data.repository.ListCrudRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Entity
class Book {
    @Id @GeneratedValue Long id;
    int pages;
}

interface BookRepository extends ListCrudRepository<Book, Long> {
}

@Service
class PageFixer {
    private final BookRepository books;

    PageFixer(BookRepository books) {
        this.books = books;
    }

    @Transactional
    void fixInTransaction(long id) {
        books.findById(id).orElseThrow().pages = 300;
    }

    void fixWithoutTransaction(long id) {
        books.findById(id).orElseThrow().pages = 400;
    }
}
```

**Answer**

Only `fixInTransaction` saves its change. The entity stays managed until the method's transaction commits, and Hibernate flushes the dirty field. In `fixWithoutTransaction`, the repository's own transaction ends inside `findById`, so the returned entity is detached and the change is lost. See [transactions and change tracking](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/transactions-and-change-tracking).

## Stop leaking a column

A new `internalNotes` field on the entity suddenly appears in the public JSON. What change keeps it out of the API without touching the entity?

```java
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class BookApi {
    private final BookRepository books;

    BookApi(BookRepository books) {
        this.books = books;
    }

    @GetMapping("/api/books")
    List<Book> all() {
        return books.findAll();
    }
}
```

**Answer**

Return a DTO, for example a `BookView(long id, String title)` record, and map each entity to it. The response then contains only the fields the record declares. This is the pattern in [entities, DTOs, and POJOs](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/entities-dtos-and-pojos).
