# JSON APIs with Minimal APIs

## HTTP methods and route handlers

An HTTP API gives other programs a contract they can call independently of any user interface. Use GET for a read and POST when a client asks the server to create or process something. Keep a route’s method, URL, and response semantics consistent.

A Minimal API handler can be a lambda, local function, or method group. These two handlers share a URL and differ by HTTP method. The POST echoes the submitted title so you can observe how the framework reads a request and serializes the response.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/reading", ListReading);
app.MapPost("/reading", (ReadingItem item) =>
    TypedResults.Ok(item));
app.Run();

static ReadingItem[] ListReading() => [new("The study notebook")];

record ReadingItem(string Title);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0)

## Typed HTTP results and other response bodies

A string return value produces plain text. An ordinary object is serialized as JSON. `IResult` represents an HTTP result that can set status, headers, or media type. The `Results` helpers return `IResult`. `TypedResults` returns concrete result types that expose response metadata and are straightforward to assert in tests.

Use `Results<T1, T2>` to express multiple permitted concrete results from one handler. Try `/loan/1` and `/loan/2`. Other helpers handle downloads, redirects, or custom text, such as the CSV response below.

```csharp
using Microsoft.AspNetCore.Http.HttpResults;

var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/loan/{id}", Results<Ok<Loan>, NotFound> (int id) =>
    id == 1 ? TypedResults.Ok(new Loan(id)) : TypedResults.NotFound());
app.MapGet("/loans.csv", () =>
    TypedResults.Text("id\n1\n", "text/csv"));
app.Run();

record Loan(int Id);
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/responses?view=aspnetcore-10.0)

## Problem Details for API errors

Problem Details gives clients a JSON error envelope with fields such as `type`, `title`, `status`, and `detail`. Use `TypedResults.Problem` to describe an expected failure. Here an archive request conflicts with the reading list’s state.

`AddProblemDetails` registers a service that cooperating middleware can use. `UseStatusCodePages` supplies a Problem Details body for otherwise empty client or server errors when the response permits it. Compare `POST /archive` and `GET /missing`. Use [exception middleware](#12_ASP.NET_Core/04_Middleware/concepts/exception-handling-by-environment) to handle unhandled exceptions.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddProblemDetails();
var app = builder.Build();
app.UseStatusCodePages();
app.MapPost("/archive", () => TypedResults.Problem(
    statusCode: 409, title: "Reading list is in use"));
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0)

## Endpoint filter order and scope

An endpoint filter wraps the selected handler and can inspect its bound arguments. Like middleware, filters can return early or await the next delegate and inspect its result. Filters run in registration order before the handler and unwind in reverse order.

Choose a filter when the rule depends on handler arguments. Choose [middleware](#12_ASP.NET_Core/04_Middleware/concepts/middleware-execution-order) when it should apply across requests, including ones that never select this endpoint. Here a filter trims the name and rejects blank input.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/hello/{name}", (string name) => $"Hello, {name}")
    .AddEndpointFilter((context, next) =>
    {
        var name = context.GetArgument<string>(0).Trim();
        if (name.Length == 0)
            return ValueTask.FromResult<object?>(TypedResults.BadRequest());
        context.Arguments[0] = name;
        return next(context);
    });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/min-api-filters?view=aspnetcore-10.0)

## Reusable endpoint filters and route groups

Implement `IEndpointFilter` when several handlers share a rule. A filter attached to a route group applies to endpoints in that group. Group nesting composes path prefixes, and settings such as authorization metadata can be applied at group scope.

This filter uses only the request and can wrap handlers with different signatures. Request `/api/rooms` and `/api/rooms/1` and inspect their headers. An argument-based reusable filter needs a shared argument contract or a filter factory that checks the handler signature when the pipeline is constructed.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
var rooms = app.MapGroup("/api/rooms").AddEndpointFilter<RevisionFilter>();
rooms.MapGet("", () => new[] { 1, 2 });
rooms.MapGet("/{id}", (int id) => new { Id = id });
app.Run();

sealed class RevisionFilter : IEndpointFilter
{
    public ValueTask<object?> InvokeAsync(EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        context.HttpContext.Response.Headers["X-Api-Revision"] = "1";
        return next(context);
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0)
