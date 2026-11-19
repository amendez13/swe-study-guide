# Logging — Drills

Predict the result before running the example.

## Which lines appear?

The app uses the configuration below. A request to `/loans` runs the service. Which of the three messages reach the console?

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "LoanService": "Information"
    }
  }
}
```

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<LoanService>();
var app = builder.Build();
app.MapGet("/loans", (LoanService loans, ILogger<Program> logger) =>
{
    logger.LogInformation("Endpoint hit");
    return loans.Count();
});
app.Run();

public class LoanService(ILogger<LoanService> logger)
{
    public int Count()
    {
        logger.LogDebug("Querying store");
        logger.LogInformation("Counted loans");
        return 3;
    }
}
```

**Answer**

Only `Counted loans` appears. `Endpoint hit` is in the `Program` category, which falls back to `Default` at `Warning`. `Querying store` is `Debug`, below the `Information` minimum set for `LoanService`.

## Fix a log call

A teammate writes the call below. What two problems does it have, and how should it be written?

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/fail/{id:int}", (int id, ILogger<Program> logger) =>
{
    try { throw new TimeoutException("store timed out"); }
    catch (Exception ex)
    {
        logger.LogError($"Loan {id} failed: {ex}");
        return Results.Problem();
    }
});
app.Run();
```

**Answer**

Interpolation builds the string even when the level is disabled, and it flattens `id` into text, so structured providers can't search for it. Passing the exception inside the message also loses its structured type and stack trace fields. Write `logger.LogError(ex, "Loan {LoanId} failed", id);`.
