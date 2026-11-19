# AOT Cache and Fast Startup

Speed up JVM startup without leaving the JVM, and compare the options with native images.

## Key points

- Java 25's AOT cache stores loaded and linked classes from a training run; it needs the same JDK and classpath.
- Train with `-Dspring.context.exit=onRefresh` on the extracted jar, then start with `-XX:AOTCache`.
- Container images freeze the JDK and classpath, so they suit the cache; buildpacks can train during the build.
- Spring AOT on the JVM (`process-aot` plus `-Dspring.aot.enabled=true`) fixes the bean set at build time.
- CRaC restores an already-warm JVM but snapshots its memory, including any secrets.

## Example

Extract the jar, train the cache, and compare two startup times.

```sh
./mvnw -q package -DskipTests
java -Djarmode=tools -jar target/study-0.0.1-SNAPSHOT.jar extract --destination application
cd application
java -jar study-0.0.1-SNAPSHOT.jar | grep Started
java -XX:AOTCacheOutput=app.aot -Dspring.context.exit=onRefresh -jar study-0.0.1-SNAPSHOT.jar
java -XX:AOTCache=app.aot -jar study-0.0.1-SNAPSHOT.jar | grep Started
```
