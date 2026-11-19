# Testing ASP.NET Core Apps

Unit tests call middleware, handlers, and controllers directly. Integration tests run the real pipeline in memory with `TestServer` or `WebApplicationFactory`, with selected services and the database replaced.

## Key points

- Test middleware with a `DefaultHttpContext` and a `MemoryStream` body. Map Minimal API handlers to static methods that return `TypedResults`.
- `WebApplicationFactory<Program>` runs the real app. `ConfigureTestServices` replaces services, and a subclass keeps shared setup in one place. In .NET 10, `Program` is public without extra code.
- The EF Core in-memory provider isn't relational. Prefer SQLite in memory with one open connection, or the real engine in a container.

## Example

Set up the solution as in [chapter 35](#12_ASP.NET_Core/35_Testing_with_xUnit), then add the testing packages and run the [WebApplicationFactory tests](#12_ASP.NET_Core/36_Testing_ASP.NET_Core_Apps/concepts/test-the-whole-app-with-webapplicationfactory) against the handlers example.

```sh
dotnet add StudyApi.Tests package Microsoft.AspNetCore.Mvc.Testing --version '10.*'
dotnet test --filter "FullyQualifiedName~BooksApiTests"
```

`Microsoft.AspNetCore.Mvc.Testing` brings in `Microsoft.AspNetCore.TestHost`. The [database example](#12_ASP.NET_Core/36_Testing_ASP.NET_Core_Apps/concepts/isolate-the-database-in-tests) also needs `Microsoft.EntityFrameworkCore.Sqlite` in both projects and a `LibraryDb` registered in the app, as in [chapter 12](#12_ASP.NET_Core/12_Entity_Framework_Core).
