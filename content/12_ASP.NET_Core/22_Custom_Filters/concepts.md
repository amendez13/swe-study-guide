# Custom Filters

## Authorization filters

An authorization filter runs first and decides whether the request may continue. To deny it, set `context.Result`, for example to `UnauthorizedResult` or `ForbidResult`. That stops every later filter and the action. It has no after method, and it must not throw: exceptions there aren't handled by exception filters.

In most apps, don't write one. `[Authorize]` with policies already plugs into this stage, and Part 4 covers it. A custom filter fits a narrow check that isn't about user identity, such as a shared key for an internal endpoint. Request `/api/internal/stats` with and without the header `X-Internal-Key: s3cret`.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class InternalKeyAttribute : Attribute, IAuthorizationFilter
{
    public void OnAuthorization(AuthorizationFilterContext context)
    {
        if (context.HttpContext.Request.Headers["X-Internal-Key"] != "s3cret")
            context.Result = new UnauthorizedResult();
    }
}

[ApiController, InternalKey]
public class StatsController : ControllerBase
{
    [HttpGet("/api/internal/stats")] public object Get() => new { Loans = 42 };
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#authorization-filters)

## Resource filters

A resource filter wraps everything after authorization, including model binding, so it can skip that work entirely. Short-circuit by setting `context.Result` in `OnResourceExecuting`. Typical uses are a feature switch, a cache that serves a stored response on a hit, or turning off form binding for large streamed uploads.

This filter reads a configuration flag from request services, because attribute constructors can't receive DI services. Request `/api/loans` while `Features:Loans` is false, and the 503 arrives before model binding runs. Start the app with `--Features:Loans=true` to let requests through.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class FeatureAttribute(string name) : Attribute, IResourceFilter
{
    public void OnResourceExecuting(ResourceExecutingContext context)
    {
        var config = context.HttpContext.RequestServices.GetRequiredService<IConfiguration>();
        if (!config.GetValue<bool>($"Features:{name}"))
            context.Result = new StatusCodeResult(StatusCodes.Status503ServiceUnavailable);
    }

    public void OnResourceExecuted(ResourceExecutedContext context) { }
}

[ApiController, Feature("Loans")]
public class LoansController : ControllerBase
{
    [HttpGet("/api/loans")] public string[] Get() => ["Atlas"];
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#resource-filters)

## Action filters

An action filter runs after model binding, so `ActionArguments` and `ModelState` are ready. It can reject the request by setting `context.Result`, change arguments before the action runs, or change `Result` after it. A common example is the model-state check for controllers without `[ApiController]`, which do nothing about invalid input on their own.

This filter adds the 400 that `[ApiController]` would give, and an MVC controller with views could re-render its form instead. Post `copies=0` as form data to `/print`: the filter returns 400 with the errors and the action never runs.

```csharp
using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class RejectInvalidAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext context)
    {
        if (!context.ModelState.IsValid)
            context.Result = new BadRequestObjectResult(new ValidationProblemDetails(context.ModelState));
    }
}

public class PrintJob { [Range(1, 50)] public int Copies { get; set; } }

public class PrintController : ControllerBase
{
    [HttpPost("/print"), RejectInvalid]
    public string Print([FromForm] PrintJob job) => $"printing {job.Copies}";
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#action-filters)

## Exception filters

An exception filter runs when page or controller creation, model binding, an action filter, or the action throws. It can set `context.Result` or mark `ExceptionHandled` to stop the exception from spreading. It doesn't see exceptions from resource filters, result filters, or result execution, such as a view that fails to render. Those reach middleware.

App-wide error handling belongs in [exception handling middleware](#12_ASP.NET_Core/04_Middleware/concepts/exception-handling-by-environment). Since .NET 8 that middleware can use `IExceptionHandler`. Use an exception filter when one group of actions needs a different response, for example turning a domain conflict into a 409 Problem Details for an API controller. Request `/api/holds/1` for the 409 and `/api/holds/2` for success.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class HoldConflictException(string message) : Exception(message);

public class ConflictProblemAttribute : ExceptionFilterAttribute
{
    public override void OnException(ExceptionContext context)
    {
        if (context.Exception is not HoldConflictException conflict) return;
        context.Result = new ObjectResult(new ProblemDetails { Status = 409, Title = conflict.Message })
            { StatusCode = StatusCodes.Status409Conflict };
    }
}

[ApiController, ConflictProblem]
public class HoldsController : ControllerBase
{
    [HttpGet("/api/holds/{id:int}")]
    public string Place(int id) => id == 1 ? throw new HoldConflictException("Already on hold") : $"hold {id} placed";
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#exception-filters)

## Result filters

A result filter wraps the execution of an action result, after the action and its filters are done. `OnResultExecuting` can still change headers, replace `context.Result`, or cancel. `OnResultExecuted` runs after the response has usually started, so it is too late to change the response. Result filters run only when the action or an action filter produced the result.

`IAlwaysRunResultFilter` also runs for results set by authorization or resource filters and by exception filters, which suits headers that every response must carry. Request `/api/catalog` and `/api/catalog?closed=true`. Only the version header appears on the short-circuited response.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers(options =>
{
    options.Filters.Add(new CacheHeaderFilter());
    options.Filters.Add(new VersionHeaderFilter());
});
var app = builder.Build();
app.MapControllers();
app.Run();

public class CacheHeaderFilter : IResultFilter
{
    public void OnResultExecuting(ResultExecutingContext c) => c.HttpContext.Response.Headers.CacheControl = "max-age=60";
    public void OnResultExecuted(ResultExecutedContext c) { }
}

public class VersionHeaderFilter : IAlwaysRunResultFilter
{
    public void OnResultExecuting(ResultExecutingContext c) => c.HttpContext.Response.Headers["X-Api-Version"] = "2";
    public void OnResultExecuted(ResultExecutedContext c) { }
}

public class ClosedAttribute : Attribute, IResourceFilter
{
    public void OnResourceExecuting(ResourceExecutingContext c)
    {
        if (c.HttpContext.Request.Query["closed"] == "true") c.Result = new StatusCodeResult(503);
    }
    public void OnResourceExecuted(ResourceExecutedContext c) { }
}

[ApiController, Closed]
public class CatalogController : ControllerBase
{
    [HttpGet("/api/catalog")] public string[] Get() => ["Atlas"];
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#result-filters)

## Page filters

A page filter implements `IPageFilter` or `IAsyncPageFilter` and runs around Razor Page handlers. `OnPageHandlerSelectionAsync` runs before model binding, so it can change which handler runs or prepare state. `OnPageHandlerExecutionAsync` runs after binding, where it can read `HandlerArguments`, check `ModelState`, or short-circuit with `context.Result`. Register it globally through `MvcOptions.Filters` or for a folder through a page convention.

This global filter puts the branch from a header into `ViewData` for every page, so no page model has to read it. Request `/Hours` with the header `X-Branch: East`. Without the header the filter supplies a default.

```csharp
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Mvc.RazorPages;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages().AddMvcOptions(options => options.Filters.Add(new BranchPageFilter()));
var app = builder.Build();
app.MapRazorPages();
app.Run();

public class BranchPageFilter : IAsyncPageFilter
{
    public Task OnPageHandlerSelectionAsync(PageHandlerSelectedContext context) => Task.CompletedTask;

