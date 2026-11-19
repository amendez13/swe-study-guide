# Dependency Injection

Wire one collaborator into an ASP.NET Core endpoint and follow how the container supplies its dependencies.

## Key points

- Make required collaborators visible in constructors or handler signatures.
- Register the graph before building the app. Framework feature methods can register several related services.
- Explicit resolution belongs at a composition boundary, with a scope when needed.

## Example

Run the [application service container example](#12_ASP.NET_Core/08_Dependency_Injection/concepts/the-application-service-container) using the [course setup](#12_ASP.NET_Core).

```sh
curl -i http://127.0.0.1:5080/loan-period
```
