# Defining Beans — Drills

Predict the result before running the example.

## Predict the second counter

How many `Counter` objects exist after startup, and does `report()` see the same counter as `audit()`?

```java
@Configuration(proxyBeanMethods = false)
class CounterConfig {
    @Bean
    Counter counter() {
        return new Counter();
    }

    @Bean
    Reporter reporter() {
        return new Reporter(counter());
    }

    @Bean
    Auditor auditor() {
        return new Auditor(counter());
    }
}
```

**Answer**

Three. Without the configuration proxy, each direct `counter()` call creates a new object, so the bean and the two objects passed to `Reporter` and `Auditor` are all different, and none of them is shared. Take the counter as a parameter, `Reporter reporter(Counter counter)`, so the container injects the one singleton. See [calls between @Bean methods](#13_Spring_Boot/35_Defining_Beans/concepts/calls-between-bean-methods).

## Define a library bean

Your `LoanService` needs a `java.security.SecureRandom` to generate loan codes. Make it injectable as a bean, and inject it into the service.

**Answer**

```java
@Configuration
class SecurityBeans {
    @Bean
    SecureRandom secureRandom() {
        return new SecureRandom();
    }
}

@Service
class LoanService {
    private final SecureRandom random;

    LoanService(SecureRandom random) {
        this.random = random;
    }
}
```

`SecureRandom` is a JDK class, so it cannot carry `@Component`; a `@Bean` method registers it. See [@Configuration and @Bean methods](#13_Spring_Boot/35_Defining_Beans/concepts/configuration-and-bean-methods).
