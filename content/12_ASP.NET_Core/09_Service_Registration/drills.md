# Service Registration — Drills

Predict the result before running the example.

## Predict the selected registration

What does `/preferred` return? What would change if the handler instead takes `IEnumerable<Label>` and returns every name?

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(new Label("Print"));
builder.Services.AddSingleton(new Label("Online"));
var app = builder.Build();
app.MapGet("/preferred", (Label label) => label.Name);
app.Run();

record Label(string Name);
```

**Answer**

The single service resolves to `Online`. The collection contains `Print` then `Online` because both registrations are included in registration order.

## Repair a captive dependency

The correct app below creates a new `Batch` per request. A teammate changes `RequestReport` to singleton. With scope validation enabled, what fails and where should the lifetime be fixed?

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<Batch>();
builder.Services.AddScoped<RequestReport>();
var app = builder.Build();
app.MapGet("/batch", (RequestReport report) => report.BatchId);
app.Run();

sealed class Batch { public Guid Id { get; } = Guid.NewGuid(); }
sealed class RequestReport(Batch batch) { public Guid BatchId => batch.Id; }
```

**Answer**

Scope validation rejects the singleton report's scoped constructor dependency. Keep the report scoped if it captures a request batch. If long-lived work needs a batch outside a request, create and dispose a scope for each operation.