    public async Task OnPageHandlerExecutionAsync(PageHandlerExecutingContext context,
        PageHandlerExecutionDelegate next)
    {
        if (context.HandlerInstance is PageModel page)
            page.ViewData["Branch"] = context.HttpContext.Request.Headers["X-Branch"].FirstOrDefault() ?? "Main";
        await next();
    }
}

public class HoursModel : PageModel { public void OnGet() { } }
```

```cshtml
@* Pages/Hours.cshtml *@
@page
@model HoursModel
<p>@ViewData["Branch"] branch: open 9 to 5</p>
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/razor-pages/filter?view=aspnetcore-10.0)

## Short-circuiting the pipeline

Setting `context.Result` in a before method short-circuits the pipeline from that stage on. What still runs depends on the stage. After an authorization or resource filter short-circuits, model binding, action filters, and the action are skipped. Ordinary result filters are skipped too, and only `IAlwaysRunResultFilter` filters run. After an action filter short-circuits, inner action filters and the action are skipped, but result filters do run.

So a header added by a result filter may vanish from rejected requests, which is the gap `IAlwaysRunResultFilter` fills. Request `/api/gate?stage=resource` and `/api/gate?stage=action` and compare their headers.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
var app = builder.Build();
app.MapControllers();
app.Run();

public class GateAttribute : Attribute, IResourceFilter, IActionFilter, IResultFilter
{
    static bool Stop(FilterContext c, string stage) => c.HttpContext.Request.Query["stage"] == stage;
    public void OnResourceExecuting(ResourceExecutingContext c) { if (Stop(c, "resource")) c.Result = new ContentResult { Content = "stopped at resource" }; }
    public void OnResourceExecuted(ResourceExecutedContext c) { }
    public void OnActionExecuting(ActionExecutingContext c) { if (Stop(c, "action")) c.Result = new ContentResult { Content = "stopped at action" }; }
    public void OnActionExecuted(ActionExecutedContext c) { }
    public void OnResultExecuting(ResultExecutingContext c) => c.HttpContext.Response.Headers["X-Result-Filter"] = "ran";
    public void OnResultExecuted(ResultExecutedContext c) { }
}

[ApiController, Gate]
public class GateController : ControllerBase
{
    [HttpGet("/api/gate")] public string Get() => "action ran";
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#cancellation-and-short-circuiting)

## Dependency injection in filters

Filter attributes are created by the compiler, so their constructors can't receive services. There are three ways to get DI into a filter. `[ServiceFilter<T>]` resolves `T` from the container, so `T` must be registered and its lifetime applies. `[TypeFilter<T>]` creates `T` with constructor injection without a registration, and `Arguments` can pass extra constructor values. An attribute that implements `IFilterFactory` builds the filter itself from the `IServiceProvider`.

Global filters added by type, as in `options.Filters.Add<AuditFilter>()`, are also created through DI. Avoid setting `IsReusable = true` on a factory whose filter depends on scoped services. Request `/api/audited` and check the console for the log line from the injected logger.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddScoped<AuditFilter>();
var app = builder.Build();
app.MapControllers();
app.Run();

public class AuditFilter(ILogger<AuditFilter> logger) : IActionFilter
{
    public void OnActionExecuting(ActionExecutingContext context) =>
        logger.LogInformation("Audit {Action}", context.ActionDescriptor.DisplayName);
    public void OnActionExecuted(ActionExecutedContext context) { }
}

[ApiController]
public class AuditedController : ControllerBase
{
    [HttpGet("/api/audited"), ServiceFilter<AuditFilter>] public string Get() => "audited";
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/filters?view=aspnetcore-10.0#dependency-injection)
