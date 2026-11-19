# JSON APIs

Expose JSON endpoints with `@RestController`, bind and validate request records, and return predictable errors.

## Key points

- A `@RestController` writes return values as JSON; use `ResponseEntity` when the handler picks the status.
- Return 201 with a `Location` header from a creation endpoint.
- Constraints on a record take effect only with `@Valid`.
- Boot 4 uses Jackson 3: `tools.jackson` packages, `JsonMapper`, and `JsonMapperBuilderCustomizer`; annotations are unchanged.
- Enable `spring.mvc.problemdetails.enabled` and map domain exceptions to `ProblemDetail` in a `@RestControllerAdvice`.

## Example

Run the [create example](#13_Spring_Boot/12_JSON_APIs/concepts/create-a-resource-from-a-json-body) and inspect the status and `Location` header.

```sh
curl -i http://localhost:8080/api/books \
  -H 'Content-Type: application/json' -d '{"title":"Accelerate","pages":288}'
```
