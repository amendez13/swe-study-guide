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

Three requests to the same endpoint, each producing a different error contract:

```http
# 1. Missing required field → 400
POST /users HTTP/1.1
Content-Type: application/json
{}

HTTP/1.1 400 Bad Request
{"error": "missing_field", "field": "email", "message": "email is required"}

# 2. Invalid field value → 422
POST /users HTTP/1.1
Content-Type: application/json
{"email": "not-an-email", "role": "superadmin"}

HTTP/1.1 422 Unprocessable Entity
{"error": "validation_error", "details": [
  {"field": "email", "message": "must be a valid email address"},
  {"field": "role", "message": "must be one of: admin, editor, viewer"}
]}

# 3. Domain conflict → 409
POST /users HTTP/1.1
Content-Type: application/json
{"email": "taken@example.com", "role": "editor"}

HTTP/1.1 409 Conflict
{"error": "duplicate_email", "message": "a user with this email already exists"}

# 4. Success → 201
POST /users HTTP/1.1
Content-Type: application/json
{"email": "new@example.com", "role": "editor"}

HTTP/1.1 201 Created
{"id": 7, "email": "new@example.com", "role": "editor"}
```

Each outcome uses a distinct status code and structured error body so the client can handle each case programmatically — no log inspection required.
