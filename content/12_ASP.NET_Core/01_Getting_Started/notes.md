# Getting Started

Start with the [course setup](#12_ASP.NET_Core) and the [ASP.NET Core and .NET card](#12_ASP.NET_Core/01_Getting_Started/concepts/asp-net-core-and-net). This introduction assumes basic C# and uses the HTTP exchange to connect the SDK, runtime, and web framework.

## Key points

- The SDK builds a Web SDK project. The ASP.NET Core framework handles the HTTP conversation at runtime.
- The same app can expose HTML and JSON under different URLs.
- Use an HTTP client that shows headers and status as well as the response body.

## Example

Run the [HTTP request and response example](#12_ASP.NET_Core/01_Getting_Started/concepts/http-request-and-response). Inspect the request target and the response with the command below.

```sh
curl -i 'http://127.0.0.1:5080/status?wing=east'
```
