# Security Hardening — Drills

Predict the result before running the example.

## Review a CORS policy

A teammate wants a single-page app on any domain to call the API with the user's cookies, and writes this policy. What happens at startup or on the first CORS request, and what should the policy be?

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCors(options => options.AddDefaultPolicy(policy =>
    policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod().AllowCredentials()));
var app = builder.Build();
app.UseCors();
app.MapGet("/api/me", () => new { Name = "ada" });
app.Run();
```

**Answer**

The CORS services reject the combination of `AllowAnyOrigin` and `AllowCredentials` with an `InvalidOperationException` when the policy is built. Allowing it would let any website make cookie-authenticated calls and read the responses. List the real front-end origins with `WithOrigins(...)` and keep `AllowCredentials`. Or drop cookies and use bearer tokens.

## Spot the injection

Which of these three endpoints can be exploited with `?sort=Title; DROP TABLE Books` or `?title=x' OR '1'='1`? How would you fix it?

```csharp
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<LibraryDb>(options => options.UseSqlite("Data Source=library.db"));
var app = builder.Build();
app.MapGet("/a", (string title, LibraryDb db) => db.Books.Where(b => b.Title == title).ToListAsync());
app.MapGet("/b", (string title, LibraryDb db) =>
    db.Books.FromSql($"SELECT * FROM Books WHERE Title = {title}").ToListAsync());
app.MapGet("/c", (string sort, LibraryDb db) =>
    db.Books.FromSqlRaw($"SELECT * FROM Books ORDER BY {sort}").ToListAsync());
app.Run();

public class Book { public int Id { get; set; } public string Title { get; set; } = ""; }
public class LibraryDb(DbContextOptions<LibraryDb> options) : DbContext(options)
{
    public DbSet<Book> Books => Set<Book>();
}
```

**Answer**

`/a` and `/b` are safe: LINQ and `FromSql` both send the title as a parameter. `/c` is injectable. C# interpolation builds the SQL string before `FromSqlRaw` sees it, and a column name can't be a parameter anyway. Map `sort` to a fixed set of LINQ orderings, such as `"title" => OrderBy(b => b.Title)`, and reject anything else.
