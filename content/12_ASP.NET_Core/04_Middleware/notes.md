# Middleware

Middleware forms a request pipeline. Each component chooses whether to pass control downstream, and registration order determines which work it can observe or intercept.

## Key points

- A component can run code on both sides of the next delegate.
- Short-circuiting skips the later middleware and endpoint.
- Choose static asset handling based on when files are discovered. Keep exception diagnostics appropriate to the environment.

## Example

Run the [static files example](#12_ASP.NET_Core/04_Middleware/concepts/build-time-and-runtime-static-files) after placing a file in the project’s web root.

```sh
mkdir -p wwwroot
printf 'Open at noon\n' > wwwroot/notice.txt
dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
# In a second shell:
curl -i http://127.0.0.1:5080/notice.txt
```
