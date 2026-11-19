# Filter Pipeline

## The MVC filter pipeline

Filters run code at fixed stages around an MVC action, after routing has chosen the endpoint. Authorization filters run first and can reject the request. Resource filters wrap almost everything else, including model binding. Action filters wrap the action method and can see the bound arguments. Exception filters handle exceptions from binding, action filters, and the action itself. Result filters wrap the execution of the result, such as rendering a view or writing JSON.

This filter implements four stage interfaces and appends a header at each stage. Request `/api/stages` and read the `X-Stage` headers in order. They are authorization, resource, action before, action, action after, and result before. The remaining "after" hooks run once the response has started, so they can't add headers.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers(options => options.Filters.Add<StageFilter>());
var app = builder.Build();
app.MapControllers();
app.Run();

public class StageFilter : IAuthorizationFilter, IResourceFilter, IActionFilter, IResultFilter
{
    static void Mark(FilterContext c, string stage) => c.HttpContext.Response.Headers.Append("X-Stage", stage);
    public void OnAuthorization(AuthorizationFilterContext c) => Mark(c, "authorization");
    public void OnResourceExecuting(ResourceExecutingContext c) => Mark(c, "resource");
    public void OnResourceExecuted(ResourceExecutedContext c) { }
    public void OnActionExecuting(ActionExecutingContext c) => Mark(c, "action before");
    public void OnActionExecuted(ActionExecutedContext c) => Mark(c, "action after");
    public void OnResultExecuting(ResultExecutingContext c) => Mark(c, "result before");
    public void OnResultExecuted(ResultExecutedContext c) { }
}

[ApiController]
public class StagesController : ControllerBase
{
    [HttpGet("/api/stages")]
    public string Get()
    {
        Response.Headers.Append("X-Stage", "action");
        return "done";
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#how-filters-work)

## The Razor Pages filter pipeline

Razor Pages has the same authorization, resource, exception, and result stages, but action filters don't run. Page filters take their place. `OnPageHandlerSelected` runs once a handler is chosen and before model binding. `OnPageHandlerExecuting` runs after binding and before the handler. `OnPageHandlerExecuted` runs after the handler returns. Page filters can be registered globally or on a page model class, but not on individual handler methods.

`PageModel` implements the page filter interfaces itself, so a page can override these methods for logic that belongs to that page only. Request `/Desk?id=4`. The selection hook sees `Id` still 0 because binding hasn't happened yet. The executing hook sees 4.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
var app = builder.Build();
app.MapRazorPages();
app.Run();

public class DeskModel : PageModel
{
    [BindProperty(SupportsGet = true)] public int Id { get; set; }
    public List<string> Log { get; } = [];

    public override void OnPageHandlerSelected(PageHandlerSelectedContext c) => Log.Add($"selected, id {Id}");
    public override void OnPageHandlerExecuting(PageHandlerExecutingContext c) => Log.Add($"executing, id {Id}");
    public void OnGet() => Log.Add("OnGet");
}
```

```cshtml
@* Pages/Desk.cshtml *@
@page
@model DeskModel
<p>@string.Join(" → ", Model.Log)</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/razor-pages/filter?view=aspnetcore-10.0)

## Filters or middleware

Middleware runs for every request, before and after endpoint routing, and sees only the `HttpContext`. Filters run only for MVC actions and Razor Pages. They can see MVC details: the selected action, bound arguments, `ModelState`, the page model, and the `IActionResult` before it executes. For Minimal APIs, [endpoint filters](#12_ASP.NET_Core/05_JSON_APIs_with_Minimal_APIs/concepts/endpoint-filter-order-and-scope) fill the same role.

Use middleware for cross-cutting work that doesn't depend on MVC, such as compression, CORS, or exception handling for the whole app. Use a filter when the logic needs MVC context or applies only to some controllers. In this example the middleware can read the path, but only the filter can read the bound `id` argument.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.Use(async (context, next) =>
{
    context.Response.Headers["X-Path"] = context.Request.Path.ToString();
    await next();
});
app.MapControllers();
app.Run();

public class ArgumentsHeaderAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext context) =>
        context.HttpContext.Response.Headers["X-Args"] =
            string.Join(",", context.ActionArguments.Select(a => $"{a.Key}={a.Value}"));
}

