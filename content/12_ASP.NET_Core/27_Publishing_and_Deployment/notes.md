# Publishing and Deployment

`dotnet publish` produces the deployment unit. A host such as IIS, systemd behind nginx, or a container runtime starts the app and often fronts it with a reverse proxy.

## Key points

- Publish framework-dependent where the server has the runtime, and self-contained where it doesn't. Since .NET 8, `dotnet publish` defaults to Release.
- Behind a proxy, enable the Forwarded Headers Middleware for known proxies only. .NET 10 uses `KnownIPNetworks`.
- Set URLs with `--urls`, `ASPNETCORE_URLS`, `ASPNETCORE_HTTP_PORTS`, or `Kestrel:Endpoints`. Container images default to port 8080 and a non-root user.

## Example

Publish the [run versus publish example](#12_ASP.NET_Core/27_Publishing_and_Deployment/concepts/run-versus-publish) and run it from the output folder.

```sh
dotnet publish -o ./publish
ASPNETCORE_ENVIRONMENT=Staging dotnet ./publish/StudyApi.dll --urls http://127.0.0.1:5080
curl -fsS http://127.0.0.1:5080/env
```

The [Linux service example](#12_ASP.NET_Core/27_Publishing_and_Deployment/concepts/run-as-a-linux-service) needs the systemd hosting package.

```sh
dotnet add package Microsoft.Extensions.Hosting.Systemd --version '10.*'
```
