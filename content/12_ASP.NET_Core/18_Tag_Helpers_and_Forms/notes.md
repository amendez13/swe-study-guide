# Tag Helpers and Forms

Tag Helpers let server code rewrite ordinary HTML elements. Form-related helpers generate names, values, input types, validation hooks, links, and antiforgery tokens from the model and routing data.

## Key points

- `asp-for` ties labels, inputs, selects, and validation messages to one model expression, so rendering and binding use the same names.
- The Form Tag Helper adds the antiforgery token to POST forms. Anchor and Form helpers build URLs from page or action names.
- Since .NET 9, `WithStaticAssets` makes `~/` asset URLs fingerprinted. `asp-append-version` was the earlier approach. The Environment Tag Helper renders content per environment.

## Example

Run the [Select Tag Helper example](#12_ASP.NET_Core/18_Tag_Helpers_and_Forms/concepts/the-select-tag-helper) and inspect the options, then submit the form in a browser.

```sh
curl -fsS http://127.0.0.1:5080/Pickup
```

Run the [Environment Tag Helper example](#12_ASP.NET_Core/18_Tag_Helpers_and_Forms/concepts/the-environment-tag-helper) in each environment.

```sh
ASPNETCORE_ENVIRONMENT=Development dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
```
