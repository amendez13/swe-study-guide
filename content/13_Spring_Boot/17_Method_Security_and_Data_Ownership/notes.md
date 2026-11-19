# Method Security and Data Ownership

Move from "is this user signed in?" to "may this user touch this record?".

## Key points

- `@EnableMethodSecurity` turns on `@PreAuthorize` and `@PostAuthorize`; a failed check becomes 403.
- Record the owner from the authenticated principal, never from the request body.
- Owner-scoped queries such as `findByIdAndOwner` are the simplest and most reliable check.
- Put complex rules in a bean and call it from SpEL with `@beanName`.
- Templates can hide controls with `sec:authorize`, but the server must still enforce the rule.
- Self-invocation bypasses the security proxy.

## Example

Run the [base example](#13_Spring_Boot/17_Method_Security_and_Data_Ownership/concepts/record-the-owner-of-data) with the [owner-scoped read](#13_Spring_Boot/17_Method_Security_and_Data_Ownership/concepts/scope-queries-to-the-owner). Use the [route rules](#13_Spring_Boot/16_Spring_Security_Foundations/concepts/secure-routes-and-http-verbs) so `/api/**` accepts Basic credentials without CSRF tokens.

Enter the password for the corresponding in-memory example user when curl prompts.

```sh
curl -s --user ada http://localhost:8080/api/notes -H 'Content-Type: application/json' -d '{"text":"Chapter 3 notes"}'
curl -i --user grace http://localhost:8080/api/notes/1
```
