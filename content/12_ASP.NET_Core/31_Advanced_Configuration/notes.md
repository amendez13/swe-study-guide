# Advanced Configuration

The pipeline is built from `Run`, `Map`, and `Use`, and anything larger becomes a middleware class. Options can be bound, configured from services, and validated at startup. A third-party container can replace the built-in one when you need its features.

## Key points

- `Run` ends the pipeline, `Map` and `MapWhen` branch it, `UseWhen` adds middleware and rejoins, and `Use` wraps the rest of the pipeline.
- Middleware classes are singletons: inject scoped services into `InvokeAsync`. Map middleware as an endpoint when it needs routing metadata.
- `AddOptions<T>()` chains binding, configuration with services, and validation. `ValidateOnStart` fails fast. `IConfigureOptions<T>` moves complex setup into a class.

## Example

Run the [OptionsBuilder example](#12_ASP.NET_Core/31_Advanced_Configuration/concepts/optionsbuilder), then override the port with an invalid value.

```sh
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
curl http://127.0.0.1:5080/smtp
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080 --Smtp:Port 0
```

The second run stops at startup with an `OptionsValidationException` naming `Port`. The [Autofac example](#12_ASP.NET_Core/31_Advanced_Configuration/concepts/use-a-third-party-di-container) needs `dotnet add package Autofac.Extensions.DependencyInjection`.
