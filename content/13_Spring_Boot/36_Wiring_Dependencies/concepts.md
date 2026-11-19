# Wiring Dependencies

## Constructor injection

Constructor injection is the recommended style. Declare dependencies as constructor parameters and store them in `final` fields. When a class has exactly one constructor, Spring uses it without any annotation. Records work too: their canonical constructor is the injection point.

The class cannot exist without its dependencies, so it is never half-built. Tests create it with `new` and fakes. A constructor with many parameters is a useful warning that the class has too many jobs.

```java
import org.springframework.stereotype.Service;

@Service
class LoanService {
    private final BookRepository books;
    private final FeePolicy fees;

    LoanService(BookRepository books, FeePolicy fees) {
        this.books = books;
        this.fees = fees;
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html#beans-constructor-injection)

## @Autowired, field and setter injection

`@Autowired` marks an injection point. It is needed on a constructor only when a class has several constructors, to tell Spring which one to use. It can also go on fields and setter methods, which Spring fills after creating the object.

Field injection is short but hides dependencies, prevents `final` fields, and forces tests to use reflection or a Spring context. Setter injection fits optional dependencies that have a sensible default. Prefer constructors for everything required; in tests, Spring's own test classes are the common place where `@Autowired` fields remain.

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
class ReminderService {
    @Autowired // Field injection: works, but hidden and hard to test without Spring.
    private MailSender mail;

    private Formatter formatter = new PlainFormatter();

    @Autowired(required = false) // Optional: keeps the default when no Formatter bean exists.
    void setFormatter(Formatter formatter) {
        this.formatter = formatter;
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)

## Several candidates: @Primary and @Qualifier

When two beans match a parameter's type, Spring cannot choose and startup fails with "expected single matching bean but found 2". `@Primary` on one definition makes it the default whenever a single bean is needed. `@Qualifier("name")` on the injection point picks a specific bean by name or qualifier, and overrides `@Primary`.

Use `@Primary` for the normal choice and `@Qualifier` for the exceptions. If the parameter name equals a bean name, Spring also uses it as a fallback match, but an explicit qualifier is clearer and survives renaming.

```java
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

interface Notifier {
    void send(String to, String text);
}

@Component
@Primary
class EmailNotifier implements Notifier {
    public void send(String to, String text) { }
}

@Component("sms")
class SmsNotifier implements Notifier {
    public void send(String to, String text) { }
}

@Service
class OverdueService {
    OverdueService(Notifier usual, @Qualifier("sms") Notifier urgent) {
        // usual is EmailNotifier, urgent is SmsNotifier
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-qualifiers.html)

## Inject every candidate

Sometimes you want all beans of a type, such as every `Notifier` or every validation rule. Inject a `List<Notifier>` and Spring passes every matching bean, ordered by `@Order` or the `Ordered` interface. A `Map<String, Notifier>` gives them keyed by bean name.

This turns a growing `if`/`switch` into a plug-in point: adding a new rule means adding a new bean, with no change to the class that uses them. Check how your class behaves when no rule is registered, because the list may then be empty.

```java
import java.util.List;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

interface LoanRule {
    void check(String member);
}

@Component @Order(1)
class NoOverdueBooksRule implements LoanRule {
    public void check(String member) { }
}

@Component @Order(2)
class LoanLimitRule implements LoanRule {
    public void check(String member) { }
}

@Service
class LoanChecker {
    private final List<LoanRule> rules;

    LoanChecker(List<LoanRule> rules) {
        this.rules = rules;
    }

    void check(String member) {
        rules.forEach(rule -> rule.check(member));
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)

## Optional and lazy dependencies with ObjectProvider

`ObjectProvider<T>` injects a handle instead of the bean. Its methods fetch the bean when you call them: `getIfAvailable()` returns null or a default when no bean exists, `getIfUnique()` returns one only when it is unambiguous, and `stream()` iterates over all candidates. Nothing is created until you ask.

Use it for optional integrations, for breaking a startup-order problem, or for getting a fresh instance of a [prototype-scoped bean](#13_Spring_Boot/37_Bean_Scopes_and_Lifecycle/concepts/singleton-and-prototype) on each call. Boot's autoconfiguration uses it widely to apply customizers only when they exist.

```java
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;

@Service
class CheckoutService {
    private final ObjectProvider<LoyaltyProgram> loyalty;

    CheckoutService(ObjectProvider<LoyaltyProgram> loyalty) {
        this.loyalty = loyalty;
    }

    int points(int fee) {
        LoyaltyProgram program = loyalty.getIfAvailable();
        return program == null ? 0 : program.points(fee);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-method-injection.html)
