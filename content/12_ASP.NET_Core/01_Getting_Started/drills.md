# Getting Started — Drills

Predict the result before running the example.

## Identify the response

For `GET /desks`, predict the status, media type, and JSON property names. Run `curl -i http://127.0.0.1:5080/desks` to check.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/desks", () => new { FreeDesks = 3 });
app.Run();
```

**Answer**

Expect 200 and a JSON media type. With the default web JSON settings, the body is `{"freeDesks":3}`. The anonymous C# object is serialized into the response.

## Choose an application shape

The team needs a browser page for volunteers and a machine-readable room count. Which endpoint is suitable for a script, and what would you use to grow the page into a multi-form site?

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/", () => TypedResults.Content("<p>Welcome</p>", "text/html"));
app.MapGet("/api/count", () => new { Count = 3 });
app.Run();
```

**Answer**

Use `/api/count` for the script because it returns a structured JSON value. Razor Pages is a natural fit for page-focused form workflows and can share this app’s host.
