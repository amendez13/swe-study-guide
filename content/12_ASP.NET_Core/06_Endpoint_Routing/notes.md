# Endpoint Routing

Routing decides which endpoint is eligible for a request and supplies path values for the handler. The same templates can generate URLs for responses and links.

## Key points

- A literal is more specific than a parameter. HTTP method and constraints affect eligibility.
- Optional segments and defaults express different contracts for omitted values.
- Use a named endpoint to generate a location from route values.

## Example

Run the [link generation example](#12_ASP.NET_Core/06_Endpoint_Routing/concepts/link-generation-and-named-results). Compare the generated URL with the creation response.

```sh
curl -i http://127.0.0.1:5080/links
curl -i -X POST http://127.0.0.1:5080/titles
```
