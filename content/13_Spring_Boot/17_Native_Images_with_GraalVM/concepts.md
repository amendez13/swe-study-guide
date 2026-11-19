# Native Images with GraalVM

## What a native image is

GraalVM Native Image compiles a Java application ahead of time into a standalone executable for one operating system and architecture. It analyses the application from its entry point and keeps only the code it can reach. The executable starts in tens of milliseconds and uses far less memory than a JVM, because no classes are loaded or compiled at run time.

The cost is a closed world. Reflection, resources, proxies, and serialization must be declared at build time. Builds take minutes and need several gigabytes of memory. Peak throughput can be lower than a warmed-up JVM, which keeps optimizing hot code. Native images suit scale-to-zero services, command-line tools, and dense deployments; long-running services often do better with the [AOT cache](#13_Spring_Boot/18_AOT_Cache_and_Fast_Startup/concepts/the-java-aot-cache).

```sh
./mvnw -Pnative native:compile
ls -lh target/study
./target/study
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/native-image/introducing-graalvm-native-images.html)

## Spring AOT processing

Spring normally discovers configuration at startup: it scans classes, evaluates conditions, and creates proxies with reflection. For a native image, Spring Boot runs that work during the build instead. The AOT engine starts the application context, evaluates `@Conditional` and `@Profile` decisions, and generates Java source that registers the resulting bean definitions directly. It also writes GraalVM hints for the reflection and resources it knows about.

Spring Native, the old experimental project, was replaced by this built-in support in Spring Boot 3, and Boot 4 continues it. Because conditions are evaluated during the build, the set of beans is fixed. A profile or property that would add or remove a bean must be set when building the image. Property values that beans read at run time can still change.

```java
import org.springframework.boot.autoconfigure.condition.ConditionalOnBooleanProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class ExportConfig {
    // In a native image this decision is made at build time, not when the executable starts.
    @Bean
    @ConditionalOnBooleanProperty("study.export.enabled")
    Runnable exporter() {
        return () -> System.out.println("Exporting catalog");
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/native-image/introducing-graalvm-native-images.html#packaging.native-image.introducing-graalvm-native-images.understanding-aot-processing)

## Build a native executable

Install a GraalVM distribution for Java 25 and make it the active JDK. Add GraalVM's Native Build Tools plugin, `native-maven-plugin`, to the POM. Boot's parent configures the plugin's version and the `native` profile. That profile runs Spring AOT processing during `package`, and `native:compile` then runs the native image builder on the result.

The executable lands in `target/` under the artifact name. It is specific to the build machine's operating system and CPU, so a macOS build does not run in a Linux container. Use the [buildpack route](#13_Spring_Boot/17_Native_Images_with_GraalVM/concepts/a-native-container-image-with-buildpacks) to produce Linux images from any machine.

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.graalvm.buildtools</groupId>
      <artifactId>native-maven-plugin</artifactId>
    </plugin>
    <plugin>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-maven-plugin</artifactId>
    </plugin>
  </plugins>
</build>
```

[Spring Boot docs](https://docs.spring.io/spring-boot/how-to/native-image/developing-your-first-application.html#howto.native-image.developing-your-first-application.native-build-tools)

## A native container image with buildpacks

`spring-boot:build-image` with the `native` profile builds a native image inside the Paketo builder, so the build machine needs Docker but not GraalVM. The resulting container holds only the executable on a minimal base image, with no JVM. Images are small and start almost instantly.

The native build runs inside Docker and needs plenty of memory; give Docker Desktop at least 8 GB for a typical web application. The image targets Linux on the builder's architecture. Run it the same way as the JVM image, with the same environment variables.

```sh
./mvnw -Pnative spring-boot:build-image -Dspring-boot.build-image.imageName=study:native
docker run --rm -p 8080:8080 study:native
docker images study
```

[Spring Boot docs](https://docs.spring.io/spring-boot/how-to/native-image/developing-your-first-application.html#howto.native-image.developing-your-first-application.buildpacks)

## Runtime hints for reflection and resources

AOT processing records hints for what Spring itself uses, but it cannot see reflection in your code or in libraries that look up classes by name. A missing hint shows up only when the native executable runs, as a `ClassNotFoundException`, a missing resource, or an empty JSON object. Register what is missing with a `RuntimeHintsRegistrar` and import it with `@ImportRuntimeHints`.

For types that are only serialized, such as a record that a client deserializes from JSON, `@RegisterReflectionForBinding` registers the reflection that Jackson needs. Records returned from Spring MVC handlers are detected automatically. Prefer these focused hints to broad reflection configuration.

```java
import org.springframework.aot.hint.MemberCategory;
import org.springframework.aot.hint.RuntimeHints;
import org.springframework.aot.hint.RuntimeHintsRegistrar;
import org.springframework.aot.hint.annotation.RegisterReflectionForBinding;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportRuntimeHints;

record PartnerTitle(String isbn, String title) {
}

@Configuration
@ImportRuntimeHints(CatalogHints.class)
@RegisterReflectionForBinding(PartnerTitle.class)
class NativeConfig {
}

class CatalogHints implements RuntimeHintsRegistrar {
    @Override
    public void registerHints(RuntimeHints hints, ClassLoader classLoader) {
        hints.resources().registerPattern("catalog/*.csv");
        hints.reflection().registerType(PluginFormatter.class, MemberCategory.INVOKE_PUBLIC_CONSTRUCTORS);
    }
}

class PluginFormatter {
    public PluginFormatter() {
    }
}
```

[Spring Framework docs](https://docs.spring.io/spring-framework/reference/core/aot.html#aot.hints)

## Libraries and native tests

Many libraries need native configuration of their own. GraalVM's reachability metadata repository supplies it for popular libraries, and the Native Build Tools plugin downloads it automatically. Libraries can also ship metadata in their jars. Check that each dependency supports native images before you rely on it, especially anything that uses dynamic class loading or bytecode generation at run time.

Run the test suite as a native image to catch missing hints before release. The `nativeTest` profile compiles the JUnit tests into a native executable and runs them. These tests are slow to build, so run them in CI rather than on every local change. Bean overrides such as `@MockitoBean` are not supported in AOT mode, so mark those test classes with `@DisabledInAotMode`.

```sh
./mvnw -PnativeTest test
```

```java
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.aot.DisabledInAotMode;

@SpringBootTest
@DisabledInAotMode
class MockHeavyTests {
    @Test
    void usesMockitoBeans() {
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/native-image/testing-native-applications.html)
