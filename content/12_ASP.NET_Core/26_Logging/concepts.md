# Logging

## Logging in a production app

In production you can't attach a debugger, so logs are the record of what the app did and why a request failed. Good logs answer specific questions: which request, which user or resource, what decision the code made, and what went wrong. ASP.NET Core already logs hosting, routing, and request failures. Add your own messages where your business logic makes decisions or meets errors.

Code writes through the `ILogger` abstraction from `Microsoft.Extensions.Logging`. `ILoggerFactory` creates loggers, and logging providers send each message to a destination. Because the app depends only on the abstraction, you can change destinations in configuration without touching call sites. POST to `/renew/5` and `/renew/0` and compare the console lines.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapPost("/renew/{loanId:int}", (int loanId, ILogger<Program> logger) =>
{
    if (loanId <= 0)
    {
        logger.LogWarning("Rejected renewal for invalid loan {LoanId}", loanId);
        return Results.BadRequest();
    }
    logger.LogInformation("Renewed loan {LoanId}", loanId);
    return Results.Ok();
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0)

## Log levels

Each message has a level: `Trace`, `Debug`, `Information`, `Warning`, `Error`, or `Critical`, in increasing severity. `None` is used only in filters, to turn a category off. Use `Information` for normal events worth keeping, `Warning` for unexpected but handled situations, and `Error` for failures of the current operation. `Critical` is for failures that take down the app or lose data.

Pass the exception as the first argument to `LogError` so providers record its type and stack trace. Don't interpolate it into the message. `Debug` and `Trace` are for diagnosis and are usually filtered out in production. Request `/report?fail=true` and look for the exception details in the console.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/report", (bool fail, ILogger<Program> logger) =>
{
    logger.LogDebug("Building report, fail={Fail}", fail);
    try
    {
        if (fail) throw new InvalidOperationException("Report source unavailable");
        return Results.Ok("report");
    }
    catch (InvalidOperationException ex)
    {
        logger.LogError(ex, "Report generation failed");
        return Results.Problem("Report unavailable");
    }
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0#log-level)

## Log categories

Every logger has a category, a string that names where messages come from. `ILogger<T>` uses the full name of `T`, such as `LoanService` or `Microsoft.AspNetCore.Routing.EndpointMiddleware`. `ILoggerFactory.CreateLogger("Name")` sets one explicitly. Filters match categories by prefix, so namespace-style names let you change verbosity for a whole area at once.

Inject `ILogger<T>` into each class with its own type so filters and log searches can target it. The console provider prints the category on each line. Request `/loans` and find the `LoanService` category in the output.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<LoanService>();
var app = builder.Build();
app.MapGet("/loans", (LoanService loans) => loans.Count());
app.Run();

public class LoanService(ILogger<LoanService> logger)
{
    public int Count()
    {
        logger.LogInformation("Counting active loans");
        return 3;
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0#log-category)

## Message templates and structured data

Log calls take a message template with named placeholders and the values as separate arguments: `LogInformation("Renewed loan {LoanId} for {Days} days", id, days)`. Arguments fill placeholders by position, not by name. Structured providers keep each value as a named property, so you can search for every event where `LoanId` is 42 rather than matching text.

Don't use string interpolation (`$"Renewed {id}"`) in log calls. The text is built even when the level is filtered out, and the properties are lost. Start this app with `--Logging:Console:FormatterName=json` to see `LoanId` and `Days` as separate JSON fields.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapPost("/loans/{loanId:int}/renew", (int loanId, int days, ILogger<Program> logger) =>
{
    logger.LogInformation("Renewed loan {LoanId} for {Days} days", loanId, days);
    return Results.Ok();
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0#log-message-template)

## Compile-time logging methods

The `[LoggerMessage]` source generator, available since .NET 6, turns a `partial` method declaration into an efficient logging method. You declare the event id, level, and template once. The generator writes code that checks whether the level is enabled before doing any work and avoids boxing the arguments. Call sites read like domain events: `log.LoanRenewed(id, days)`.

Prefer it for messages on hot paths and for any event you log from several places. Templates are checked at compile time, so a placeholder count that doesn't match the parameters is a build error. POST to `/loans/7/renew?days=14` to see the event with its id.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapPost("/loans/{loanId:int}/renew", (int loanId, int days, ILogger<Program> logger) =>
{
    logger.LoanRenewed(loanId, days);
    return Results.Ok();
});
app.Run();

static partial class LoanLog
{
    [LoggerMessage(EventId = 1001, Level = LogLevel.Information, Message = "Renewed loan {LoanId} for {Days} days")]
    public static partial void LoanRenewed(this ILogger logger, int loanId, int days);
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator)

## Logging providers

`WebApplication.CreateBuilder` adds the Console, Debug, and EventSource providers, plus EventLog on Windows. Call `builder.Logging.ClearProviders()` and add the ones you want. `AddJsonConsole()` writes one JSON object per line, which log collectors in containers can parse. Third-party libraries such as Serilog and NLog plug in as providers and add sinks for files and log services. OpenTelemetry's logging provider exports logs alongside traces and metrics.

Choose destinations per environment: readable text locally, and JSON or an OpenTelemetry exporter in production. The example replaces the defaults with the JSON console formatter and includes scopes and UTC timestamps.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddJsonConsole(options =>
{
    options.IncludeScopes = true;
    options.UseUtcTimestamp = true;
    options.TimestampFormat = "O";
});
var app = builder.Build();
app.MapGet("/", (ILogger<Program> logger) =>
{
    logger.LogInformation("Catalog opened at {Branch}", "East");
    return "ok";
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0#logging-providers)

## Filter log verbosity

Filters decide which messages reach providers by category prefix and minimum level. The `Logging:LogLevel` section of configuration sets them, and the most specific matching category wins. The templates set `Default` to `Information` and `Microsoft.AspNetCore` to `Warning`, which hides per-request framework noise. A provider section, such as `Logging:Console:LogLevel`, overrides the general rules for that provider only.

Because filters are configuration, you can raise verbosity with an environment variable such as `Logging__LogLevel__LoanService=Debug` without redeploying code. `builder.Logging.AddFilter` sets the same rules in code. With the settings below, `LoanService` debug messages appear while framework information is hidden.

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "LoanService": "Debug"
    }
  }
}
```

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<LoanService>();
var app = builder.Build();
app.MapGet("/loans", (LoanService loans) => loans.Count());
app.Run();

public class LoanService(ILogger<LoanService> logger)
{
    public int Count()
    {
        logger.LogDebug("Querying loan store");
        return 3;
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0#configure-logging)

## Log scopes

A scope attaches properties to every message logged inside it. `using (logger.BeginScope(new Dictionary<string, object> { ["LoanId"] = id }))` adds `LoanId` to each message in the block, including messages from services the block calls. ASP.NET Core already opens a scope per request with `RequestId`, `RequestPath`, and the trace and span ids.

Scopes appear only when a provider includes them. The JSON console formatter does so with `IncludeScopes`, as do structured providers. Use them for context shared by many messages, and keep values small. POST to `/loans/9/renew` and check that both messages carry `LoanId`.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Logging.AddJsonConsole(options => options.IncludeScopes = true);
builder.Services.AddSingleton<Notifier>();
var app = builder.Build();
app.MapPost("/loans/{loanId:int}/renew", (int loanId, ILogger<Program> logger, Notifier notifier) =>
{
    using (logger.BeginScope(new Dictionary<string, object> { ["LoanId"] = loanId }))
    {
        logger.LogInformation("Renewing loan");
        notifier.Send();
    }
    return Results.Ok();
});
app.Run();

public class Notifier(ILogger<Notifier> logger)
{
    public void Send() => logger.LogInformation("Renewal notice queued");
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging#log-scopes)
