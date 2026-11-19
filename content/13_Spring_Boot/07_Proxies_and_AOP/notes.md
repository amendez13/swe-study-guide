# Proxies and AOP

Understand how annotations such as `@Transactional` and `@Cacheable` work, and why they sometimes do nothing.

## Key points

- AOP keeps cross-cutting concerns such as transactions, security, and caching out of business code.
- Spring wraps beans in proxies; other beans receive the proxy, which adds behavior and forwards the call.
- Boot uses CGLIB subclass proxies, which cannot intercept `private` or `final` methods.
- Calls inside the same object skip the proxy: the self-invocation trap.
- Write aspects with `@Aspect` and `@Around` after adding `spring-boot-starter-aspectj`.

## Example

Add `spring-boot-starter-aspectj`, the [timing aspect and annotation](#13_Spring_Boot/07_Proxies_and_AOP/concepts/write-an-aspect), and a service that uses it. Call the service from a runner and from inside itself, and compare the output.

```java
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Service;

@Service
class SlowService {
    @LogTime
    public String work() throws InterruptedException {
        Thread.sleep(200);
        return "done";
    }

    public String workTwice() throws InterruptedException {
        return work() + work(); // No timing output: self-invocation.
    }
}

@Configuration
class AopDemo {
    @Bean
    CommandLineRunner aopRunner(SlowService service) {
        return args -> {
            System.out.println(service.getClass().getName());
            service.work();
            service.workTwice();
        };
    }
}
```
