# Custom Filters

Each filter type suits a different job: authorization filters reject, resource filters skip work, action and page filters inspect bound input, exception filters translate errors, and result filters adjust responses.

## Key points

- Short-circuit by setting `context.Result`. After an authorization or resource filter does so, only `IAlwaysRunResultFilter` result filters still run.
- Exception filters cover binding, action filters, and the action, but not result execution. Keep app-wide error handling in middleware.
- Get services into filters with `[ServiceFilter<T>]`, `[TypeFilter<T>]`, `IFilterFactory`, or global filters added by type.

## Example

Run the [short-circuiting example](#12_ASP.NET_Core/22_Custom_Filters/concepts/short-circuiting-the-pipeline) and compare the result filter header on each response.

```sh
curl -i 'http://127.0.0.1:5080/api/gate?stage=resource'
curl -i 'http://127.0.0.1:5080/api/gate?stage=action'
curl -i http://127.0.0.1:5080/api/gate
```
