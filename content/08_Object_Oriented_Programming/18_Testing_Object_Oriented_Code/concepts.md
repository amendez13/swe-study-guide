## Unit testing

Testing individual classes and methods in isolation to verify they behave correctly. Each test creates an instance, calls a method with known inputs, and asserts the output or state change. Unit tests are the primary feedback loop for OOP code quality — they run fast and catch regressions immediately.

```java
@Test
void depositIncreasesBalance() {
    BankAccount account = new BankAccount("Alice", 100);
    account.deposit(50);
    assertEquals(150, account.getBalance());
}
```

A good unit test is independent (no shared state between tests), repeatable (same result every time), and focused (tests one behavior per method).

## Test-Driven Development (TDD)

A discipline where you write a failing test before writing the production code that makes it pass. The cycle is Red (write a test that fails), Green (write the minimum code to pass), Refactor (clean up without breaking the test).

```text
1. Red    — write test: assertEquals("fizz", fizzBuzz(3))  → fails
2. Green  — write code: if (n % 3 == 0) return "fizz"      → passes
3. Refactor — clean up, run tests again                     → still passes
```

TDD forces design to emerge from usage rather than speculation. The test acts as the first client of the class, revealing awkward interfaces before they harden.

## Test doubles (mocks, stubs, fakes)

Objects that stand in for real dependencies during testing. They let you isolate the class under test from its collaborators — a database, a web service, a file system — so failures point to the code being tested, not its environment.

```java
// Stub — returns canned data
OrderRepository stub = mock(OrderRepository.class);
when(stub.findById(1)).thenReturn(new Order(1, "pending"));

// Verify interaction — mock
NotificationService mock = mock(NotificationService.class);
orderService.complete(1);
verify(mock).send("Order 1 completed");
```

Overusing mocks can make tests brittle and tightly coupled to implementation. Mock at boundaries (I/O, external services), not between internal collaborators.

## Testability as a design signal

Classes with low coupling, dependency injection, and interface-based collaborators are easy to test. If writing a test requires setting up a complex chain of real objects, the design is likely too coupled.

```java
// Hard to test — creates its own dependency
public class ReportService {
    private final DatabaseRepo repo = new DatabaseRepo();  // concrete, no injection
}

// Easy to test — dependency is injected
public class ReportService {
    private final OrderRepository repo;
    public ReportService(OrderRepository repo) { this.repo = repo; }
}
```

Difficulty writing a test is the most reliable early warning that a class has a design problem. If you have to fight the code to test it, listen to the feedback.
