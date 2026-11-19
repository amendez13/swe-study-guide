# Values, SpEL, Environment, and Profiles

Read configuration into beans, compute small values with SpEL, and switch beans per environment with profiles.

## Key points

- `@Value("${key:default}")` injects one converted property; a missing key without a default fails startup.
- `${...}` is a placeholder and `#{...}` is a SpEL expression; keep expressions small.
- The `Environment` merges property sources by priority and knows the active profiles.
- `@Profile` registers beans per environment; activate profiles from outside the jar.
- Reference secrets with placeholders and supply them at run time.

## Example

Add the [profile-based mail senders](#13_Spring_Boot/06_Values_SpEL_Environment_and_Profiles/concepts/profiles) and a runner that sends one message, then start with and without `prod`.

```java
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class MailDemo {
    @Bean
    CommandLineRunner sendWelcome(MailSender mail) {
        return args -> mail.send("ada@example.com", "Welcome to the library");
    }
}
```

```sh
./mvnw spring-boot:run
./mvnw spring-boot:run -Dspring-boot.run.profiles=prod
```
