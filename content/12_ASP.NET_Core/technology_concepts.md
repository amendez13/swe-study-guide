# ASP.NET Core

Build HTTP APIs on ASP.NET Core 10 and .NET 10. The course follows the chapter order of Andrew Lock’s *ASP.NET Core in Action*, third edition. The explanations, examples, and drills are original and use Microsoft's documentation for technical guidance. [Chapter structure](https://www.oreilly.com/library/view/asp-net-core-in/9781633438620/OEBPS/Text/ToC.htm) · [ASP.NET Core 10 documentation](https://learn.microsoft.com/en-us/aspnet/core/?view=aspnetcore-10.0)

## Run the C# examples

Install the [.NET 10 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/10.0). Run the commands below from a scratch directory. Each C# example is a complete replacement for the generated `Program.cs`. Stop the current app before swapping examples, and rebuild when changing static files that are included in the asset manifest.

```sh
dotnet new web --framework net10.0 -o StudyApi
cd StudyApi
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```

Use a browser for GET requests or call the sample URLs with `curl`. A few examples specify a file to create or a different environment to use. Try each drill before reading its answer.

## Course plan

- Introduction · chapter 1
- Part 1 · Minimal APIs, chapters 2–7
- [Part 2 · Complete applications](#12_ASP.NET_Core/08_Dependency_Injection), chapters 8–12
- Part 3 · Razor Pages and MVC, chapters 13–22
- Part 4 · Security and deployment, chapters 23–29
- Part 5 · Advanced ASP.NET Core, chapters 30–36
- Beyond the book · Blazor, SignalR, gRPC, Native AOT, HybridCache, output caching, and rate limiting

Start with [chapter 1](#12_ASP.NET_Core/01_Getting_Started). Chapters 1–12 are available now. The Notes tabs in chapters 11 and 12 list the extra packages and tools their examples need.

## Changes since .NET 7

- Chapter 4 uses `MapStaticAssets`, added in .NET 9, for assets discovered at build time. [Static files](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-10.0)
- Chapter 7 uses the form binding and antiforgery support added in .NET 8 and the opt-in Minimal API validation added in .NET 10. [ASP.NET Core 8 changes](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-8.0?view=aspnetcore-10.0) · [ASP.NET Core 10 validation](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/validation?view=aspnetcore-10.0)
- Chapter 9 uses built-in keyed DI registrations, added in .NET 8. [Keyed services](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0#keyed-services)
- Chapter 10 shows how the .NET 10 configuration binder preserves explicit JSON nulls. [Configuration null values](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/configuration-null-values-preserved)
- Chapter 11 uses built-in OpenAPI document generation, added in .NET 9. In .NET 10 it defaults to OpenAPI 3.1 and can include XML comments. [OpenAPI support](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview?view=aspnetcore-10.0)
- Later chapters will cover the Identity API endpoints added in .NET 8. [Identity endpoints](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity-api-authorization?view=aspnetcore-10.0)
