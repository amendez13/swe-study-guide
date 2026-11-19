# Transactions Basics — Drills

Predict the result before running the example.

## Predict what is committed

`chargeDeposit` throws `PaymentDeclinedException`, a checked exception. After the call fails, does the `loan` row exist?

```java
@Transactional
void lendWithDeposit(long bookId, long memberId) throws PaymentDeclinedException {
    loans.save(new Loan(bookId, memberId));
    payments.chargeDeposit(memberId);
}
```

**Answer**

Yes. By default Spring rolls back only on unchecked exceptions, so the transaction commits the loan even though the method threw. Add `rollbackFor = PaymentDeclinedException.class`, or make the exception extend `RuntimeException`. See [when a transaction rolls back](#13_Spring_Boot/40_Transactions_Basics/concepts/when-a-transaction-rolls-back).

## Fix the missing transaction

The import below should be all or nothing, but when the third book fails validation, the first two stay in the database. Why, and how do you fix it?

```java
@Service
class ImportService {
    void importAll(List<Book> books) {
        saveAll(books);
    }

    @Transactional
    void saveAll(List<Book> books) {
        for (Book book : books) {
            validate(book); // throws IllegalArgumentException for an invalid book
            repository.save(book);
        }
    }
}
```

**Answer**

The controller calls `importAll`, which has no annotation, and it calls `saveAll` on the same object, so the proxy never starts a transaction. Each `repository.save` then commits on its own. Annotate the public entry point instead, `@Transactional void importAll(...)`, or move `saveAll` into another bean and call it through that bean. See [common transaction pitfalls](#13_Spring_Boot/40_Transactions_Basics/concepts/common-transaction-pitfalls).
