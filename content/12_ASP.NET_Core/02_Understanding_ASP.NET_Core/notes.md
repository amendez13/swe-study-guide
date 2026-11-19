# Understanding ASP.NET Core

ASP.NET Core combines a web server, an application host, and choices about how HTTP endpoints are written. A migration plan has to account for each of those boundaries.

## Key points

- Kestrel accepts traffic. Endpoint handlers and middleware consume the per-request context.
- Select a presentation style for the feature. Minimal endpoints and controllers can share an application.
- Preserve observable HTTP contracts during a staged migration.

## Example

Run the [Kestrel and request context example](#12_ASP.NET_Core/02_Understanding_ASP.NET_Core/concepts/kestrel-and-the-request-context), then compare the logged request address with the data returned by the endpoint.

```sh
curl -i http://127.0.0.1:5080/request
```
