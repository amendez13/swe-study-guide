# Minimal API Binding and Validation

## Binding sources

Binding converts request data and services into handler arguments. A simple parameter named in the route template comes from the route by default; a simple parameter outside the template generally comes from the query string. Use attributes when readers need to see the source or when the incoming name differs.

This handler reads a route value, query string, and header independently. Try `/shelves/6?q=history` with the header `X-Branch: east`. Omit `id` by using an unmatched path, or supply a non-number to see the distinction in [route constraints and binding errors](#12_ASP.NET_Core/06_Endpoint_Routing/concepts/route-constraints-and-binding-errors).

```csharp
using Microsoft.AspNetCore.Mvc;

var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/shelves/{id}", (int id, [FromQuery(Name = "q")] string? term,
    [FromHeader(Name = "X-Branch")] string? branch) => new { id, term, branch });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## JSON request bodies

On a typical POST route an unregistered complex parameter is inferred as a JSON body, and `[FromBody]` can make the contract explicit. GET, HEAD, OPTIONS, and DELETE handlers do not infer a JSON body. A handler can read one body model and group multiple related fields inside it.

Send `{"title":"Notes","pages":13}` to `/journals` with `Content-Type: application/json`. A malformed JSON document normally produces 400, and an unsupported body media type produces 415. A successfully deserialized request can still fail [validation rules](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/automatic-minimal-api-validation).

```csharp
using Microsoft.AspNetCore.Mvc;

var app = WebApplication.CreateBuilder(args).Build();
app.MapPost("/journals", ([FromBody] Journal journal) => TypedResults.Ok(journal));
app.Run();

record Journal(string Title, int Pages);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Array parameters

A query array represents repeated values under one name. For example, `/search?tag=art&tag=history` binds two strings. A JSON array is useful when each element is a structured object, or when the collection naturally belongs in the body of a write request.

Compare the query with a POST to `/reading-order` containing `[{ "title": "Journal" }]`. Conversion is per element, so a non-numeric value in a query array declared as `int[]` causes the request to fail binding.

```csharp
using Microsoft.AspNetCore.Mvc;

var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/search", ([FromQuery] string[] tag) => TypedResults.Ok(tag));
app.MapPost("/reading-order", ([FromBody] ReadingEntry[] entries) =>
    TypedResults.Ok(new { Count = entries.Length }));
app.Run();

record ReadingEntry(string Title);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Optional and default parameters

A nullable handler parameter can represent an omitted route or query input. A parameter default supplies a concrete value on omission. If the client sends a malformed value for a typed parameter, conversion still fails.

Request `/catalog` to see the defaults and `/catalog?page=2&section=maps` to supply both values. Then request `/catalog?page=blue`. The parser rejects the supplied value before the handler runs.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/catalog", (string? section, int page = 1) =>
    new { Section = section ?? "all", Page = page });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Services and request objects

An explicitly registered type can be injected into a handler. `[FromServices]` documents that source and avoids ambiguity when a type might look like a request model. ASP.NET Core also supplies well-known values directly, including `HttpContext` and the request-aborted `CancellationToken`.

This endpoint declares a dependency and a request object in the same signature. When a handler performs asynchronous I/O, pass the request’s cancellation token to the operation. Since .NET 8, keyed registrations can be selected explicitly with `[FromKeyedServices]` when an app has multiple implementations.

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(new CatalogLabel("Main"));
var app = builder.Build();
app.MapGet("/catalog", ([FromServices] CatalogLabel label, HttpContext context,
    CancellationToken cancelled) => new
{
    label.Name,
    Method = context.Request.Method,
    Cancelled = cancelled.IsCancellationRequested
});
app.Run();

record CatalogLabel(string Name);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Multipart uploads and antiforgery

Use `IFormFile` to bind an upload from a `multipart/form-data` field. The field name matches the handler parameter. Since ASP.NET Core 8, form-bound Minimal API endpoints such as this one require antiforgery validation by default. Register antiforgery, add its middleware, and send the request token with the corresponding cookie.

First request `/upload-token` and retain its antiforgery cookie. Send the returned text in the `RequestVerificationToken` header and attach a small test file under the field `file`. The endpoint returns the uploaded length; a real upload feature also needs explicit limits and content handling.

```csharp
using Microsoft.AspNetCore.Antiforgery;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddAntiforgery();
var app = builder.Build();
app.UseAntiforgery();
app.MapGet("/upload-token", (HttpContext context, IAntiforgery antiforgery) =>
    antiforgery.GetAndStoreTokens(context).RequestToken!);
app.MapPost("/uploads", ([FromForm] IFormFile file) =>
    TypedResults.Ok(new { Bytes = file.Length }));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Custom binding with BindAsync

A custom type can define a public static `BindAsync(HttpContext)` method when its inputs need to be combined or normalized. A `TryParse` method is a smaller option when the type comes from one string. Keep routine route, query, and header binding declarative.

This type reads and trims a custom header. Try a request with header `X-Branch: east` and then omit the header. Returning null for the required parameter signals a 400 binding failure, so the handler only sees successfully bound values.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/branch", (Branch branch) => branch.Value);
app.Run();

record Branch(string Value)
{
    public static ValueTask<Branch?> BindAsync(HttpContext context)
    {
        var value = context.Request.Headers["X-Branch"].ToString().Trim();
        return ValueTask.FromResult(value.Length == 0 ? null : new Branch(value));
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Group handler parameters with AsParameters

`[AsParameters]` gives related arguments a name and lets ASP.NET Core bind their members as separate handler parameters. The members can come from distinct sources, including route, query, and registered services.

Use it for a flat parameter bag. Use a body model for nested JSON. Send `/branches/4/titles?prefix=dot` in the example to see both members bound from different parts of the request.

```csharp
using Microsoft.AspNetCore.Mvc;

var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/branches/{branch}/titles", ([AsParameters] TitleQuery query) =>
    new { query.Branch, query.Prefix });
app.Run();

record struct TitleQuery([FromRoute] int Branch, [FromQuery] string? Prefix);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding?view=aspnetcore-10.0)

## Automatic Minimal API validation

Binding determines whether request data can become the expected C# types. Validation checks properties of those bound values. For example, JSON can bind a seat count of zero to an integer even though a reservation must include at least one seat.

ASP.NET Core 10 adds opt-in Minimal API validation. Call `AddValidation()` before `Build()` to validate supported endpoint models against DataAnnotations before the handler runs. Invalid input gets a 400 with validation details. In .NET 7 a common approach was a custom validation filter. Keep business rules such as checking available capacity in application code.

```csharp
using System.ComponentModel.DataAnnotations;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddValidation();
var app = builder.Build();
app.MapPost("/reservations", (Reservation input) => TypedResults.Ok(input));
app.Run();

public sealed class Reservation
{
    [Required] public string? Room { get; init; }
    [Range(1, 12)] public int Seats { get; init; }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/validation?view=aspnetcore-10.0)
