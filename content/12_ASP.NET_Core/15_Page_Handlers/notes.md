# Page Handlers

A page handler is a page-model method chosen by HTTP verb and an optional handler name. It returns either the page itself or another result.

## Key points

- `On{Verb}[Name][Async]` names select handlers. HEAD falls back to `OnGet`, and a request with no matching handler just renders the page.
- Return `Page()` to re-render, `RedirectToPage` after a successful change, and `NotFound()` or `StatusCode` for errors.
- `UseStatusCodePagesWithReExecute` gives empty error responses an HTML page without changing their status.

## Example

Run the [page and redirect results example](#12_ASP.NET_Core/15_Page_Handlers/concepts/page-and-redirect-results) and follow the redirect.

```sh
curl -i -X POST http://127.0.0.1:5080/Renew
curl -fsS http://127.0.0.1:5080/Renew/42
```
