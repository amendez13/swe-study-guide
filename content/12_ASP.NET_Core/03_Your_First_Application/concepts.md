# Your First Application

## The Web SDK project

`dotnet new web` creates a small ASP.NET Core project. The `.csproj` selects `Microsoft.NET.Sdk.Web` and a target framework such as `net10.0`. The Web SDK includes the ASP.NET Core shared framework through an implicit framework reference. Add a package reference when an application needs a library beyond the shared framework.

`Program.cs` holds startup code. `appsettings.json` holds application defaults, `Properties/launchSettings.json` can define local launch profiles, and `wwwroot` is the conventional web root. Run `dotnet build` to restore dependencies if necessary and compile the example before serving it with `dotnet run`.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/version", () => new { Runtime = Environment.Version.ToString() });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/?view=aspnetcore-10.0)

## Build and run the application

`WebApplication.CreateBuilder(args)` initializes configuration, logging, and services. `Build()` produces the application, after which you configure its pipeline and map endpoints. The parameterless `Run()` starts the host and waits for shutdown.

Run with `dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080` to use a known local URL. The remaining arguments are passed to the app. Read `/environment` to see which deployment environment the host resolved.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/environment", () => app.Environment.EnvironmentName);
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/?view=aspnetcore-10.0)

## Register and consume a service

Register a dependency in `builder.Services` before `Build()`. An endpoint can receive it as a handler parameter. Explicit registration gives the host responsibility for providing the service and keeps the handler focused on the request.

A singleton is shared across requests, so this example uses an immutable label. A production service that holds request-specific data needs an appropriate lifetime. The [service and request parameters card](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/services-and-request-objects) shows how injection sits alongside request binding.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(new SiteLabel("North reading room"));
var app = builder.Build();
app.MapGet("/site", (SiteLabel site) => site.Name);
app.Run();

record SiteLabel(string Name);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0)

## Configure request handling in Program.cs

The host setup is the place to assemble request-wide behavior and endpoint-specific behavior. Register shared middleware with `Use`, and associate a handler with a method and path using `MapGet` or another mapping method.

This app stamps requests with a version header; the mapped handler owns the response payload. Compare the result of `GET /` with `GET /missing` to see which behavior applies across routes. Continue with the [middleware order card](#12_ASP.NET_Core/04_Middleware/concepts/middleware-execution-order).

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.Use((context, next) =>
{
    context.Response.Headers["X-Study-Version"] = "1";
    return next(context);
});
app.MapGet("/", () => new { Name = "Reading tracker" });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/?view=aspnetcore-10.0)
