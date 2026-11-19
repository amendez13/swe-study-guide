# OpenAPI

Generate an OpenAPI document with ASP.NET Core's built-in package. Use that document for interactive calls and typed client generation.

## Key points

- Register OpenAPI generation and map the document route in the environments that need it.
- Keep descriptions and documented responses aligned with runtime behavior.
- Regenerate clients when the contract changes and test the generated result.

## Example

Run the [built-in generation example](#12_ASP.NET_Core/11_OpenAPI/concepts/built-in-openapi-document-generation) in a fresh `net10.0` web project.

```sh
dotnet add package Microsoft.AspNetCore.OpenApi --version '10.*'
ASPNETCORE_ENVIRONMENT=Development \
  dotnet run --no-launch-profile -- --urls http://127.0.0.1:5080
# In a second shell:
curl -fsS http://127.0.0.1:5080/openapi/v1.json
```

For the [interactive example](#12_ASP.NET_Core/11_OpenAPI/concepts/interactive-api-documentation), add `Scalar.AspNetCore` with `dotnet add package Scalar.AspNetCore`, then visit `http://127.0.0.1:5080/scalar`.

For the [XML comments example](#12_ASP.NET_Core/11_OpenAPI/concepts/xml-comments-in-generated-documents), add this property inside the project file's `PropertyGroup`.

```xml
<GenerateDocumentationFile>true</GenerateDocumentationFile>
```

For the [client generation example](#12_ASP.NET_Core/11_OpenAPI/concepts/generate-and-refresh-a-typed-client), run that app in Development and run these commands in a separate scratch directory. The generated C# file uses System.Text.Json and accepts an injected `HttpClient` with a base address.

```sh
dotnet new console --framework net10.0
dotnet tool install --tool-path ./.tools NSwag.ConsoleCore
curl -fsS http://127.0.0.1:5080/openapi/v1.json -o openapi.json
./.tools/nswag openapi2csclient /input:openapi.json /output:BranchClient.cs \
  /classname:BranchClient /namespace:StudyClients /JsonLibrary:SystemTextJson /UseBaseUrl:false
```

Replace the console project's `Program.cs` with the following code and run `dotnet run` while the API is running. To refresh the client later, fetch the document and rerun the generator command.

```csharp
using var http = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:5080/") };
var branch = await new StudyClients.BranchClient(http).GetBranchAsync(3);
Console.WriteLine(branch.Name);
```
