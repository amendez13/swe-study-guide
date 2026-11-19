# JSON APIs — Drills

Predict the result before running the example.

## Predict the validation outcome

The record has constraints, and the client posts `{"title":"","pages":10}`. What status does the client get, and does `create` run? What one change makes Spring check the constraints?

```java
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

record NewBook(@NotBlank String title, int pages) {
}

@RestController
class BookApi {
    @PostMapping("/api/books")
    NewBook create(@RequestBody NewBook input) {
        return input;
    }
}
```

**Answer**

200, and `create` runs with the blank title. Constraints on a record do nothing until something validates it. Annotate the parameter with `@Valid` (and add `spring-boot-starter-validation`) to get a 400 before the handler runs, as in [validate request records](#13_Spring_Boot/04_JSON_APIs/concepts/validate-request-records).

## Migrate a Jackson 2 customizer

This configuration compiled against Spring Boot 3. Which names change for Boot 4, and which import stays the same?

```java
import com.fasterxml.jackson.annotation.JsonIgnore;
import tools.jackson.databind.SerializationFeature;
import org.springframework.boot.jackson.autoconfigure.JsonMapperBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class JsonConfig {
    // Boot 3: Jackson2ObjectMapperBuilderCustomizer and com.fasterxml.jackson.databind.SerializationFeature
    @Bean
    JsonMapperBuilderCustomizer sortedKeys() {
        return builder -> builder.enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS);
    }
}

record Member(String name, @JsonIgnore String passwordHash) {
}
```

**Answer**

The customizer type is now `JsonMapperBuilderCustomizer`, and `SerializationFeature` moved to `tools.jackson.databind`. The `@JsonIgnore` import stays in `com.fasterxml.jackson.annotation`, because Jackson 3 kept the annotations package. The code above is the migrated form. See [Jackson 3 in Spring Boot 4](#13_Spring_Boot/04_JSON_APIs/concepts/jackson-3-in-spring-boot-4).
