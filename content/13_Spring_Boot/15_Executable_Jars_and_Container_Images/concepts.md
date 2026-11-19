# Executable Jars and Container Images

## The executable uber jar

`./mvnw package` runs the Spring Boot Maven plugin's `repackage` goal, which turns the normal jar into an executable one. The jar holds your classes under `BOOT-INF/classes`, every dependency as a nested jar under `BOOT-INF/lib`, and a small launcher that can load nested jars. `java -jar` is all a server needs, besides a Java 25 runtime.

Changed in Boot 4: the "fully executable" jar with an embedded Unix launch script is gone, and so is the classic loader implementation. Run the jar with `java -jar` from a service manager such as systemd, or put it in a container. The plain jar without dependencies is kept beside it as `*.jar.original`.

```sh
./mvnw -q package
ls target/*.jar
jar tf target/study-0.0.1-SNAPSHOT.jar | grep -E '^BOOT-INF/(classes|lib)/' | head
java -jar target/study-0.0.1-SNAPSHOT.jar
```

[Spring Boot docs](https://docs.spring.io/spring-boot/maven-plugin/packaging.html)

## Extract the jar for production

Reading classes from nested jars works but is slower than reading them from plain files. For production, extract the uber jar with Boot's `tools` jar mode. The result is an application jar plus a `lib` folder, and the application jar's manifest lists the dependencies. Start it with `java -jar` as before. Startup is faster, and the layout is what the [AOT cache](#13_Spring_Boot/18_AOT_Cache_and_Fast_Startup/concepts/the-java-aot-cache) needs.

The `--layers` option splits the files by how often they change: dependencies, Spring Boot's loader, snapshot dependencies, and application code. A container image can copy each layer separately, so rebuilding after a code change reuses the cached dependency layers.

```sh
java -Djarmode=tools -jar target/study-0.0.1-SNAPSHOT.jar extract --destination target/extracted
java -jar target/extracted/study-0.0.1-SNAPSHOT.jar
java -Djarmode=tools -jar target/study-0.0.1-SNAPSHOT.jar list-layers
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/efficient.html)

## Write a Dockerfile

A hand-written Dockerfile gives full control over the image. A multi-stage build keeps it small. The first stage extracts the jar into layers, and the second copies each layer onto a JRE base image, from least to most frequently changed. Run as a non-root user and let the JVM size its heap from the container's memory limit.

Build the jar first, then the image. Changing only application code rebuilds only the last layer, so pushes and pulls move a few kilobytes instead of the whole dependency set. Pin the base image to a Java 25 release that you patch regularly.

```dockerfile
FROM eclipse-temurin:25-jre AS builder
WORKDIR /builder
COPY target/*.jar application.jar
RUN java -Djarmode=tools -jar application.jar extract --layers --destination extracted

FROM eclipse-temurin:25-jre
RUN useradd --system --uid 10001 spring
USER spring
WORKDIR /application
COPY --from=builder /builder/extracted/dependencies/ ./
COPY --from=builder /builder/extracted/spring-boot-loader/ ./
COPY --from=builder /builder/extracted/snapshot-dependencies/ ./
COPY --from=builder /builder/extracted/application/ ./
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "application.jar"]
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/container-images/dockerfiles.html)

## Build an image with buildpacks

Cloud Native Buildpacks build an image without a Dockerfile. `./mvnw spring-boot:build-image` sends the application to the Paketo Java buildpacks through a local Docker daemon. They pick a JRE for the project's Java version, add the layered jar, and configure a memory calculator. A rebuild can then update the base image or JRE without changes to your code.

Configure the image name and buildpack options in the plugin or on the command line. Buildpack settings are environment variables such as `BP_JVM_VERSION`. Prefer buildpacks when you want consistent, patched images across many services. Write a Dockerfile only when you need control the buildpacks do not offer.

```xml
<plugin>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-maven-plugin</artifactId>
  <configuration>
    <image>
      <name>docker.io/example/study:${project.version}</name>
      <env>
        <BP_JVM_VERSION>25</BP_JVM_VERSION>
      </env>
    </image>
  </configuration>
</plugin>
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/packaging/container-images/cloud-native-buildpacks.html)

## Release an image to a registry

A registry such as Docker Hub stores images so that servers and clusters can pull them. Tag each release with an immutable version, such as the project version or the commit SHA. A moving tag such as `latest` makes it unclear which code is running and makes rollbacks harder.

Either push with the Docker CLI after `docker login`, or let the Maven plugin publish while it builds. The plugin reads registry credentials from its `docker.publishRegistry` configuration, which can take them from environment variables in CI. Never commit a registry token.

```sh
./mvnw spring-boot:build-image -Dspring-boot.build-image.imageName=docker.io/example/study:0.0.1
docker login docker.io
docker push docker.io/example/study:0.0.1
docker run --rm -p 8080:8080 -e SPRING_PROFILES_ACTIVE=prod docker.io/example/study:0.0.1
```

[Spring Boot docs](https://docs.spring.io/spring-boot/maven-plugin/build-image.html#build-image.examples.docker)