[ApiController]
public class CopiesController : ControllerBase
{
    [HttpGet("/api/copies/{id:int}"), ArgumentsHeader] public int Get(int id) => id;
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#use-middleware-in-the-filter-pipeline)

## A simple filter

The quickest custom filter derives from a built-in attribute base class: `ActionFilterAttribute`, `ResultFilterAttribute`, or `ExceptionFilterAttribute`. Each filter stage has a synchronous interface with before and after methods, and an async interface with one method that calls `next()`. Implement one or the other for a stage, not both. If a class has both, MVC calls only the async one.

The async form keeps the before and after logic in one method, which suits timing. Request `/api/slow` and read `X-Elapsed-Ms`. The header is added after `next()` returns, which still works because the action filter finishes before the result writes the response.

```csharp
using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class ElapsedHeaderAttribute : ActionFilterAttribute
{
    public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        var started = Stopwatch.GetTimestamp();
        await next();
        var ms = Stopwatch.GetElapsedTime(started).TotalMilliseconds;
        context.HttpContext.Response.Headers["X-Elapsed-Ms"] = ms.ToString("F0");
    }
}

[ApiController]
public class SlowController : ControllerBase
{
    [HttpGet("/api/slow"), ElapsedHeader]
    public async Task<string> Get() { await Task.Delay(150); return "done"; }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#implementation)

## Add filters to actions and pages

A filter can apply at three scopes. As an attribute on an action, it applies to that action only. As an attribute on a controller or page model class, it applies to every action or handler in it. Added to `MvcOptions.Filters`, it applies globally to every controller, action, and Razor Page in the app. Razor Pages also takes filters through conventions, for example on every page in a folder.

Global filters added by type, such as `Filters.Add<T>()`, are created per request and get constructor dependencies from DI. Filters added as an instance are shared singletons. Request `/api/scoped` and `/Admin/Report` and compare their `X-Filter` headers.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers(options => options.Filters.Add(new TagAttribute("global")));
builder.Services.AddRazorPages(options => options.Conventions.AddFolderApplicationModelConvention(
    "/Admin", model => model.Filters.Add(new TagAttribute("admin folder"))));
var app = builder.Build();
app.MapControllers();
app.MapRazorPages();
app.Run();

public class TagAttribute(string name) : ResultFilterAttribute
{
    public override void OnResultExecuting(ResultExecutingContext context) =>
        context.HttpContext.Response.Headers.Append("X-Filter", name);
}

[ApiController, Tag("controller")]
public class ScopedController : ControllerBase
{
    [HttpGet("/api/scoped"), Tag("action")] public string Get() => "ok";
}
```

```cshtml
@* Pages/Admin/Report.cshtml *@
@page
<p>Report</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#applying-filters)

## Default filter order

Within one stage, scope sets the default order. Global filters wrap controller or page filters, which wrap action filters. The before methods run outside-in and the after methods run inside-out, like nested middleware. A controller derived from `Controller` is itself a filter around all of these. Its `OnActionExecuting` override runs before every other action filter, and its `OnActionExecuted` runs after them.

Request `/order` and read the console log. The sequence is controller override, global, class, method, the action, then the same names in reverse.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers(options => options.Filters.Add(new LogAttribute("global")));
var app = builder.Build();
app.MapControllers();
app.Run();

public class LogAttribute(string name) : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext c) => Console.WriteLine($"{name} before");
    public override void OnActionExecuted(ActionExecutedContext c) => Console.WriteLine($"{name} after");
}

[Log("class")]
public class OrderController : Controller
{
    public override void OnActionExecuting(ActionExecutingContext c) => Console.WriteLine("override before");
    public override void OnActionExecuted(ActionExecutedContext c) => Console.WriteLine("override after");

    [HttpGet("/order"), Log("method")]
    public string Get() { Console.WriteLine("action"); return "see console"; }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#filter-scopes-and-order-of-execution)

## Override order with IOrderedFilter

A filter that implements `IOrderedFilter` has an `Order` number that outranks scope. Filters sort by `Order` first, ascending, and only filters with equal `Order` fall back to scope. A lower number runs its before code earlier and its after code later. The default is 0, and the built-in attribute base classes expose `Order` as a settable property.

Here the method filter sets `Order = -1`, so it runs outside the global filter even though it is declared on the method. Request `/api/early` and read the console. Change the number when one filter must see the request first, for example a timing filter that should include every other filter.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers(options => options.Filters.Add(new LogAttribute("global")));
var app = builder.Build();
app.MapControllers();
app.Run();

public class LogAttribute(string name) : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext c) => Console.WriteLine($"{name} before");
    public override void OnActionExecuted(ActionExecutedContext c) => Console.WriteLine($"{name} after");
}

[ApiController]
public class EarlyController : ControllerBase
{
    [HttpGet("/api/early"), Log("method", Order = -1)] public string Get() => "see console";
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#override-the-default-order)
