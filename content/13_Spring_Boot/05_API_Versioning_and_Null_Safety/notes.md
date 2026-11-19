# API Versioning and Null Safety

Two Spring Boot 4 features that make API contracts explicit: versioned request mappings on the server and client, and JSpecify nullability annotations in code.

## Key points

- Map several handlers to one path with the `version` attribute; configure how requests carry the version with `spring.mvc.apiversion.*`.
- A missing version uses the default, if one is set; an unsupported version is rejected with 400.
- A baseline such as `1.2+` carries a handler forward to later versions.
- `StandardApiVersionDeprecationHandler` announces deprecation and sunset dates in response headers.
- `RestClient` sends versions through an `ApiVersionInserter`; Boot does not copy the server settings.
- `@NullMarked` makes non-null the default; mark the exceptions with `@Nullable`.

## Example

Add the properties and controller from [versioned request mappings](#13_Spring_Boot/05_API_Versioning_and_Null_Safety/concepts/versioned-request-mappings), then request each version.

```sh
curl -s http://localhost:8080/api/books/1
curl -s -H 'API-Version: 2.0' http://localhost:8080/api/books/1
curl -i -H 'API-Version: 3.0' http://localhost:8080/api/books/1
```
