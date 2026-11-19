# Razor Views

## Razor templates

A Razor view is a `.cshtml` file that mixes HTML with C#. The Razor SDK compiles each view into a C# class during the build, so syntax errors in markup show up as build errors. Razor Pages and MVC views use the same syntax. A page also has `@page` and can have a page model, while a view is rendered by a controller or another page.

`@{ ... }` holds statements, and `@` before an expression writes its value. Use a code-behind page model for logic and keep the template focused on output. ASP.NET Core 10 marks Razor runtime compilation obsolete. To see markup edits without a restart, use Hot Reload with `dotnet watch` instead of `AddRazorRuntimeCompilation`.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();
```

```cshtml
@* Pages/Today.cshtml *@
@page
@{
    var opens = new TimeOnly(9, 0);
    var hours = 8;
}
<p>Opens at @opens, closes at @opens.AddHours(hours).</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor?view=aspnetcore-10.0)

## Pass data to a view

`@model` makes a view strongly typed, so `Model` has the page model's or view model's type and IntelliSense and the compiler check every member. `ViewData` is a string-keyed dictionary for data that isn't part of the model. The most common use is the page title, which a layout reads. Marking a page-model property with `[ViewData]` copies it into `ViewData` under the property's name.

Prefer the model for anything the page renders. Use `ViewData` for small values shared with layouts and partials. Request `/Branch` to see both: the heading comes from `Model` and the title from `ViewData`. MVC controllers also have `ViewBag`, a dynamic wrapper over the same dictionary.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();

public class BranchModel : PageModel
{
    [ViewData] public string Title { get; set; } = "";
    public string Name { get; private set; } = "";

    public void OnGet() => (Name, Title) = ("East branch", "East branch hours");
}
```

```cshtml
@* Pages/Branch.cshtml *@
@page
@model BranchModel
<title>@ViewData["Title"]</title>
<h1>@Model.Name</h1>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/overview?view=aspnetcore-10.0#pass-data-to-views)

## C# expressions and encoding

An implicit expression is `@` followed by a C# expression with no spaces, such as `@title.Length`. Use the explicit form `@( ... )` when the expression has spaces, operators, or generics, or when text follows straight after it. `@@` writes a literal `@`. Razor treats a pattern like `ada@example.org` as text, not code.

Every value Razor writes is HTML-encoded, so `<`, `>`, `&`, and quotes become entities. That is the first defense against cross-site scripting. The query string in this example can't inject markup: request `/Echo?text=<b>hi</b>` and view the source.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();
```

```cshtml
@* Pages/Echo.cshtml *@
@page
@{ var text = HttpContext.Request.Query["text"].ToString(); }
<p>You sent @text (@(text.Length * 2) bytes as UTF-16).</p>
<p>Write to desk@@example.org or ada@example.org.</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor?view=aspnetcore-10.0#razor-syntax)

## Loops and conditionals

Razor's control structures are C# statements prefixed with `@`: `@if`, `@foreach`, `@for`, `@switch`, `@while`, and `@using`. Inside their braces, an HTML tag switches back to markup, and `@` switches to C# again. A line of plain text without a tag can be wrapped in `<text>`, which renders only its content.

Request `/Loans`. The loop writes one list item per loan, and the `switch` picks the status text. Keep any filtering or sorting in the page model. The template should only decide how each item looks.

```csharp
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();

public record Loan(string Title, int DaysLeft);

public class LoansModel : PageModel
{
    public Loan[] Loans { get; } = [new("Atlas", 3), new("Primer", 0), new("Almanac", -2)];
}
```

```cshtml
@* Pages/Loans.cshtml *@
@page
@model LoansModel
@if (Model.Loans.Length == 0) { <p>No loans.</p> }
<ul>
    @foreach (var loan in Model.Loans)
    {
        <li>@loan.Title:
            @switch (loan.DaysLeft)
            {
                case > 0: <text>due in @loan.DaysLeft days</text> break;
                case 0: <strong>due today</strong> break;
                default: <em>overdue</em> break;
            }
        </li>
    }
</ul>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor?view=aspnetcore-10.0#control-structures)

## Raw HTML output

`@Html.Raw(value)` writes a string without encoding. So does any `IHtmlContent`, such as `HtmlString`. Use it only for markup you produced or sanitized yourself, such as HTML rendered from trusted Markdown. Raw user input lets a visitor run script in other users' browsers.

The example renders the same string twice. The encoded line shows the tags as text, and the raw line renders them as bold. When you need HTML from user input, sanitize it with an allow-list library before writing it raw.

```csharp
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();

