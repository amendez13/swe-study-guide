# Minimal API Binding and Validation — Drills

Predict the result before running the example.

## Distinguish absence from a bad value

Predict `GET /reports`, `GET /reports?limit=5`, and `GET /reports?limit=many`.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/reports", (int? limit) => new { Limit = limit ?? 10 });
app.Run();
```

**Answer**

The first two return 200 with limits of 10 and 5. The last returns 400 because the supplied value cannot become an integer.

## Diagnose two bad requests

Send well-formed JSON with `{"copies":0}`, then send malformed JSON with `{"copies":`. Both have `Content-Type: application/json`. Which stage rejects each request?

```csharp
using System.ComponentModel.DataAnnotations;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddValidation();
var app = builder.Build();
app.MapPost("/print", (PrintRequest input) => TypedResults.Ok(input));
app.Run();

public sealed class PrintRequest
{
    [Range(1, 50)] public int Copies { get; init; }
}
```

**Answer**

Zero binds to an integer, then fails the range rule. The malformed JSON fails during binding before validation can check any attributes. Neither invokes the handler.
