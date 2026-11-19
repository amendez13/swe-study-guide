# Generic Host and Startup

Before .NET 6, apps built the generic host in `Program` and configured it in a `Startup` class. Minimal hosting replaced both with `WebApplication`, but the generic host still runs underneath, and `Startup` code is common in older apps.

## Key points

- `Host.CreateDefaultBuilder` plus `ConfigureWebHostDefaults` builds a web host. `Startup.ConfigureServices` registers services and `Startup.Configure` builds the pipeline, with explicit `UseRouting` and `UseEndpoints`.
- The `Startup` constructor can inject only configuration and environment types. `Configure` can inject any registered service.
- `WebApplicationBuilder` doesn't support `UseStartup`; call a `Startup` instance's methods yourself. `Host.CreateApplicationBuilder` is the non-web builder, and .NET 10 marks `WebHostBuilder` and `WebHost` obsolete.

## Example

Run the [Startup example](#12_ASP.NET_Core/30_Generic_Host_and_Startup/concepts/the-startup-class-configures-the-app) in both environments.

```sh
ASPNETCORE_ENVIRONMENT=Development dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
curl http://127.0.0.1:5080/
ASPNETCORE_ENVIRONMENT=Production dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
curl http://127.0.0.1:5080/
```

The first response is `Hi, developer` and the second is `Welcome`. The log line from `Configure` names the environment each time.
