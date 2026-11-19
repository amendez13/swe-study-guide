# Beyond the Book — Drills

Predict the result before running the example.

## The third request in a window

Call `/search` three times in quick succession. What status codes come back? What changes if you delete the `RejectionStatusCode` line?

```csharp
using Microsoft.AspNetCore.RateLimiting;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("search", window =>
    {
        window.PermitLimit = 2;
        window.Window = TimeSpan.FromSeconds(10);
    });
});
var app = builder.Build();
app.UseRateLimiter();
app.MapGet("/search", () => "results").RequireRateLimiting("search");
app.Run();
```

**Answer**

200, 200, 429. The window allows two requests, and the queue limit defaults to 0, so the third is rejected at once. After ten seconds the window resets. Without the `RejectionStatusCode` line, the third request gets the default 503 Service Unavailable, which clients may treat as an outage rather than a signal to slow down.

## Two requests to a cached clock

Request `/time` twice, five seconds apart. Then request it with an `Authorization` header. What timestamps do you see?

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOutputCache();
var app = builder.Build();
app.UseOutputCache();
app.MapGet("/time", () => DateTime.UtcNow.ToString("O")).CacheOutput();
app.Run();
```

```sh
curl http://127.0.0.1:5080/time
sleep 5; curl http://127.0.0.1:5080/time
curl -H 'Authorization: Bearer x' http://127.0.0.1:5080/time
```

**Answer**

The first two responses show the same timestamp, because the default policy caches the 200 response for 60 seconds. The third shows a new timestamp. The default policy doesn't serve or store cached responses for requests with an `Authorization` header, so one user's response can't leak to another.
