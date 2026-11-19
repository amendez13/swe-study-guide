# Executable Jars and Container Images

Package the app once and run it anywhere: an executable jar, an extracted layout for production, and a container image in a registry.

## Key points

- `./mvnw package` produces an uber jar that runs with `java -jar`; Boot 4 removed the embedded launch script.
- Extract the jar with `-Djarmode=tools` for faster startup and container layers.
- A multi-stage Dockerfile copies layers from least to most frequently changed and runs as a non-root user.
- `spring-boot:build-image` builds an image with Paketo buildpacks and no Dockerfile.
- Tag images with immutable versions and keep registry credentials out of the repository.

## Example

Build the jar and an image with buildpacks, then run the image. Docker must be running.

```sh
./mvnw -q package
./mvnw spring-boot:build-image -Dspring-boot.build-image.imageName=study:local
docker run --rm -p 8080:8080 study:local
```