public class NoticeModel : PageModel
{
    public string Notice { get; } = "Closed <strong>Monday</strong>";
}
```

```cshtml
@* Pages/Notice.cshtml *@
@page
@model NoticeModel
<p>@Model.Notice</p>
<p>@Html.Raw(Model.Notice)</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/security/cross-site-scripting?view=aspnetcore-10.0)

## Layouts and sections

A layout holds markup that every page shares, such as the `<head>`, navigation, and footer. It calls `@RenderBody()` where each page's content goes. A page selects a layout with `Layout = "_Layout"`, and Razor looks for it in the page's folder and its parent folders, then in `Pages/Shared`. Layouts can nest: a layout can have its own `Layout`.

Sections let a page fill other named slots in the layout. The layout calls `@RenderSection("Aside", required: false)`, and the page supplies `@section Aside { ... }`. A required section that a page omits causes a runtime error. A section that the page defines but the layout never renders also causes one. Request `/Visit` to see the page's content inside the layout.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();
```

```cshtml
@* Pages/Shared/_Layout.cshtml *@
<!DOCTYPE html>
<html><body>
    <header>City Library</header>
    <main>@RenderBody()</main>
    <aside>@RenderSection("Aside", required: false)</aside>
</body></html>
```

```cshtml
@* Pages/Visit.cshtml *@
@page
@{ Layout = "_Layout"; }
<p>Visiting hours are 9 to 5.</p>
@section Aside { <p>Free entry on Sundays.</p> }
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/layout?view=aspnetcore-10.0)

## Partial views

A partial view is a reusable piece of markup with no `@page`, conventionally named with a leading underscore. The Partial Tag Helper `<partial name="_BookCard" model="book" />` renders it with its own model. Razor finds it with the same search as layouts: the page's folder and its parents, then `Pages/Shared`. Without a `model` attribute the partial receives the parent's model.

Partials remove repeated markup. They have no handler or logic of their own, so the parent must prepare all their data. When a fragment needs to load its own data, use a view component instead. Request `/Shelf` to render one partial per book.

```csharp
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();

public record Book(string Title, string Author);

public class ShelfModel : PageModel
{
    public Book[] Books { get; } = [new("Atlas", "Ortelius"), new("Primer", "Lovelace")];
}
```

```cshtml
@* Pages/Shared/_BookCard.cshtml *@
@model Book
<article><h2>@Model.Title</h2><p>by @Model.Author</p></article>
```

```cshtml
@* Pages/Shelf.cshtml *@
@page
@model ShelfModel
@foreach (var book in Model.Books) { <partial name="_BookCard" model="book" /> }
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/partial?view=aspnetcore-10.0)

## _ViewStart and _ViewImports

`_ViewStart.cshtml` runs before every page or view in its folder and subfolders. The templates use it for one line, `@{ Layout = "_Layout"; }`, so pages don't each set a layout. `_ViewImports.cshtml` holds directives shared by every view below it: `@using`, `@addTagHelper`, `@namespace`, `@model`, and `@inject`. Razor applies every `_ViewImports` from the root down to the view's folder. A deeper file adds to the ones above it.

This version of `Pages/_ViewImports.cshtml` keeps the Tag Helpers line from the course setup and adds a namespace import and an injected service. Every page under `Pages` can then use `CultureInfo` and `Clock` without declaring them.

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.Services.AddSingleton(TimeProvider.System);
var app = builder.Build();
app.MapRazorPages();
app.Run();
```

```cshtml
@* Pages/_ViewImports.cshtml *@
@using System.Globalization
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers
@inject TimeProvider Clock
```

```cshtml
@* Pages/Clock.cshtml *@
@page
<p>@Clock.GetUtcNow().ToString("D", CultureInfo.GetCultureInfo("fr-FR"))</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/layout?view=aspnetcore-10.0#importing-shared-directives)
