# Logging

ASP.NET Core logs through `ILogger`. Code chooses levels, categories, and structured templates, and configuration chooses providers and filters.

## Key points

- Inject `ILogger<T>` so the category matches the class. Pick the level by severity and pass exceptions as the first argument.
- Use message templates with named placeholders, or `[LoggerMessage]` methods, never string interpolation.
- Configure verbosity with `Logging:LogLevel` and add context with scopes. Use JSON or OpenTelemetry output in production.

## Example

Run the [log scopes example](#12_ASP.NET_Core/26_Logging/concepts/log-scopes) and trigger a renewal. Both JSON lines carry `LoanId` in their scopes.

```sh
curl -i -X POST http://127.0.0.1:5080/loans/9/renew
```

Raise one category's verbosity without editing files.

```sh
Logging__LogLevel__LoanService=Debug dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```
