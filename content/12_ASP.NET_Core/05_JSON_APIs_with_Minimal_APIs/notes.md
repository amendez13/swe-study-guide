# JSON APIs with Minimal APIs

Use Minimal APIs to specify a small HTTP contract in C#. Start with a method, a route, and an explicit set of outcomes, then group endpoints that share a prefix or a filter.

## Key points

- Choose status codes and response media types deliberately.
- Add Problem Details for API errors that clients need to interpret.
- Use endpoint filters to keep endpoint-specific work close to the handler.

## Example

Run the [error response example](#12_ASP.NET_Core/05_JSON_APIs_with_Minimal_APIs/concepts/problem-details-for-api-errors). Compare an explicit conflict with the automatic body for an unmatched route.

```sh
curl -i -X POST http://127.0.0.1:5080/archive
curl -i http://127.0.0.1:5080/missing
```
