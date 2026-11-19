# IHttpClientFactory

## The problem with HttpClient

`HttpClient` looks disposable, so the natural code is `using var client = new HttpClient()` around each call. Disposing the client closes its connection, and the closed socket then stays in the `TIME_WAIT` state for a while. Under load, an app that does this can run out of sockets. The opposite fix, one static `HttpClient` for the app, reuses connections well but keeps them open indefinitely, so the app never sees DNS changes when a service moves.

There are two good answers. Use `IHttpClientFactory`, which pools and recycles the underlying handlers. Or use a long-lived client whose `SocketsHttpHandler` sets `PooledConnectionLifetime`, so connections are replaced periodically. The example calls the app's own `/books` endpoint, using the second approach.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
var shared = new HttpClient(new SocketsHttpHandler { PooledConnectionLifetime = TimeSpan.FromMinutes(2) })
{
    BaseAddress = new Uri("http://127.0.0.1:5080"),
};
app.MapGet("/books", () => new[] { "Atlas", "Primer" });
app.MapGet("/proxy", async () => await shared.GetStringAsync("/books"));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines)

## Create clients with IHttpClientFactory

`AddHttpClient()` registers `IHttpClientFactory`. Each `CreateClient()` call returns a new, cheap `HttpClient` that wraps a pooled `HttpMessageHandler`. The factory keeps each handler for two minutes by default and then switches new clients to a fresh one, which picks up DNS changes. Old handlers are disposed once no client uses them.

You don't need to dispose clients from the factory, though doing so is harmless. Don't hold one in a singleton for the app's lifetime, because that defeats the handler rotation. Create the client where you need it. `SetHandlerLifetime` changes the rotation interval. The example proxies the app's own endpoint.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient();
var app = builder.Build();
app.MapGet("/books", () => new[] { "Atlas", "Primer" });
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
{
    var client = factory.CreateClient();
    return await client.GetFromJsonAsync<string[]>("http://127.0.0.1:5080/books");
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0)

## Named clients

A named client keeps per-service settings in one place. Register it with `AddHttpClient("catalog", client => ...)` to set the base address, default headers, and timeout. Then create it by name. Every client with that name shares the configuration and its own handler pool.

Named clients suit apps that call a few services and want the settings centralized, without writing a class per service. The name is a string, so keep it in a constant to avoid typos. Settings can come from configuration, as shown here with `Catalog:BaseUrl`.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?> { ["Catalog:BaseUrl"] = "http://127.0.0.1:5080" });
builder.Services.AddHttpClient(Clients.Catalog, (services, client) =>
{
    client.BaseAddress = new Uri(services.GetRequiredService<IConfiguration>()["Catalog:BaseUrl"]!);
    client.DefaultRequestHeaders.UserAgent.ParseAdd("StudyApi/1.0");
    client.Timeout = TimeSpan.FromSeconds(5);
});
var app = builder.Build();
app.MapGet("/books", (HttpRequest request) => new { agent = request.Headers.UserAgent.ToString() });
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient(Clients.Catalog).GetStringAsync("/books"));
app.Run();

static class Clients { public const string Catalog = "catalog"; }
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0#named-clients)

## Typed clients

A typed client is a class that takes an `HttpClient` in its constructor and exposes methods for one remote API. Register it with `AddHttpClient<TClient>()` and inject the class where you need it. The factory configures and supplies the `HttpClient`, and callers see methods such as `GetBooksAsync` instead of URLs and JSON.

Typed clients are registered as transient. Don't inject one into a singleton, because the singleton would keep one handler forever. Register an interface with `AddHttpClient<ICatalogClient, CatalogClient>()` to swap in a fake in tests. Request `/proxy` to see the typed call.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient<CatalogClient>(client => client.BaseAddress = new Uri("http://127.0.0.1:5080"));
var app = builder.Build();
app.MapGet("/books", () => new[] { new Book("Atlas", 3), new Book("Primer", 0) });
app.MapGet("/proxy", async (CatalogClient catalog) => await catalog.GetAvailableAsync());
app.Run();

public record Book(string Title, int Copies);

