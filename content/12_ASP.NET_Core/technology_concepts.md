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

## Run the Razor Pages and MVC examples

From chapter 13, examples also include Razor files. Each `cshtml` block starts with a Razor comment that names its path in the project, such as `@* Pages/Index.cshtml *@`. Save the block at that path. The C# block still replaces `Program.cs`, and the page models and controllers are declared there. Run this once in the project so pages and views can use Tag Helpers.

```sh
mkdir -p Pages Views
printf '@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers\n' > Pages/_ViewImports.cshtml
cp Pages/_ViewImports.cshtml Views/_ViewImports.cshtml
```

Before each new example, delete the Razor files left by the previous one and keep the two `_ViewImports.cshtml` files.

```sh
find Pages Views -name '*.cshtml' ! -name _ViewImports.cshtml -delete
```

## Course plan

- Introduction · chapter 1
- Part 1 · Minimal APIs, chapters 2–7
- [Part 2 · Complete applications](#12_ASP.NET_Core/08_Dependency_Injection), chapters 8–12
- [Part 3 · Razor Pages and MVC](#12_ASP.NET_Core/13_Razor_Pages), chapters 13–22
- [Part 4 · Security and deployment](#12_ASP.NET_Core/23_Identity), chapters 23–29
- [Part 5 · Advanced ASP.NET Core](#12_ASP.NET_Core/30_Generic_Host_and_Startup), chapters 30–36
- [Beyond the book](#12_ASP.NET_Core/37_Beyond_the_Book) · Blazor, SignalR, gRPC, rate limiting, output caching, HybridCache, Native AOT, and Aspire

Start with [chapter 1](#12_ASP.NET_Core/01_Getting_Started). All chapters, 1–36, and the Beyond the book topic are available. The Notes tabs in chapters 11, 12, 23, 25, 27, and 31–37 list the extra packages and tools their examples need.

## Changes since .NET 7

- Chapter 4 uses `MapStaticAssets`, added in .NET 9, for assets discovered at build time. [Static files](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-10.0)
- Chapter 7 uses the form binding and antiforgery support added in .NET 8 and the opt-in Minimal API validation added in .NET 10. [ASP.NET Core 8 changes](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-8.0?view=aspnetcore-10.0) · [ASP.NET Core 10 validation](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/validation?view=aspnetcore-10.0)
- Chapter 9 uses built-in keyed DI registrations, added in .NET 8. [Keyed services](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0#keyed-services)
- Chapter 10 shows how the .NET 10 configuration binder preserves explicit JSON nulls. [Configuration null values](https://learn.microsoft.com/en-us/dotnet/core/compatibility/extensions/10.0/configuration-null-values-preserved)
- Chapter 11 uses built-in OpenAPI document generation, added in .NET 9. In .NET 10 it defaults to OpenAPI 3.1 and can include XML comments. [OpenAPI support](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview?view=aspnetcore-10.0)
- Chapters 13, 18, and 19 use the .NET 9 templates. These call `MapStaticAssets` and chain `WithStaticAssets()` on page and controller endpoints, so Razor writes fingerprinted asset URLs and `asp-append-version` is no longer needed. [Static files](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files?view=aspnetcore-10.0)
- Chapter 14 uses `LinkGenerator` outside pages and controllers. ASP.NET Core 10 marks `IActionContextAccessor` obsolete. [Breaking changes in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/overview?view=aspnetcore-10.0)
- Chapter 16 notes that the .NET 10 `AddValidation` applies to Minimal APIs only. Razor Pages and MVC keep their built-in validation. [Model validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation?view=aspnetcore-10.0)
- Chapter 17 uses Hot Reload because ASP.NET Core 10 marks Razor runtime compilation obsolete. [Breaking changes in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/overview?view=aspnetcore-10.0)
- Chapter 20 uses `dotnet new webapi --use-controllers`, because the .NET 10 template creates Minimal APIs by default. In .NET 10, `[ApiController]` endpoints protected by cookie authentication return 401 or 403 instead of redirecting. [ASP.NET Core 10 changes](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0)
- Chapter 22 points app-wide error handling to exception middleware with `IExceptionHandler`, added in .NET 8. [Handle errors](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling?view=aspnetcore-10.0)
- Chapter 23 uses the Identity API endpoints added in .NET 8 (`AddIdentityApiEndpoints` and `MapIdentityApi`). In .NET 10, Identity also supports passkeys. [Identity endpoints](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity-api-authorization?view=aspnetcore-10.0)
- Chapter 24 uses `AddAuthorizationBuilder`, added in .NET 7. It also covers the .NET 10 change that returns 401 and 403 instead of cookie login redirects for API endpoints. [Cookie redirects for API endpoints](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0)
- Chapter 25 describes bearer authentication with a document transformer in the built-in OpenAPI generator instead of Swashbuckle. In .NET 10 that generator uses OpenAPI.NET 2 types from the `Microsoft.OpenApi` namespace. [Customize OpenAPI documents](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi?view=aspnetcore-10.0)
- Chapter 26 uses `[LoggerMessage]` source-generated logging and the JSON console formatter in place of a third-party structured logging setup. [Compile-time logging](https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator)
- Chapter 27 covers `dotnet publish` defaulting to Release (.NET 8), `ASPNETCORE_HTTP_PORTS` and SDK container publishing (.NET 8), Ubuntu-based images (.NET 10), and `KnownIPNetworks` replacing the obsolete `KnownNetworks` (.NET 10). [Breaking changes in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/overview?view=aspnetcore-10.0)
- Chapter 29 relies on the antiforgery middleware that Minimal API form endpoints use since .NET 8. [Antiforgery](https://learn.microsoft.com/en-us/aspnet/core/security/anti-request-forgery?view=aspnetcore-10.0)
- Chapter 30 uses `Host.CreateApplicationBuilder`, added in .NET 7, for non-web hosts. ASP.NET Core 10 marks `WebHostBuilder`, `IWebHost`, and `WebHost` obsolete. [Breaking changes in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/overview?view=aspnetcore-10.0)
- Chapter 31 mentions the `[OptionsValidator]` source generator and built-in keyed services, both added in .NET 8. [Options validation](https://learn.microsoft.com/en-us/dotnet/core/extensions/options#options-validation)
- Chapter 32 notes that custom validation attributes also work in Minimal APIs through the .NET 10 `AddValidation`, and calls FluentValidation validators explicitly instead of through its automatic MVC integration. [Model validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation?view=aspnetcore-10.0)
- Chapter 33 uses `Microsoft.Extensions.Http.Resilience` (.NET 8) in place of `Microsoft.Extensions.Http.Polly`, and `ConfigureHttpClientDefaults` (.NET 8). [HTTP resilience](https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience)
- Chapter 34 notes that in .NET 10 the host runs all of `BackgroundService.ExecuteAsync` in the background. [.NET 10 breaking changes](https://learn.microsoft.com/en-us/dotnet/core/compatibility/10)
- Chapters 35 and 36 note the .NET 10 `.slnx` default for `dotnet new sln`, xUnit v3, Microsoft.Testing.Platform support in `dotnet test`, and the generated public `Program` class that `WebApplicationFactory<Program>` needs. [ASP.NET Core 10 changes](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0)
- Beyond the book covers features the book doesn't: Blazor render modes (.NET 8), rate limiting and output caching (.NET 7), HybridCache (.NET 9), Native AOT for ASP.NET Core (.NET 8), Server-Sent Events results (.NET 10), and Aspire. [What's new in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0)
