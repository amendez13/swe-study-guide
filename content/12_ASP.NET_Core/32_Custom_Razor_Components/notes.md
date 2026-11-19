# Custom Razor Components

Tag Helpers, view components, and validation attributes extend Razor Pages and MVC with your own reusable pieces. FluentValidation is a common alternative to DataAnnotations for complex rules.

## Key points

- Tag Helpers rewrite elements or attributes during rendering. Register your assembly with `@addTagHelper *, StudyApi`.
- View components are partial views with their own logic and DI. Razor Pages finds their views in `Pages/Shared/Components/{Name}/`.
- Custom `ValidationAttribute` classes treat null as valid. FluentValidation validators are registered in DI and called explicitly.

## Example

Register the project's Tag Helpers once, add Markdig, and run the [Markdown example](#12_ASP.NET_Core/32_Custom_Razor_Components/concepts/render-markdown-with-a-tag-helper).

```sh
printf '@addTagHelper *, StudyApi\n' >> Pages/_ViewImports.cshtml
dotnet add package Markdig
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
curl http://127.0.0.1:5080/
```

The response contains an `h2` and a list instead of a `markdown` element. The [FluentValidation examples](#12_ASP.NET_Core/32_Custom_Razor_Components/concepts/add-fluentvalidation-to-an-app) need `dotnet add package FluentValidation.DependencyInjectionExtensions`, which also brings in `FluentValidation`.
