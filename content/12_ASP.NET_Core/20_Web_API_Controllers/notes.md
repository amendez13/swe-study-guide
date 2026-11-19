# Web API Controllers

Web API controllers apply the MVC pattern to HTTP APIs. Actions return data, and output formatters serialize it according to content negotiation.

## Key points

- Derive from `ControllerBase`, add `[ApiController]`, and route with attributes. Use `ActionResult<T>` to return either data or a status result.
- `[ApiController]` adds automatic 400 responses, binding-source inference, and Problem Details for error results. In ASP.NET Core 10 it also turns cookie login redirects into 401 or 403.
- Microsoft recommends Minimal APIs for new APIs. Controllers remain the choice when you need MVC-only extensibility.

## Example

Run the [typed action results example](#12_ASP.NET_Core/20_Web_API_Controllers/concepts/typed-action-results) and create a book.

```sh
curl -i http://127.0.0.1:5080/api/books \
  -H 'Content-Type: application/json' -d '{"title":"Almanac"}'
curl -i http://127.0.0.1:5080/api/books/9
```

Run the [content negotiation example](#12_ASP.NET_Core/20_Web_API_Controllers/concepts/content-negotiation) and compare the status codes.

```sh
curl -i -H 'Accept: text/csv' http://127.0.0.1:5080/api/visits
curl -i http://127.0.0.1:5080/api/visits
```
