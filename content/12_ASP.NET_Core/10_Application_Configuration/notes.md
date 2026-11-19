# Application Configuration

Combine environment settings, files, and command-line overrides into one typed application configuration.

## Key points

- Providers resolve precedence per key. Hierarchical environment variable names use double underscores.
- Keep credentials outside committed configuration. Reload and validation are separate behaviors.
- Choose the options interface by the consumer's lifetime and freshness requirements.

## Example

Run the [hosting environment example](#12_ASP.NET_Core/10_Application_Configuration/concepts/default-sources-and-hosting-environments). The endpoint reports Development and the command-line heading.

```sh
ASPNETCORE_ENVIRONMENT=Development Bulletin__Heading=Afternoon \
  dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080 --Bulletin:Heading=Evening
# In a second shell:
curl -fsS http://127.0.0.1:5080/settings
```

For the [development secrets example](#12_ASP.NET_Core/10_Application_Configuration/concepts/development-secrets-and-production-overrides), run these commands in a scratch project, then request `/catalog-settings`.

```sh
dotnet user-secrets init
dotnet user-secrets set Catalog:ApiKey example-only-value
ASPNETCORE_ENVIRONMENT=Development \
  dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```
