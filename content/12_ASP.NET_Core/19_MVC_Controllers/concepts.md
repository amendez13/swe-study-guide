# MVC Controllers

## A first MVC application

An MVC app groups related actions into controller classes and keeps their views under `Views/{Controller}`. `AddControllersWithViews` registers controllers, Razor views, Tag Helpers, and antiforgery. `MapControllerRoute` adds a conventional route. The `mvc` template's pattern, `{controller=Home}/{action=Index}/{id?}`, maps `/` to `HomeController.Index` and `/Books/Details/3` to `BooksController.Details(3)`. `MapDefaultControllerRoute()` is a shorthand for that pattern.

Since .NET 9 the template also calls `MapStaticAssets` and chains `.WithStaticAssets()` on the controller route, just as the Razor Pages template does. A class is a controller when its name ends in `Controller` or it derives from `Controller`. Its public methods are actions. Request `/` and `/Home/Index`. Both render the same view.

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
var app = builder.Build();
app.MapStaticAssets();
app.MapControllerRoute("default", "{controller=Home}/{action=Index}/{id?}")
    .WithStaticAssets();
app.Run();

public class HomeController : Controller
{
    public IActionResult Index() => View();
}
```

```cshtml
@* Views/Home/Index.cshtml *@
<h1>City Library</h1>
<p>Served by @ViewContext.RouteData.Values["controller"].@ViewContext.RouteData.Values["action"]</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/overview?view=aspnetcore-10.0)

## Controllers compared with page models

A controller action and a page handler do the same job: bind input, call application services, and return an `IActionResult`. The difference is how they are organized. A page model serves one URL with a handler per verb, and its properties are the view model. A controller serves many URLs, one action each, and passes a separate view model to `View(model)`.

Both use the same model binding, validation, filters, and result types. That is why this action reads like a page handler, with `NotFound()` in place of an empty page. Request `/Books/Details/1` and `/Books/Details/5`. Constructor injection works the same way in both.

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
var app = builder.Build();
app.MapDefaultControllerRoute();
app.Run();

public record BookView(int Id, string Title);

public class BooksController : Controller
{
    private static readonly Dictionary<int, string> Titles = new() { [1] = "Atlas", [2] = "Primer" };

    public IActionResult Details(int id) =>
        Titles.TryGetValue(id, out var title) ? View(new BookView(id, title)) : NotFound();
}
```

```cshtml
@* Views/Books/Details.cshtml *@
@model BookView
<h1>@Model.Title</h1>
<p>Catalog number @Model.Id</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/actions?view=aspnetcore-10.0)

## Selecting a view

`View()` with no name renders the view named after the action. Razor looks in `Views/{Controller}/{Action}.cshtml`, then in `Views/Shared/{Action}.cshtml`, and the first match wins. `View("Retired", model)` chooses another name with the same search. A path starting with `~/` or `/` skips the search. If no file matches, the request fails with an error that lists every location Razor tried.

Shared views suit markup that several controllers use, such as an error or empty-state page. Request `/Books/Show/1`, which renders `Views/Books/Show.cshtml`. Then request `/Books/Show/2`, which finds the shared `Retired` view.

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
var app = builder.Build();
app.MapDefaultControllerRoute();
app.Run();

public class BooksController : Controller
{
    public IActionResult Show(int id) => id == 2 ? View("Retired", "Primer") : View(model: "Atlas");
}
```

```cshtml
@* Views/Books/Show.cshtml *@
@model string
<h1>@Model is on the shelf</h1>
```

```cshtml
@* Views/Shared/Retired.cshtml *@
@model string
<h1>@Model has been retired</h1>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/overview?view=aspnetcore-10.0#view-discovery)

## Choosing Razor Pages or MVC

Razor Pages suits page-focused UI. Each URL has one file for markup and one class for its logic, and adding a page doesn't touch a shared controller. Microsoft's docs describe it as easier and more productive for those scenarios. MVC controllers suit an existing MVC codebase. They also fit a set of actions that share a lot of setup, or a team that prefers grouping by resource over grouping by page. For new interactive UI, look at Blazor.

You don't have to pick only one. One app can map both, because they share services, routing, and the Razor view engine. Request `/Hours` for the page and `/Catalog/Count` for the controller. Each reads the same singleton service. Both register with `AddControllersWithViews` plus `AddRazorPages`, or with `AddMvc`, which registers both.

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
builder.Services.AddRazorPages();
builder.Services.AddSingleton<Catalog>();
var app = builder.Build();
app.MapRazorPages();
app.MapDefaultControllerRoute();
app.Run();

public class Catalog { public int Count => 3; }

public class CatalogController(Catalog catalog) : Controller
{
    public IActionResult Count() => Content($"{catalog.Count} titles");
}
```

```cshtml
@* Pages/Hours.cshtml *@
@page
@inject Catalog Catalog
<p>Open 9 to 5 with @Catalog.Count titles.</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/razor-pages/?view=aspnetcore-10.0)
