# Profiles, YAML, and Property Overrides

Ship one jar and change its behavior per environment with profiles, YAML documents, environment variables, and external files.

## Key points

- Keep one validated properties type; only the values change per environment.
- `application-{profile}.properties` overrides the default file when the profile is active; profile groups activate several at once.
- YAML nests keys and can hold profile-specific documents separated by `---`.
- Environment variables use uppercase, underscores, and no dashes; `configtree:` imports mounted secret files.
- Command-line arguments override system properties, environment variables, and files; external files override packaged ones.

## Example

Add the [profile files](#13_Spring_Boot/14_Profiles_YAML_and_Property_Overrides/concepts/profile-specific-property-files) and the properties record, then start the jar with and without the `prod` profile.

```sh
./mvnw -q package -DskipTests
java -jar target/study-0.0.1-SNAPSHOT.jar
SPRING_PROFILES_ACTIVE=prod java -jar target/study-0.0.1-SNAPSHOT.jar
```
