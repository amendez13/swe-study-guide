# Middleware

## Middleware execution order

Middleware runs in registration order on the way to an endpoint. A component that awaits the next delegate resumes on the way back, so outer middleware can measure downstream work or use a callback to add headers when the response starts.

Register the middleware that needs to observe downstream work before that work. Watch the console for `GET /` in this example. Once the response has started, changing its headers may fail, so schedule late header changes with `Response.OnStarting`.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.Use(async (context, next) =>
{
    Console.WriteLine("Entering");
    await next(context);
    Console.WriteLine($"Leaving {context.Response.StatusCode}");
});
app.MapGet("/", () => "Reading room");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-10.0)

## Short-circuit a request

A middleware component short-circuits a request when it writes the response and omits the next call. This is useful for local maintenance pages or when a component can finish the entire HTTP exchange itself.

Try `/` and `/ready`. The scoped condition keeps the readiness endpoint reachable. The overload `app.Run(RequestDelegate)` registers terminal middleware, while the parameterless `app.Run()` starts the application.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.Use(async (context, next) =>
{
    if (context.Request.Path == "/")
    {
        context.Response.StatusCode = 503;
        await context.Response.WriteAsync("Reading room opens soon");
        return;
    }
    await next(context);
});
app.MapGet("/ready", () => "ready");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-10.0)

## Build-time and runtime static files

Create `wwwroot/notice.txt` before building, then request `/notice.txt`. `MapStaticAssets` maps endpoints from the build or publish manifest and enables optimized asset delivery, including fingerprinted URLs and compression for supported assets.

.NET 7 served ordinary local static files through `UseStaticFiles`. On .NET 10 use `MapStaticAssets` for known build-time assets and `UseStaticFiles` when you need a runtime file provider or files absent from the manifest. Keep private data outside paths configured for public serving.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapStaticAssets();
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-10.0)

## Exception handling by environment

The developer exception page is enabled automatically in Development with `WebApplication.CreateBuilder`. It shows diagnostic details for a thrown exception and belongs in a local environment. In other environments, configure `UseExceptionHandler` early so it can catch failures downstream before the response starts.

Run the example with `ASPNETCORE_ENVIRONMENT=Production` and request `/reading`. The middleware and registered problem details service can return a generic 500 response. Use the server logs to diagnose the exception. The [problem details card](#12_ASP.NET_Core/05_JSON_APIs_with_Minimal_APIs/concepts/problem-details-for-api-errors) covers expected API errors and bare status codes.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddProblemDetails();
var app = builder.Build();
if (!app.Environment.IsDevelopment())
    app.UseExceptionHandler();

app.MapGet("/reading", Fail);
app.Run();

static string Fail() => throw new InvalidOperationException("Catalog unavailable");
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling?view=aspnetcore-10.0)
