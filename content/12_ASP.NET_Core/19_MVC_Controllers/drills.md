# MVC Controllers — Drills

Predict the result before running the example.

## Route conventional URLs

With the default route, which action handles `/`, `/Loans`, `/Loans/Renew/7`, and `/Loans/Renew`? What `id` does each `Renew` call receive?

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
var app = builder.Build();
app.MapDefaultControllerRoute();
app.Run();

public class HomeController : Controller
{
    public IActionResult Index() => Content("Home.Index");
}

public class LoansController : Controller
{
    public IActionResult Index() => Content("Loans.Index");
    public IActionResult Renew(int id) => Content($"Loans.Renew {id}");
}
```

**Answer**

`/` runs `Home.Index` because both defaults apply. `/Loans` runs `Loans.Index` because only the action default applies. `/Loans/Renew/7` binds `id` as 7. `/Loans/Renew` still matches because `{id?}` is optional, and `id` gets the `int` default of 0. Make the parameter `int?`, or add a `{id:int}` constraint, to tell those cases apart.

## Find the view

`/Reports/Summary` throws instead of rendering. Which paths did Razor search, and what are two ways to fix it?

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();
var app = builder.Build();
app.MapDefaultControllerRoute();
app.Run();

public class ReportsController : Controller
{
    public IActionResult Summary() => View();
}
```

```cshtml
@* Views/Report/Summary.cshtml *@
<h1>Summary</h1>
```

**Answer**

The view sits in `Views/Report` but the controller's name is `Reports`. Razor searched `/Views/Reports/Summary.cshtml` and `/Views/Shared/Summary.cshtml`, found neither, and threw an `InvalidOperationException` that lists both paths. Rename the folder to `Views/Reports`, or return `View("~/Views/Report/Summary.cshtml")`.
