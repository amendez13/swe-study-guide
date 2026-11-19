# Transactions Basics

Make several database changes succeed or fail together with `@Transactional`, and avoid the usual traps.

## Key points

- A transaction makes a group of changes atomic, isolated, and durable.
- `@Transactional` on a public service method starts, commits, and rolls back through a proxy.
- Rollback happens on unchecked exceptions by default; use `rollbackFor` for checked ones.
- `readOnly = true` for queries; `REQUIRED` joins the caller's transaction, `REQUIRES_NEW` starts a separate one.
- Self-invocation skips the transaction; keep remote calls outside transactions.

## Example

Generate a project with `-d dependencies=web,data-jdbc,h2`. Add a `book` table and a service whose transactional method inserts two rows and then fails. Call it and count the rows: there are none.

```java
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
class DemoImport {
    private final JdbcClient jdbc;

    DemoImport(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    @Transactional
    void importTwoThenFail() {
        jdbc.sql("insert into book (title) values ('Dune')").update();
        jdbc.sql("insert into book (title) values ('Emma')").update();
        throw new IllegalStateException("third book invalid");
    }

    long count() {
        return jdbc.sql("select count(*) from book").query(Long.class).single();
    }
}
```

```sql
-- src/main/resources/schema.sql
create table book (id bigint auto_increment primary key, title varchar(200) not null);
```

Remove `@Transactional` and run it again: the two rows stay.
