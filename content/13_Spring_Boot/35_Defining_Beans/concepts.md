# Defining Beans

## Component scanning and @Component

The simplest way to define a bean is to annotate your class with `@Component`. At startup, component scanning searches the main class's package and its subpackages for annotated classes and registers one bean definition for each. The bean's name defaults to the class name with a lowercase first letter, such as `bookService`.

Scanning suits your own classes, because you can put the annotation on them. A scanned class with one constructor needs no further annotation: the container uses that constructor and injects its parameters.

```java
import java.time.Clock;
import java.time.LocalDate;
import org.springframework.stereotype.Component;

@Component
class DueDateCalculator {
    private final Clock clock;

    DueDateCalculator(Clock clock) {
        this.clock = clock;
    }

    LocalDate dueDate() {
        return LocalDate.now(clock).plusDays(21);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html)

## Stereotype annotations

`@Service`, `@Repository`, and `@Controller` are specializations of `@Component`. They register beans the same way, and they also state the class's role, which helps readers and tools. `@RestController` is `@Controller` plus `@ResponseBody`.

A few have extra behavior. `@Repository` turns database exceptions into Spring's `DataAccessException` hierarchy when exception translation is enabled. `@Controller` classes are picked up by Spring MVC as request handlers. `@Configuration` is also a component, one that declares other beans. Choose the annotation that matches the role.

| Annotation | Role | Extra behavior |
|---|---|---|
| `@Component` | Generic bean | None |
| `@Service` | Business logic | None |
| `@Repository` | Data access | Exception translation |
| `@Controller` / `@RestController` | Web handlers | Request mapping |
| `@Configuration` | Bean definitions | `@Bean` methods |

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html#beans-stereotype-annotations)

## @Configuration and @Bean methods

You cannot annotate a class from a library, such as `java.time.Clock` or a client SDK. For those, write a `@Bean` method in a `@Configuration` class. The method creates and returns the object, and the container registers the result as a bean named after the method. Parameters of a `@Bean` method are injected like constructor parameters.

`@Bean` methods also fit when creation needs logic, such as reading settings or choosing between implementations. Keep them small: build the object and return it.

```java
import java.time.Clock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
class InfrastructureConfig {
    @Bean
    Clock clock() {
        return Clock.systemUTC();
    }

    @Bean
    RestClient isbnClient(RestClient.Builder builder) {
        return builder.baseUrl("https://isbn.example.com").build();
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/java/bean-annotation.html)

## Calls between @Bean methods

Inside a `@Configuration` class, one `@Bean` method may call another. Spring subclasses the configuration class with a proxy, so the call returns the existing singleton instead of creating a second object. That is why `@Configuration` classes must not be `final`.

`@Configuration(proxyBeanMethods = false)` skips the proxy. Startup is a little faster, and Boot's own autoconfiguration uses it. Without the proxy, a direct call really calls the method and creates a new object, so declare the dependency as a method parameter instead. Parameters work in both modes and are the clearer style.

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration(proxyBeanMethods = false)
class LoanConfig {
    @Bean
    FeePolicy feePolicy() {
        return new FeePolicy(50);
    }

    @Bean
    LoanService loanService(FeePolicy feePolicy) { // Injected: the same singleton in any mode.
        return new LoanService(feePolicy);
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/java/configuration-annotation.html)

## Choose how to define a bean

Use a stereotype annotation for your own classes; it keeps the definition next to the code. Use `@Bean` methods for third-party classes, for objects that need construction logic, and when you want several beans of the same type with different settings. Boot's autoconfiguration defines most infrastructure beans for you, and your own definitions usually replace them, as [topic 1](#13_Spring_Boot/01_Core_Features_and_Autoconfiguration/concepts/autoconfiguration-backs-off) explains.

Conditional definitions extend both styles: `@Profile` and `@ConditionalOnProperty` register a bean only in some environments. For loops and complex logic, Spring Framework 7 adds `BeanRegistrar`, covered in [what's new](#13_Spring_Boot/31_Whats_New_in_Spring_Boot_4/concepts/core-null-safety-and-programmatic-beans).

| Situation | Use |
|---|---|
| Your own service, repository, controller | `@Service`, `@Repository`, `@RestController` |
| Library class such as `Clock` or an SDK client | `@Bean` method |
| Two configured instances of one type | Two `@Bean` methods |
| Bean only in some environments | `@Profile` or `@ConditionalOnProperty` |

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/beans/java/basic-concepts.html)
