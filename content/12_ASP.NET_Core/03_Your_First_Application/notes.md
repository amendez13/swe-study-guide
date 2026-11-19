# Your First Application

Build and run a Web SDK project, then trace the order in which services, middleware, and endpoints are assembled.

## Key points

- The project file selects the SDK, target framework, and extra packages.
- Configure services before building the application. Configure the pipeline and endpoints on the built app.
- The URL for a local run is hosting configuration; the route template fixes the endpoint path.

## Example

Run the [startup example](#12_ASP.NET_Core/03_Your_First_Application/concepts/build-and-run-the-application) using the explicit URL and query its endpoint.

```sh
dotnet build
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
# In a second shell:
curl -i http://127.0.0.1:5080/environment
```
