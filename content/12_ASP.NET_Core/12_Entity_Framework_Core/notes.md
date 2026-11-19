# Entity Framework Core

Use EF Core 10 and its SQLite provider to work with a local relational database. Use a fresh project for this topic so the two scratch databases are isolated.

## Key points

- Register a scoped context and choose a provider that matches the database.
- Materialize bounded queries. Use the context's tracked entities when making changes.
- Use migrations for a database whose schema must survive app updates.

## Example

Install the EF Core 10 provider in a fresh `net10.0` project. Run the [insert example](#12_ASP.NET_Core/12_Entity_Framework_Core/concepts/insert-a-record-and-return-its-identifier) using the [course setup](#12_ASP.NET_Core). Save the returned identifier for the read and update examples.

```sh
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version '10.*'
curl -i http://127.0.0.1:5080/rooms \
  -H 'Content-Type: application/json' -d '{"name":"Maps"}'
```

For the [migration example](#12_ASP.NET_Core/12_Entity_Framework_Core/concepts/define-and-apply-migrations), use a separate fresh project with the same provider. Add the EF design package and a local tool. Create and apply the first migration before running the app.

```sh
dotnet add package Microsoft.EntityFrameworkCore.Design --version '10.*'
dotnet new tool-manifest
dotnet tool install dotnet-ef --version '10.*'
dotnet ef migrations add InitialLibrary
dotnet ef database update
```

Add `public int OpenCapacity { get; set; }` to `Room`, then generate and review `AddOpenCapacity`. Use the generated migration to update the same database.

```sh
dotnet ef migrations add AddOpenCapacity
dotnet ef database update
```
