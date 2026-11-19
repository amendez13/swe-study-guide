# Profiles, YAML, and Property Overrides — Drills

Predict the result before running the example.

## Predict the active value

`application.properties` sets `study.catalog.cache-ttl=30s`, `application-prod.properties` sets `5m`, and the app runs with `SPRING_PROFILES_ACTIVE=prod` and `STUDY_CATALOG_CACHETTL=10m`. What does the runner print? What prints without the second variable?

```java
import java.time.Duration;
import org.springframework.boot.ApplicationRunner;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class PrintTtl {
    @Bean
    ApplicationRunner printTtl(@Value("${study.catalog.cache-ttl}") Duration ttl) {
        return args -> System.out.println(ttl);
    }
}
```

**Answer**

`PT10M`. Environment variables override every packaged config file, including profile-specific ones. Without that variable, the active `prod` profile's file overrides the default file and the runner prints `PT5M`. See [the order of property overrides](#13_Spring_Boot/14_Profiles_YAML_and_Property_Overrides/concepts/the-order-of-property-overrides).

## Fix a profile document that never applies

The intent is a local default with a `prod` override, but the app no longer starts. What is wrong with this `application.yaml`?

```yaml
study:
  catalog:
    branch-name: Local branch
spring:
  config:
    activate:
      on-profile: prod
study:
  catalog:
    branch-name: West Branch
```

**Answer**

There is no `---` separator, so this is one document with a duplicate `study` key and an `on-profile` condition that would apply to the whole file. Boot's YAML loader rejects duplicate keys, so startup fails with a parse error. Put `---` before the `spring.config.activate.on-profile` block so the defaults form their own document. See [switch to YAML](#13_Spring_Boot/14_Profiles_YAML_and_Property_Overrides/concepts/switch-to-yaml).
