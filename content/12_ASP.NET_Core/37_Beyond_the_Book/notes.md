# Beyond the Book

ASP.NET Core has grown beyond server-rendered pages and JSON APIs. These are short introductions to the features since .NET 7 that a modern app is most likely to use. Each card links to the full documentation.

## Key points

- Blazor builds interactive UI in C# with per-component render modes. SignalR pushes real-time messages, and gRPC gives typed, contract-first calls between services.
- Rate limiting and output caching are built-in middleware since .NET 7. `HybridCache` adds stampede protection over memory and distributed caches.
- Native AOT produces small, fast-starting executables for Minimal APIs. Aspire runs and observes multi-service apps from a C# app model.

## Example

Run the [output caching example](#12_ASP.NET_Core/37_Beyond_the_Book/concepts/output-caching) and evict the cache.

```sh
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
curl http://127.0.0.1:5080/time; echo
curl http://127.0.0.1:5080/time; echo
curl -X POST http://127.0.0.1:5080/time/reset
curl http://127.0.0.1:5080/time; echo
```

The first two timestamps match, and the one after the reset is new. The [HybridCache example](#12_ASP.NET_Core/37_Beyond_the_Book/concepts/hybridcache) needs `dotnet add package Microsoft.Extensions.Caching.Hybrid`. The Blazor, gRPC, Native AOT, and Aspire examples each start from their own template, named on the card.
