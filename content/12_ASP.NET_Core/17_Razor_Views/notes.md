# Razor Views

Razor views are compiled templates that mix HTML with C#. Layouts, sections, partials, and the special `_ViewStart` and `_ViewImports` files keep shared markup in one place.

## Key points

- `@` writes an encoded value. `@( ... )` handles complex expressions, and `Html.Raw` is only for trusted markup.
- Pass page data through a strongly typed model. Use `ViewData` for small values that layouts read, such as the title.
- Layouts wrap pages with `RenderBody` and optional sections. Partials share fragments. `_ViewImports` and `_ViewStart` apply to a whole folder tree.

## Example

Run the [layouts and sections example](#12_ASP.NET_Core/17_Razor_Views/concepts/layouts-and-sections). Then delete the page's `@section` line and request it again. The optional section renders empty.

```sh
curl -fsS http://127.0.0.1:5080/Visit
```

Razor runtime compilation is obsolete in ASP.NET Core 10. To see markup edits without a restart, run the example under Hot Reload.

```sh
dotnet watch --no-launch-profile -- --urls http://127.0.0.1:5080
```
