# Testing ASP.NET Core Apps — Drills

Predict the result before running the example.

## The empty response body

This test uses the `PingMiddleware` from the first card. Does it pass?

```csharp
// StudyApi.Tests/PingBodyDrill.cs
using Microsoft.AspNetCore.Http;

namespace StudyApi.Tests;

public class PingBodyDrill
{
    [Fact]
    public async Task Ping_writes_pong()
    {
        var context = new DefaultHttpContext();
        context.Request.Path = "/ping";

        await new PingMiddleware(_ => Task.CompletedTask).InvokeAsync(context);

        context.Response.Body.Position = 0;
        Assert.Equal("pong", await new StreamReader(context.Response.Body).ReadToEndAsync());
    }
}
```

**Answer**

It fails. A `DefaultHttpContext` starts with `Stream.Null` as its response body, so the middleware's write is discarded and the reader returns an empty string. Setting `Position` on `Stream.Null` is allowed and does nothing. Assign `context.Response.Body = new MemoryStream()` before calling the middleware.

## Duplicate ISBNs in two providers

`LibraryDb` has a unique index on `Book.Isbn`. The same test runs once with the EF Core in-memory provider and once with SQLite in memory. What happens on `SaveChanges` in each?

```csharp
public class Book
{
    public int Id { get; set; }
    public string Isbn { get; set; } = "";
}

public class LibraryDb(DbContextOptions<LibraryDb> options) : DbContext(options)
{
    public DbSet<Book> Books => Set<Book>();
    protected override void OnModelCreating(ModelBuilder model) =>
        model.Entity<Book>().HasIndex(b => b.Isbn).IsUnique();
}

// In the test, after EnsureCreated():
db.Books.Add(new Book { Isbn = "9780000000001" });
db.Books.Add(new Book { Isbn = "9780000000001" });
db.SaveChanges();
```

**Answer**

With the in-memory provider, `SaveChanges` succeeds and stores both rows, because that provider isn't relational and doesn't enforce unique indexes. With SQLite, it throws a `DbUpdateException` from the UNIQUE constraint. A test suite on the in-memory provider would miss the bug that production hits. That's why SQLite in memory, or the real engine, is the better choice.
