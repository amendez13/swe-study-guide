# Publishing and Deployment — Drills

Predict the result before running the example.

## Find the client address behind nginx

nginx on the same machine forwards to the app with `X-Forwarded-For` and `X-Forwarded-Proto: https`. What does `/client` report without the middleware line, and with it? What changes if nginx runs on another host at 10.0.0.5?

```csharp
using Microsoft.AspNetCore.HttpOverrides;

var builder = WebApplication.CreateBuilder(args);
builder.Services.Configure<ForwardedHeadersOptions>(options =>
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto);
var app = builder.Build();
app.UseForwardedHeaders();
app.MapGet("/client", (HttpContext context) =>
    $"{context.Connection.RemoteIpAddress} via {context.Request.Scheme}");
app.Run();
```

**Answer**

Without `UseForwardedHeaders`, the app reports the loopback address and `http`. With it, the client's real address and `https` replace them, because loopback proxies are trusted by default. A proxy at 10.0.0.5 isn't trusted, so the headers are ignored again. Add it with `KnownProxies` or a `KnownIPNetworks` entry.

## Which port does the container use?

The image is built with `dotnet publish /t:PublishContainer` and started with `docker run -p 5080:8080 app`. Then a teammate adds `--urls http://+:9000` to the container's arguments. What happens to requests on host port 5080?

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/", () => "catalog");
app.Run();
```

**Answer**

At first the app listens on 8080, set by `ASPNETCORE_HTTP_PORTS` in the base image, so host port 5080 works. With `--urls`, Kestrel listens on 9000 instead and logs that it overrides the port settings. Nothing listens on 8080, so requests to host port 5080 fail. Map `-p 5080:9000` or drop the argument.
