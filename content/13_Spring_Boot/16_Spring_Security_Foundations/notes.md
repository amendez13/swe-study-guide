# Spring Security Foundations

Put Spring Security in front of the app: understand the filter chain, define users, and write route rules.

## Key points

- Adding the security starter locks every endpoint and creates a temporary `user` account.
- A `SecurityFilterChain` bean defines the policy; rules are checked in order and the first match decides.
- Store password hashes produced by the delegating `PasswordEncoder`.
- Back `UserDetailsService` with a Spring Data repository for real accounts.
- Rules can match HTTP methods; anonymous users get 401, authenticated users without the role get 403.
- CSRF protection stays on for cookie-based sessions; Thymeleaf adds the token to forms.

## Example

Run the [route and verb rules](#13_Spring_Boot/16_Spring_Security_Foundations/concepts/secure-routes-and-http-verbs) with the [in-memory users](#13_Spring_Boot/16_Spring_Security_Foundations/concepts/users-and-password-encoding) and a small `/api/books` controller. Compare the status codes.

Enter the password for the corresponding in-memory example user when curl prompts.

```sh
curl -i http://localhost:8080/api/books/1
curl -i -X DELETE http://localhost:8080/api/books/1 --user ada
curl -i -X DELETE http://localhost:8080/api/books/1 --user grace
```
