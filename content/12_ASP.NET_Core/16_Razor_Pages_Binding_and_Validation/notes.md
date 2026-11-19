# Razor Pages Binding and Validation

Model binding turns form fields, route values, and query strings into handler parameters and bound properties. Validation then records rule failures in `ModelState` for the handler to act on.

## Key points

- Binding searches form fields, then route values, then the query string. Source attributes override that order.
- Conversion and validation errors go into `ModelState`. The handler still runs and must check `IsValid`.
- Bind a small input model per page, never a domain entity, and validate on the server even with client-side checks.

## Example

Run the [server-side validation example](#12_ASP.NET_Core/16_Razor_Pages_Binding_and_Validation/concepts/server-side-validation) and open `http://127.0.0.1:5080/BookRoom` in a browser. Submit an empty room, then `Maps` with 2 seats, then `Atlas` with 2 seats. Each response shows which rule rejected the input.
