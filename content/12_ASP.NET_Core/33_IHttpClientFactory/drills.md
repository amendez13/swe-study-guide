# IHttpClientFactory — Drills

Predict the result before running the example.

## Handler order

Two handlers are added to the same client. What does `/proxy` return, and in what order do the log lines appear?

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("tagged", client => client.BaseAddress = new Uri("http://127.0.0.1:5080"))
    .AddHttpMessageHandler(services => new TagHandler("A"))
    .AddHttpMessageHandler(services => new TagHandler("B"));
var app = builder.Build();
app.MapGet("/echo", (HttpRequest request) => string.Join(",", request.Headers["X-Tag"].ToArray()));
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient("tagged").GetStringAsync("/echo"));
app.Run();

public class TagHandler(string name) : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token)
    {
        Console.WriteLine($"{name} out");
        request.Headers.Add("X-Tag", name);
        var response = await base.SendAsync(request, token);
        Console.WriteLine($"{name} back");
        return response;
    }
}
```

**Answer**

`/proxy` returns `A,B`. The log shows `A out`, `B out`, `B back`, `A back`. Handlers added first are outermost, so A sees the request first and the response last, like middleware.

## How many upstream calls?

`/flaky` fails with 503 on its first two calls and succeeds on the third. What does one request to `/proxy` return, and roughly how long does it take? The example needs the `Microsoft.Extensions.Http.Resilience` package.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient("upstream", client => client.BaseAddress = new Uri("http://127.0.0.1:5080"))
    .AddStandardResilienceHandler();
var app = builder.Build();
var calls = 0;
app.MapGet("/flaky", () => ++calls >= 3 ? Results.Ok($"call {calls}") : Results.StatusCode(503));
app.MapGet("/proxy", async (IHttpClientFactory factory) =>
    await factory.CreateClient("upstream").GetStringAsync("/flaky"));
app.Run();
```

**Answer**

It returns 200 with `"call 3"`. The standard handler retries 503 up to three times with exponential backoff and jitter, starting from a two-second base delay. Two retries take several seconds in all. Without the resilience handler, `GetStringAsync` would throw on the first 503 and the proxy would return 500.
