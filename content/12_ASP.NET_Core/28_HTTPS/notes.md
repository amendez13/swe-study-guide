# HTTPS

Serve every page and API over HTTPS. Kestrel or a reverse proxy terminates TLS, and the app enforces HTTPS with HSTS and redirection for browsers, and by rejecting plain HTTP for APIs.

## Key points

- Use the trusted dev certificate locally and a CA-issued certificate in `Kestrel:Endpoints` or at the proxy in production.
- `UseHsts` outside Development and `UseHttpsRedirection` for browser apps. Behind a proxy, forward the original scheme first.
- APIs should listen only on HTTPS or reject plain HTTP with 400 rather than redirecting.

## Example

Trust the development certificate, then run the [HSTS example](#12_ASP.NET_Core/28_HTTPS/concepts/http-strict-transport-security) in Production on both schemes.

```sh
dotnet dev-certs https --trust
dotnet run --no-launch-profile -- --urls "https://localhost:5443;http://localhost:5080"
curl -i http://localhost:5080/
curl -i https://localhost:5443/
```

The HSTS middleware excludes `localhost`, so the second response has no `Strict-Transport-Security` header. Add a hosts entry and use that name to see it.
