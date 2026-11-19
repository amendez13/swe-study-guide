# Identity

Authentication turns a request into a `ClaimsPrincipal`. ASP.NET Core Identity adds stored user accounts, password hashing, and sign-in on top of the authentication schemes.

## Key points

- A principal holds identities, and identities hold claims. A scheme authenticates the request, challenges anonymous callers, and forbids unauthorized ones.
- Identity stores users through EF Core and is driven by `UserManager` and `SignInManager`. It offers a Razor UI or, since .NET 8, JSON API endpoints.
- Customize with `IdentityOptions`, scaffolded pages, a derived user class, and a claims principal factory.

## Example

The Identity examples need EF Core's SQLite provider and the Identity EF Core stores in a fresh `net10.0` project. The default UI examples also need the UI package.

```sh
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version '10.*'
dotnet add package Microsoft.AspNetCore.Identity.EntityFrameworkCore --version '10.*'
dotnet add package Microsoft.AspNetCore.Identity.UI --version '10.*'
```

Run the [Identity API endpoints example](#12_ASP.NET_Core/23_Identity/concepts/identity-api-endpoints), then register, log in, and call the protected endpoint.

```sh
curl -i http://127.0.0.1:5080/account/register -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.org","password":"Passw0rd!"}'
token=$(curl -fsS http://127.0.0.1:5080/account/login -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.org","password":"Passw0rd!"}' | sed 's/.*"accessToken":"\([^"]*\)".*/\1/')
curl -i -H "Authorization: Bearer $token" http://127.0.0.1:5080/books
```
