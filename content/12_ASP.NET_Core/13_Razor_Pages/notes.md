# Razor Pages

Razor Pages generate HTML on the server. Each page file pairs Razor markup with an optional page model whose handlers run before the markup renders.

## Key points

- `AddRazorPages` registers the page services and `MapRazorPages` maps one endpoint per `@page` file. A file without `@page` is a view, not an endpoint.
- Handlers act as the controller in model-view-controller. They read the binding model, call the application model, and fill the view model.
- Form posts use post/redirect/get. Razor Pages checks antiforgery tokens on POST by default.

## Example

Before the first example, follow the [Razor Pages setup](#12_ASP.NET_Core) in the course overview. Then run the [complete request example](#12_ASP.NET_Core/13_Razor_Pages/concepts/a-complete-razor-page-request) and open `http://127.0.0.1:5080/Sign` in a browser. Submit an empty name, then a real one. From a shell, compare a POST without the antiforgery token.

```sh
curl -i -X POST http://127.0.0.1:5080/Sign -d 'Name=Ada'
```
