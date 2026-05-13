# Request Validation and Error Contracts

Backend APIs earn trust by failing clearly. Strong validation and predictable error responses keep bad input from leaking into deeper layers and give clients enough information to recover without reading server internals.

## Key Points

- **Validate at the boundary** - Reject malformed input before it reaches business logic or storage.
- **Use declarative schemas** - Typed request models make contracts explicit and easier to test.
- **Choose coercion carefully** - Convenience can become ambiguity when the server silently accepts buggy input.
- **Keep input sources distinct** - Bodies, query parameters, path parameters, and headers have different roles.
- **Return consistent success shapes** - Similar operations should feel similar to consumers.
- **Design useful error payloads** - Clients need field-level or rule-level guidance, not vague failure strings.
- **Map domain failures intentionally** - Business-rule conflicts should become stable HTTP responses.

## Example

```python
def validate_create_user(payload: dict) -> tuple[int, dict]:
    if "email" not in payload:
        return 400, {"error": "missing_field", "field": "email"}
    if "@" not in payload["email"]:
        return 422, {"error": "invalid_email", "field": "email"}
    return 201, {"id": 1, "email": payload["email"]}


for sample in ({}, {"email": "not-an-email"}, {"email": "user@example.com"}):
    print(validate_create_user(sample))
```

The same input path produces three different outcomes: malformed request, semantically invalid data, and successful creation. That distinction is the core of a good API error contract.
