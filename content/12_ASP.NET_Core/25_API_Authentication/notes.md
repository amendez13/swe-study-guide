# API Authentication

APIs authenticate callers with bearer tokens, usually JWTs issued by an identity provider. The API validates each token and applies authorization policies to its claims.

## Key points

- OAuth 2.0 issues access tokens for APIs, and OpenID Connect adds user sign-in. The API validates the signature, issuer, audience, and expiry.
- `AddJwtBearer` reads its settings from `Authentication:Schemes:Bearer`, and `dotnet user-jwts` issues development tokens.
- Apply policies with `RequireAuthorization`, on route groups where possible. Describe the bearer scheme in OpenAPI with a document transformer.

## Example

Add the JWT bearer package to a fresh `net10.0` project, run the [policies example](#12_ASP.NET_Core/25_API_Authentication/concepts/authorization-policies-for-minimal-api-endpoints) in Development, and create two tokens.

```sh
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer --version '10.*'
dotnet user-jwts create --audience http://localhost:5080 --role librarian
dotnet user-jwts create --audience http://localhost:5080 --role reader
ASPNETCORE_ENVIRONMENT=Development dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```

Call the endpoints with each printed token.

```sh
curl -i -X POST http://127.0.0.1:5080/catalog/books -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"title":"Almanac"}'
```

The [OpenAPI example](#12_ASP.NET_Core/25_API_Authentication/concepts/describe-authentication-in-openapi) also needs `Microsoft.AspNetCore.OpenApi`, as in [chapter 11](#12_ASP.NET_Core/11_OpenAPI).
