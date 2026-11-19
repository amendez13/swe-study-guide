# Endpoint Routing

## Endpoint selection and route precedence

Endpoint routing matches a request path and applies policies such as HTTP method matching. The selected endpoint carries a delegate and metadata that middleware can inspect before execution. The routing system is shared by Minimal APIs, Razor Pages, and controllers.

A literal segment is more specific than a parameter. `GET /rooms/new` selects the literal endpoint and `GET /rooms/east` selects the parameter endpoint. Avoid overlapping equally specific patterns with the same method because a request matching both can be ambiguous.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/rooms/{name}", (string name) => $"Room {name}");
app.MapGet("/rooms/new", () => "New room form");
app.MapPost("/rooms/new", () => TypedResults.NoContent());
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0)

## Optional segments and route defaults

A segment such as `{floor?}` can be omitted and leaves no value to bind; use a nullable handler parameter when the absence matters. A segment such as `{floor=1}` supplies a route value of `1` when omitted.

Try `/areas`, `/desks`, and `/desks/2`. The first uses its handler’s fallback label. The second gets a concrete default from the route, and the third uses the supplied value. A route default participates in URL generation as well as matching.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/areas/{floor?}", (int? floor) =>
    floor.HasValue ? $"Floor {floor}" : "All areas");
app.MapGet("/desks/{floor=1}", (int floor) => $"Desks on floor {floor}");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0)

## Route constraints and binding errors

A constraint such as `:int` narrows route selection. Use it to distinguish endpoints that share a path shape. A value that fails the constraint leaves that endpoint out of the candidate set.

If an endpoint with an unconstrained parameter is selected, an `int` handler parameter is converted later by [parameter binding](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/binding-sources). Here `/slots/blue` returns 404, while `/desks/blue` selects a route and returns 400 during binding.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/slots/{id:int}", (int id) => $"Slot {id}");
app.MapGet("/desks/{id}", (int id) => $"Desk {id}");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0)

## Catch-all route parameters

A catch-all parameter matches the remainder of the path and belongs at the end of the template. Use `{**path}` when you also want generated paths to preserve slashes within the route value.

Compare `/manual/setup/linux` with `/manual`. Treat a captured path as request data. If an endpoint uses it to select a file, enforce an explicit file-serving boundary.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/manual/{**path}", (string? path) => path ?? "Index");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0)

## Link generation and named results

Name an endpoint with `WithName` to give outbound link generation a stable identifier. `LinkGenerator.GetPathByName` creates a path from that name and route values; it returns null when no path can be generated. `RouteOptions` can set defaults for generated paths, such as lowercasing.

`TypedResults.CreatedAtRoute` uses a named route to fill the `Location` header of a 201 response. Compare the relative path at `GET /links` with the absolute URL in the header from `POST /titles`. The create endpoint uses a fixed identifier for demonstration.

```csharp
using Microsoft.AspNetCore.Routing;

var builder = WebApplication.CreateBuilder(args);
builder.Services.Configure<RouteOptions>(options => options.LowercaseUrls = true);
var app = builder.Build();
app.MapGet("/Titles/{id:int}", (int id) => new { Id = id }).WithName("ReadTitle");
app.MapGet("/links", (LinkGenerator links) =>
    links.GetPathByName("ReadTitle", new { id = 7 }) ?? "No link");
app.MapPost("/titles", () =>
    TypedResults.CreatedAtRoute(new { Id = 7 }, "ReadTitle", new { id = 7 }));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-10.0)
