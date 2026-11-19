# Background Services

Hosted services run work alongside the web app: timers, queue consumers, and cache refreshers. Worker services run the same code without HTTP, and Quartz.NET adds cron schedules and clustering.

## Key points

- `BackgroundService.ExecuteAsync` runs long work, while the host awaits `StartAsync` before listening. In .NET 10, all of `ExecuteAsync` runs in the background.
- Hosted services are singletons. Create a scope per unit of work for scoped services, and catch exceptions so one failure doesn't stop the host.
- `dotnet new worker` builds a headless host. Quartz.NET schedules jobs with cron triggers, and its clustered persistent store fires each trigger on one instance.

## Example

Run the [Quartz schedule example](#12_ASP.NET_Core/34_Background_Services/concepts/schedule-a-job-with-quartz-net) and watch the log.

```sh
dotnet add package Quartz.Extensions.Hosting
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```

A report line appears at every ten-second mark, such as :00, :10, and :20, with the next fire time. To try the worker template, run `dotnet new worker -o LibraryWorker` and `dotnet run` in the new folder. The [production example](#12_ASP.NET_Core/34_Background_Services/concepts/run-workers-in-production) needs the `Microsoft.Extensions.Hosting.Systemd` and `Microsoft.Extensions.Hosting.WindowsServices` packages.
