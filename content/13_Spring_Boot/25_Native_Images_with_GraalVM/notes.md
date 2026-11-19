# Native Images with GraalVM

Compile the application into a native executable that starts in milliseconds, and learn what the closed world costs.

## Key points

- Native images trade build time, flexibility, and some peak throughput for fast startup and low memory.
- Spring AOT processing fixes the bean set at build time, so conditions and profiles are build-time choices.
- `./mvnw -Pnative native:compile` needs GraalVM for Java 25 and the `native-maven-plugin`.
- `./mvnw -Pnative spring-boot:build-image` builds a Linux native container with only Docker.
- Register reflection and resources your code needs with runtime hints; run tests natively with `-PnativeTest`.

## Example

Build a native container for the [JSON API example](#13_Spring_Boot/12_JSON_APIs/concepts/a-rest-controller) and compare the startup line with the JVM image from [topic 23](#13_Spring_Boot/23_Executable_Jars_and_Container_Images).

```sh
./mvnw -Pnative spring-boot:build-image -Dspring-boot.build-image.imageName=study:native
docker run --rm -p 8080:8080 study:native | grep 'Started'
```
