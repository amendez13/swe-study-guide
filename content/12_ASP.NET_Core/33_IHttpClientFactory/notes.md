# IHttpClientFactory

Creating and disposing `HttpClient` per call exhausts sockets, and one static client ignores DNS changes. `IHttpClientFactory` pools handlers, centralizes client settings, and lets you add handlers for resilience and cross-cutting headers.

## Key points

- Use `IHttpClientFactory`, or a long-lived client with `PooledConnectionLifetime`. Prefer named or typed clients to keep settings in one place.
- Typed clients are transient. Don't capture them in singletons.
- `Microsoft.Extensions.Http.Resilience` replaces `Microsoft.Extensions.Http.Polly`. `AddStandardResilienceHandler` covers most apps, and `ConfigureHttpClientDefaults` applies it to every client.

## Example

The examples call endpoints in the same app on port 5080. Add the resilience package and run the [resilience example](#12_ASP.NET_Core/33_IHttpClientFactory/concepts/handle-transient-errors-with-resilience-handlers).

```sh
dotnet add package Microsoft.Extensions.Http.Resilience
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
time curl -i http://127.0.0.1:5080/proxy
```

The response is 200 after the third upstream call. The console shows a log line for each retry.
