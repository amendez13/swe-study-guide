# Razor Pages Routing

A page's file path gives its default route. The `@page` template can extend or replace that route, and conventions in `Program.cs` can add more.

## Key points

- `Index` pages answer their folder URL. Every page carries its name as the `page` route value.
- A relative `@page` template appends segments. A template starting with `/` replaces the route.
- Generate links from page names with `Url.Page`, the Anchor Tag Helper, or `LinkGenerator`, never from hand-built strings.

## Example

Run the [link generation example](#12_ASP.NET_Core/14_Razor_Pages_Routing/concepts/generate-urls-to-pages-and-controllers), then compare the generated paths with the routes that serve them.

```sh
curl -fsS http://127.0.0.1:5080/Books/Links
curl -fsS http://127.0.0.1:5080/b/4
curl -i http://127.0.0.1:5080/Books/Details/4
```
