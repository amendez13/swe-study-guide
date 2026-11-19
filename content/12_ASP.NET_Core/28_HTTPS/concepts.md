# HTTPS

## Why every app needs HTTPS

HTTPS encrypts traffic and authenticates the server, so a network observer can't read or modify requests and responses. Cookies, bearer tokens, form posts, and personal data all cross the connection, so any app with sign-in or private data needs it everywhere, not only on the login page. Browsers mark plain HTTP pages as not secure. Browser features such as service workers and some cookie settings require a secure context, and browsers support HTTP/2 only over HTTPS.

TLS can end at Kestrel or at a reverse proxy. Either way the app must know the original scheme, so it generates `https` links and sets secure cookies. Behind a proxy that means [forwarded headers](#12_ASP.NET_Core/27_Publishing_and_Deployment/concepts/run-behind-a-reverse-proxy-on-linux). `Request.IsHttps` reports the scheme the app sees.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/scheme", (HttpContext context) => new
{
    context.Request.Scheme,
    context.Request.IsHttps,
    Protocol = context.Request.Protocol
});
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0)

## The development certificate

The .NET SDK creates a self-signed localhost certificate for development, and Kestrel uses it automatically for `https://localhost` endpoints. `dotnet dev-certs https --trust` adds it to the trusted store so browsers accept it on Windows and macOS. On Linux, trust depends on the distribution and browser. `--check` reports its state, and `--clean` removes it so you can create a fresh one.

The certificate only covers `localhost`, so it is useless in production. Run the example with an HTTPS URL to see Kestrel pick it up without configuration. The project templates' `https` launch profile does the same.

```sh
dotnet dev-certs https --check --trust
dotnet dev-certs https --trust
dotnet run --no-launch-profile -- --urls "https://localhost:5443;http://localhost:5080"
```

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/", (HttpContext context) => $"secure: {context.Request.IsHttps}");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-dev-certs)

## A production certificate in Kestrel

When Kestrel terminates TLS itself, give it a certificate trusted by clients, usually from a public certificate authority such as Let's Encrypt. Configure it in the `Kestrel:Endpoints` section with a PEM certificate and key (`Path` and `KeyPath`), a PFX file and password, or a certificate store entry. Keep the password and key file out of source control: environment variables or a secret store fill those settings.

Configuration-based endpoints replace `--urls` and the port variables. `Kestrel:Certificates:Default` applies one certificate to every HTTPS endpoint that doesn't name its own. Certificates expire, so automate renewal and restart, or terminate TLS at a proxy that handles renewal for you.

```json
{
  "Kestrel": {
    "Endpoints": {
      "Https": {
        "Url": "https://0.0.0.0:443",
        "Certificate": {
          "Path": "/etc/ssl/catalog/fullchain.pem",
          "KeyPath": "/etc/ssl/catalog/privkey.pem"
        }
      }
    }
  }
}
```

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/", () => "catalog over TLS");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints?view=aspnetcore-10.0#configure-https)

## HTTP Strict Transport Security

HSTS is a response header, `Strict-Transport-Security`, that tells a browser to use only HTTPS for the site for a set time. After the first secure visit, the browser upgrades `http://` links itself and refuses to bypass certificate errors. That closes the gap where an attacker intercepts an initial plain-HTTP request. `UseHsts()` adds the header to HTTPS responses.

The templates call `UseHsts` only outside Development, because a cached HSTS policy for `localhost` would affect every local site. Configure `MaxAge`, `IncludeSubDomains`, and `Preload` with `AddHsts`. Increase the age gradually, and use preload only when every subdomain serves HTTPS, since removal from browser preload lists is slow.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHsts(options =>
{
    options.MaxAge = TimeSpan.FromDays(60);
    options.IncludeSubDomains = true;
});
var app = builder.Build();
if (!app.Environment.IsDevelopment()) app.UseHsts();
app.UseHttpsRedirection();
app.MapGet("/", () => "catalog");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0#http-strict-transport-security-protocol-hsts)

## HTTPS redirection

`UseHttpsRedirection()` answers plain HTTP requests with a redirect (307 by default) to the same URL over HTTPS. It must know the HTTPS port. It reads that from `HttpsRedirectionOptions.HttpsPort`, the `ASPNETCORE_HTTPS_PORT` or `ASPNETCORE_HTTPS_PORTS` settings, or the server's single HTTPS endpoint. If it can't find one, it logs a warning and doesn't redirect.

Behind a TLS-terminating proxy, every request reaches the app over HTTP. Run the forwarded headers middleware first, or the app will redirect every request in a loop. Use `RedirectStatusCode = 308` once the setup is stable, so clients keep the method and body and may cache the redirect.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 5443;
});
var app = builder.Build();
app.UseHttpsRedirection();
app.MapGet("/", () => "catalog");
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0#require-https)

## Reject HTTP in APIs

Redirects protect browsers, but API clients may already have sent credentials in the first plain request, and many clients don't follow redirects for POST. Microsoft's guidance for APIs is not to listen on HTTP at all, or to close the HTTP port, or to reject plain requests with 400 rather than redirect. HSTS is ignored by most non-browser clients.

The simplest fix is configuration: bind only an HTTPS endpoint. If HTTP must stay open, for example for health probes, reject other plain requests early. The middleware below returns 400 for any non-HTTPS request except `/healthz`.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.Use(async (context, next) =>
{
    if (!context.Request.IsHttps && context.Request.Path != "/healthz")
    {
        context.Response.StatusCode = StatusCodes.Status400BadRequest;
        await context.Response.WriteAsync("HTTPS required");
        return;
    }
    await next();
});
app.MapGet("/healthz", () => "ok");
app.MapGet("/api/books", () => new[] { "Atlas" });
app.Run();
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0#api-projects)
