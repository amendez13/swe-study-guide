# Service Registration

Choose the registration lifetime to match how the object is used. Pay particular attention to services that carry mutable state or wrap a database connection or context.

## Key points

- The type, instance, and factory overloads control how the provider gets an object.
- A single service and the corresponding collection have different multiple-registration rules. Keyed services express a specific named selection.
- Keep long-lived objects from holding scoped dependencies.

## Example

Run the [service lifetimes example](#12_ASP.NET_Core/09_Service_Registration/concepts/transient-scoped-and-singleton-lifetimes). Compare both arrays within each response, then compare responses.

```sh
curl -fsS http://127.0.0.1:5080/instances
curl -fsS http://127.0.0.1:5080/instances
```
