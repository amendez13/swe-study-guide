# Transactions Basics

## What a transaction guarantees

A transaction groups several database changes into one unit that either completes entirely or not at all. Lending a book might insert a loan, decrease the available copies, and add a fee. If the second step fails after the first succeeded, the data is inconsistent: a loan exists for a book still shown as available.

Databases give transactions four guarantees, known as ACID: atomicity (all or nothing), consistency (constraints hold), isolation (concurrent transactions do not see each other's half-done work), and durability (committed data survives a crash). Spring's job is to start, commit, and roll back transactions around your code so you do not manage connections by hand.

```sql
begin;
insert into loan (book_id, member_id) values (7, 42);
update book set available = available - 1 where id = 7;
commit;   -- or rollback; if anything failed
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/motivation.html)

## @Transactional

Annotate a public service method with `@Transactional` and Spring runs it in a transaction. The [transaction proxy](#13_Spring_Boot/39_Proxies_and_AOP/concepts/how-spring-proxies-work) begins a transaction before the method, binds the connection to the current thread so every repository call in the method uses it, and commits when the method returns. Boot configures the transaction manager for JDBC or JPA automatically.

Put transactions on service methods that form one business operation, not on controllers or individual repository calls. Spring Data repository methods are already transactional on their own, so the service-level annotation is what joins several of them into one unit. [Topic 6](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/transactions-and-change-tracking) shows how JPA uses the transaction to track entity changes.

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
class LendingService {
    private final LoanRepository loans;
    private final BookRepository books;

    LendingService(LoanRepository loans, BookRepository books) {
        this.loans = loans;
        this.books = books;
    }

    @Transactional
    void lend(long bookId, long memberId) {
        books.decrementAvailable(bookId);
        loans.save(new Loan(bookId, memberId));
        // Both changes commit together, or neither does.
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)

## When a transaction rolls back

By default, Spring rolls back when the method throws an unchecked exception (`RuntimeException` or `Error`) and commits when it returns normally or throws a checked exception. That default surprises people who use checked exceptions for business failures: the changes made before the exception are committed.

Use `rollbackFor` to roll back on checked exceptions too. Catching an exception inside the method and not rethrowing it also means the method returns normally, so the transaction commits whatever was done before the failure.

```java
import org.springframework.transaction.annotation.Transactional;

class PaymentDeclinedException extends Exception {
}

@Transactional(rollbackFor = PaymentDeclinedException.class)
void lendWithDeposit(long bookId, long memberId) throws PaymentDeclinedException {
    loans.save(new Loan(bookId, memberId));
    payments.chargeDeposit(memberId); // throws the checked exception
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)

## Read-only transactions and propagation

`@Transactional(readOnly = true)` marks a method that only reads. JPA then skips checking entities for changes at the end, and some databases and drivers optimize read-only work. A common style is `readOnly = true` on the service class and plain `@Transactional` on the methods that write.

Propagation decides what happens when a transactional method calls another. The default, `REQUIRED`, joins an existing transaction or starts one, so the whole call chain commits or rolls back together. `REQUIRES_NEW` suspends the current transaction and runs in a separate one that commits on its own, useful for an audit record that must survive a rollback. It needs a second connection, so use it sparingly.

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
class CatalogService {
    List<Book> search(String title) {
        return books.findByTitleContaining(title);
    }

    @Transactional // Overrides the class default: read-write.
    void rename(long id, String title) {
        books.findById(id).ifPresent(b -> b.setTitle(title));
    }
}

@Service
class AuditService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    void record(String event) {
        audit.save(new AuditEntry(event)); // Commits even if the caller rolls back.
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

## Common transaction pitfalls

`@Transactional` is applied by a proxy, so every [proxy limit](#13_Spring_Boot/39_Proxies_and_AOP/concepts/proxy-limits-to-remember) applies: a call from another method of the same class, a `private` method, or an object created with `new` runs without the transaction you expect. Keep transactional methods public and call them from another bean.

Keep transactions short. A transaction holds a database connection, and often row locks, until it ends. Calling a slow HTTP service or sending email inside one ties up the connection pool and blocks other writers. Do the remote call before or after the transaction, or publish an event that runs [after commit](#13_Spring_Boot/32_Beyond_the_Book/concepts/events-between-modulith-modules).

| Pitfall | Effect | Fix |
|---|---|---|
| Self-invocation | No transaction | Call through another bean |
| Checked exception | Commits partial work | `rollbackFor` |
| Exception caught and swallowed | Commits partial work | Rethrow or mark rollback |
| Remote call inside | Long-held connection and locks | Move it outside the transaction |

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
