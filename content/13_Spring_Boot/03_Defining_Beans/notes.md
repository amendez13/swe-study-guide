# Defining Beans

Register beans with annotations on your classes or with `@Bean` methods, and know when to use each.

## Key points

- `@Component` plus component scanning registers your own classes; the name defaults to the class name.
- `@Service`, `@Repository`, and `@Controller` are components that also state the role; `@Repository` translates exceptions.
- `@Bean` methods in a `@Configuration` class define library objects and beans with construction logic.
- With `proxyBeanMethods = false`, calling another `@Bean` method creates a new object; inject a parameter instead.
- `@Profile` and conditions make a definition depend on the environment.

## Example

Add the [InfrastructureConfig](#13_Spring_Boot/03_Defining_Beans/concepts/configuration-and-bean-methods) and the [DueDateCalculator](#13_Spring_Boot/03_Defining_Beans/concepts/component-scanning-and-component), then expose the due date.

```java
import java.time.LocalDate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class DueDateController {
    private final DueDateCalculator calculator;

    DueDateController(DueDateCalculator calculator) {
        this.calculator = calculator;
    }

    @GetMapping("/api/due-date")
    LocalDate dueDate() {
        return calculator.dueDate();
    }
}
```

```sh
curl -s http://localhost:8080/api/due-date
```
