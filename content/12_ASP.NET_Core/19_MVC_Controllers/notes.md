# MVC Controllers

MVC controllers group actions by resource and pass view models to Razor views. They share routing, binding, validation, filters, and results with Razor Pages.

## Key points

- `AddControllersWithViews` and `MapControllerRoute` (or `MapDefaultControllerRoute`) set up conventional MVC routing.
- `View()` looks in `Views/{Controller}` and then in `Views/Shared` for a view named after the action. Pass a name or a full path to choose another.
- Prefer Razor Pages for page-focused UI. Use controllers when grouping by resource helps, and mix both in one app when needed.

## Example

Run the [view selection example](#12_ASP.NET_Core/19_MVC_Controllers/concepts/selecting-a-view) and compare the two views.

```sh
curl -fsS http://127.0.0.1:5080/Books/Show/1
curl -fsS http://127.0.0.1:5080/Books/Show/2
```
