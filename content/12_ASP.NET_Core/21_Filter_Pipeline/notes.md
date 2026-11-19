# Filter Pipeline

Filters run code at fixed stages around MVC actions and Razor Page handlers, with access to MVC context that middleware can't see.

## Key points

- MVC stages run in this order: authorization, resource, model binding, action, then result, with exception filters covering binding and the action. Razor Pages replaces action filters with page filters.
- Apply filters globally, on a controller or page model, or on an action. Global filters wrap class filters, which wrap method filters.
- `IOrderedFilter.Order` outranks scope. Lower numbers run their before code first and their after code last.

## Example

Run the [MVC filter pipeline example](#12_ASP.NET_Core/21_Filter_Pipeline/concepts/the-mvc-filter-pipeline) and read the stage headers in order.

```sh
curl -sS -D - -o /dev/null http://127.0.0.1:5080/api/stages
```

Run the [default order example](#12_ASP.NET_Core/21_Filter_Pipeline/concepts/default-filter-order), request `/order`, and read the app's console output.
