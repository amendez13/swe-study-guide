# Authorization

Authorization checks the authenticated principal against rules attached to endpoints, or against a resource in handler code.

## Key points

- `RequireAuthorization` and `[Authorize]` attach rules. A fallback policy protects every endpoint that has no rule of its own.
- An anonymous caller is challenged (401 or a login redirect), and an authenticated caller without permission is forbidden (403). In .NET 10, cookie authentication returns 401 and 403 for API endpoints.
- Policies combine claim, role, and custom requirements. Use `IAuthorizationService` for resource-based checks and to hide UI.

## Example

Run the [policies example](#12_ASP.NET_Core/24_Authorization/concepts/policies-from-claims-and-roles) with a cookie jar and compare the two departments.

```sh
curl -s -c jar.txt 'http://127.0.0.1:5080/login?dept=archives' -o /dev/null
curl -i -b jar.txt http://127.0.0.1:5080/vault
curl -s -c jar.txt 'http://127.0.0.1:5080/login?dept=loans' -o /dev/null
curl -i -b jar.txt http://127.0.0.1:5080/vault
```