public class CatalogClient(HttpClient http)
{
    public async Task<Book[]> GetAvailableAsync()
    {
        var books = await http.GetFromJsonAsync<Book[]>("/books") ?? [];
        return books.Where(b => b.Copies > 0).ToArray();
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0#typed-clients)

## Handle transient errors with resilience handlers

Remote calls fail for short-lived reasons: a restart, a timeout, a 503 under load. Retrying with backoff hides most of these. The book-era approach used `Microsoft.Extensions.Http.Polly`. Since .NET 8, the recommended package is `Microsoft.Extensions.Http.Resilience`, built on Polly 8. `AddStandardResilienceHandler()` adds a tested pipeline: a rate limiter, a total timeout, retries with exponential backoff and jitter, a circuit breaker, and a per-attempt timeout.

The standard retry handles 5xx, 408, and 429 responses as well as network errors and attempt timeouts. Tune it through the options lambda. The example's `/flaky` endpoint fails twice, then succeeds. The proxy returns 200 after a few seconds of retries.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("upstream", client => client.BaseAddress = new Uri("http://127.0.0.1:5080"))
    .AddStandardResilienceHandler(options => options.Retry.MaxRetryAttempts = 3);
var app = builder.Build();
var calls = 0;
app.MapGet("/flaky", () => ++calls % 3 == 0 ? Results.Ok($"ok on call {calls}") : Results.StatusCode(503));
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient("upstream").GetStringAsync("/flaky"));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience)

## Build a custom resilience pipeline

When the standard pipeline doesn't fit, `AddResilienceHandler` builds your own from Polly strategies. Add a retry with `HttpRetryStrategyOptions`, a circuit breaker with `HttpCircuitBreakerStrategyOptions`, and a timeout, in that order from outer to inner. Each option type already knows which HTTP results count as transient.

Be careful retrying non-idempotent requests such as `POST`, because a retry after a lost response can repeat the action. The standard options have `DisableForUnsafeHttpMethods()` for that. In the example, a short base delay makes retries visible in the log quickly.

```csharp
using Microsoft.Extensions.Http.Resilience;
using Polly;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("upstream", client => client.BaseAddress = new Uri("http://127.0.0.1:5080"))
    .AddResilienceHandler("upstream-pipeline", pipeline =>
    {
        pipeline.AddRetry(new HttpRetryStrategyOptions
        {
            MaxRetryAttempts = 4,
            BackoffType = DelayBackoffType.Exponential,
            Delay = TimeSpan.FromMilliseconds(200),
            UseJitter = true,
        });
        pipeline.AddTimeout(TimeSpan.FromSeconds(2));
    });
var app = builder.Build();
var calls = 0;
app.MapGet("/flaky", () => ++calls % 4 == 0 ? Results.Ok($"ok on call {calls}") : Results.StatusCode(503));
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient("upstream").GetStringAsync("/flaky"));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience#add-custom-resilience-handlers)

## A custom DelegatingHandler

Every `HttpClient` sends requests through a chain of `HttpMessageHandler`s, ending in the one that does the network I/O. A `DelegatingHandler` sits in that chain. It can change the request, call `base.SendAsync` to pass it on, and inspect the response on the way back. That makes it the place for API keys, correlation ids, and logging that every call needs.

Register the handler as transient and attach it with `AddHttpMessageHandler<T>()`. Handlers run in the order you add them, so the first one added is the outermost. The example adds an API key header that the app's own endpoint echoes back.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddTransient<ApiKeyHandler>();
builder.Services.AddHttpClient("partner", client => client.BaseAddress = new Uri("http://127.0.0.1:5080"))
    .AddHttpMessageHandler<ApiKeyHandler>();
var app = builder.Build();
app.MapGet("/echo", (HttpRequest request) => $"X-Api-Key: {request.Headers["X-Api-Key"]}");
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient("partner").GetStringAsync("/echo"));
app.Run();

public class ApiKeyHandler(IConfiguration configuration) : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        request.Headers.Add("X-Api-Key", configuration["Partner:ApiKey"] ?? "dev-key");
        return base.SendAsync(request, cancellationToken);
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0#outgoing-request-middleware)

## Defaults for every client

Since .NET 8, `ConfigureHttpClientDefaults` applies settings to every client the factory creates: named, typed, and unnamed. Use it for policies that should never be forgotten, such as a resilience handler, a user agent, or a correlation handler. Per-client registrations can still add to or override them.

Avoid adding the same resilience handler both by default and on a specific client, because the strategies would nest. The example gives every client the standard resilience pipeline and a user agent, so the typed client gets both without extra code.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.ConfigureHttpClientDefaults(http =>
{
    http.ConfigureHttpClient(client => client.DefaultRequestHeaders.UserAgent.ParseAdd("StudyApi/1.0"));
    http.AddStandardResilienceHandler();
});
builder.Services.AddHttpClient<EchoClient>(client => client.BaseAddress = new Uri("http://127.0.0.1:5080"));
var app = builder.Build();
app.MapGet("/echo", (HttpRequest request) => request.Headers.UserAgent.ToString());
app.MapGet("/proxy", (EchoClient echo) => echo.GetAgentAsync());
app.Run();

public class EchoClient(HttpClient http)
{
    public Task<string> GetAgentAsync() => http.GetStringAsync("/echo");
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience#add-resilience-to-all-http-clients)
