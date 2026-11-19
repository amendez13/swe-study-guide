# Application Configuration

## Configuration keys and provider precedence

Configuration flattens hierarchical settings into keys such as `Bulletin:Heading`. Providers load values from different sources into one configuration view. If multiple providers supply a key, the last provider added wins for that key. Other keys can still come from earlier providers.

The in-memory providers make the merge visible. `/bulletin` returns the heading from the second provider and the page size from the first. A fresh web app already has providers from the host defaults. Position a custom provider according to what it should be allowed to override.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?>
{
    ["Bulletin:Heading"] = "Library news", ["Bulletin:PageSize"] = "8"
});
builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?>
{
    ["Bulletin:Heading"] = "Weekend news"
});
var app = builder.Build();
app.MapGet("/bulletin", (IConfiguration config) => new
{
    Heading = config["Bulletin:Heading"], Size = config.GetValue<int>("Bulletin:PageSize")
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-10.0)

## Default sources and hosting environments

`WebApplication.CreateBuilder` establishes the hosting environment before it loads environment-specific settings. With the default providers, later sources usually override earlier ones in this order from lowest to highest precedence: base JSON, environment JSON, Development user secrets, environment variables, and command-line arguments.

Run with `ASPNETCORE_ENVIRONMENT=Development` and no launch profile. The example reports the environment, and a value for `Bulletin__Heading` in the process environment becomes `Bulletin:Heading`. A command-line `--Bulletin:Heading=Evening` takes precedence over that variable.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/settings", (IConfiguration config, IWebHostEnvironment host) =>
    new { Environment = host.EnvironmentName, Heading = config["Bulletin:Heading"] });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-10.0)

## Development secrets and production overrides

Keep credentials out of committed settings files. In local Development, `dotnet user-secrets` can populate the default user-secrets provider. Its store is intended for development and is unencrypted. Production should supply credentials through the deployment platform's secret-management facilities.

This endpoint reports whether a value was configured. It omits the credential itself. Follow the [setup commands in the Notes tab](#12_ASP.NET_Core/10_Application_Configuration) with a disposable example value and confirm the endpoint changes when the setting is present.

```csharp
var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/catalog-settings", (IConfiguration config) => new
{
    HasCredential = !string.IsNullOrWhiteSpace(config["Catalog:ApiKey"])
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-10.0)

## Bind and validate typed options

Bind a configuration section to a class with public settable properties. Register the options with a section name, then inject `IOptions<T>`. This keeps string keys at the binding boundary and gives consumers properties with concrete types and defaults.

`ValidateOnStart` runs the registered checks during startup. Override `Bulletin__PageSize` with `0` to see the application reject the setting before it can serve traffic. For one-off binding, `configuration.GetSection("Bulletin").Get<BulletinOptions>()` gives a typed value without registering options or enabling their validation.

```csharp
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOptions<BulletinOptions>().BindConfiguration("Bulletin")
    .Validate(value => value.PageSize is >= 1 and <= 100, "PageSize must be 1–100")
    .ValidateOnStart();
var app = builder.Build();
app.MapGet("/page-size", (IOptions<BulletinOptions> options) => options.Value.PageSize);
app.Run();

sealed class BulletinOptions { public int PageSize { get; set; } = 10; }
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options?view=aspnetcore-10.0)

## Configuration reload and options lifetimes

A provider has to support change notifications for the app to observe file edits. `IOptions<T>` keeps its first value, `IOptionsSnapshot<T>` computes and caches a value within each scope, and `IOptionsMonitor<T>` exposes the latest value and can notify subscribers. Inject the monitor into a singleton that needs to react to updates.

Create `bulletin.json` with `{"Bulletin":{"Heading":"Morning"}}` and run the app. Change `Morning` to `Evening` and make a new request after the file watcher reloads. The snapshot reflects the edit on a new request. Other providers, such as the environment provider, do not watch for updates.

```csharp
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddJsonFile("bulletin.json", optional: false, reloadOnChange: true);
builder.Services.Configure<BulletinOptions>(builder.Configuration.GetSection("Bulletin"));
var app = builder.Build();
app.MapGet("/heading", (IOptionsSnapshot<BulletinOptions> options) => options.Value.Heading);
app.Run();

sealed class BulletinOptions { public string Heading { get; set; } = "News"; }
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options?view=aspnetcore-10.0)

## Explicit null in JSON settings

.NET 10 preserves explicit JSON nulls during configuration binding. A property with an initializer keeps that initializer when its setting is omitted, but a present null can replace it. Earlier versions could skip null values during binding or have providers convert null into a different value.

Create `nullable-settings.json` with `{"Bulletin":{"Heading":null}}` and request `/heading`. Replace it with `{"Bulletin":{"Enabled":true}}`, restart, and compare. The second payload keeps the initialized heading because the key is absent. The extra property still gives the binder a section to bind.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddJsonFile("nullable-settings.json", optional: false);
var app = builder.Build();
app.MapGet("/heading", (IConfiguration config) =>
    config.GetSection("Bulletin").Get<BulletinOptions>());
app.Run();

sealed class BulletinOptions
{
    public string? Heading { get; set; } = "Library news";
    public bool Enabled { get; set; }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/configuration-null-values-preserved)
