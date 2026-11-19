# Spring Data JPA Basics

## Add Spring Data JPA

`spring-boot-starter-data-jpa` brings Hibernate as the Jakarta Persistence provider, Spring Data JPA, and transaction support. With an embedded database such as H2 on the classpath and no `spring.datasource.url`, Boot creates an in-memory database, configures the `EntityManagerFactory`, and lets Hibernate create the schema from the entities on each start.

Changed in Boot 4: the stack moves to Hibernate 7 and Jakarta Persistence 3.2, persistence autoconfiguration lives in its own modules, and `@EntityScan` moved to `org.springframework.boot.persistence.autoconfigure`. For a real database, set the URL and credentials and manage the schema with a migration tool instead of Hibernate's schema generation.

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
  <groupId>com.h2database</groupId>
  <artifactId>h2</artifactId>
  <scope>runtime</scope>
</dependency>
```

```properties
spring.jpa.show-sql=true
spring.jpa.open-in-view=false
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/data/sql.html#data.sql.jpa-and-spring-data)

## Map an entity

An entity is a class whose instances Hibernate stores as table rows. It needs `@Entity`, an `@Id`, and a no-argument constructor that Hibernate can call; make it `protected` so application code uses the real constructor. `@GeneratedValue` lets the database assign the identifier on insert. By default the table and columns take the class and field names.

Records cannot be entities, because Hibernate needs to create an empty instance and change its fields as it loads and tracks it. Use records for the [data transfer objects](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/entities-dtos-and-pojos) that leave the persistence layer.

```java
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;

@Entity
public class Book {
    @Id
    @GeneratedValue
    private Long id;

    @Column(nullable = false)
    private String title;

    private int pages;

    protected Book() {
    }

    public Book(String title, int pages) {
        this.title = title;
        this.pages = pages;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public int getPages() { return pages; }
    public void setPages(int pages) { this.pages = pages; }
}
```

[Spring Data JPA docs](https://docs.spring.io/spring-data/jpa/reference/jpa/entity-persistence.html)

## Repositories

Declare an interface that extends `ListCrudRepository<Book, Long>`, or `JpaRepository` for paging and JPA-specific methods. Spring Data finds the interface at startup and creates an implementation with `save`, `findById`, `findAll`, `count`, and `deleteById`. Each repository method runs in a transaction, read-only for queries.

This app seeds two rows at startup and lists them. `save` returns the managed entity with its generated identifier. Run it with the starter and H2 from the [setup card](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/add-spring-data-jpa).

```java
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import java.util.List;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.data.repository.ListCrudRepository;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }

    @Bean
    CommandLineRunner seed(BookRepository books) {
        return args -> {
            books.saveAll(List.of(new Book("Refactoring", 448), new Book("Release It!", 376)));
            books.findAll().forEach(book -> System.out.println(book.getId() + " " + book.getTitle()));
        };
    }
}

@Entity
class Book {
    @Id @GeneratedValue Long id;
    String title;
    int pages;

    protected Book() {
    }

    Book(String title, int pages) { this.title = title; this.pages = pages; }
    Long getId() { return id; }
    String getTitle() { return title; }
    void setPages(int pages) { this.pages = pages; }
}

interface BookRepository extends ListCrudRepository<Book, Long> {
}
```

[Spring Data JPA docs](https://docs.spring.io/spring-data/jpa/reference/repositories/core-concepts.html)

## Entities, DTOs, and POJOs

An entity represents persistent state and is tracked by the persistence context. A data transfer object (DTO) is a plain shape for crossing a boundary, such as a JSON response; a record suits it. A POJO is any ordinary Java object without framework requirements, such as a calculation helper. Keep each in its role.

Return DTOs from controllers instead of entities. The API contract then does not change when a column is added, lazy associations are not loaded by accident during serialization, and clients cannot set fields such as the owner through mass assignment. This controller maps the entity from the [repository example](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/repositories) to a view record.

```java
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

record BookView(long id, String title) {
    static BookView of(Book book) {
        return new BookView(book.getId(), book.getTitle());
    }
}

@RestController
class BookApi {
    private final BookRepository books;

    BookApi(BookRepository books) {
        this.books = books;
    }

    @GetMapping("/api/books")
    List<BookView> all() {
        return books.findAll().stream().map(BookView::of).toList();
    }
}
```

[Spring Data JPA docs](https://docs.spring.io/spring-data/jpa/reference/repositories/projections.html)

## Transactions and change tracking

Inside a transaction, an entity loaded through JPA is managed. Hibernate compares its state with the loaded snapshot at commit and writes an `UPDATE` for changed fields, so no explicit `save` call is needed. Put `@Transactional` on a service method so the load, the change, and the flush form one unit that commits or rolls back together.

`@Transactional` works through a proxy, so it applies to calls that arrive from another bean, not to a method calling another method on the same object. Throwing an unchecked exception rolls back the transaction. Use this service with the entity and repository from the [repository example](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/repositories).

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
class BookService {
    private final BookRepository books;

    BookService(BookRepository books) {
        this.books = books;
    }

    @Transactional
    void correctPages(long id, int pages) {
        var book = books.findById(id).orElseThrow();
        book.setPages(pages);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
