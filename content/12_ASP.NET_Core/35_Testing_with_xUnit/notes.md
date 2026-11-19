# Testing with xUnit

xUnit is the test framework used by ASP.NET Core itself. Tests live in a separate project that references the app, and `dotnet test` builds and runs them.

## Key points

- Unit tests are fast and isolated, integration tests check wiring, and end-to-end tests check the deployed app. Write mostly unit tests.
- `[Fact]` is one scenario and `[Theory]` runs one test per data row. xUnit creates a new class instance per test.
- `Assert.Throws<T>` matches the exact type and `ThrowsAny<T>` accepts derived types. In .NET 10, `dotnet new sln` creates a `.slnx` file, and xUnit v3 is the current major version.

## Example

From the folder that contains `StudyApi`, use the [kinds of tests](#12_ASP.NET_Core/35_Testing_with_xUnit/concepts/kinds-of-tests) `Program.cs` and create the test project and solution.

```sh
dotnet new sln -n Library
dotnet new xunit -o StudyApi.Tests
dotnet sln add StudyApi StudyApi.Tests
dotnet add StudyApi.Tests reference StudyApi
dotnet test
dotnet test --filter "FullyQualifiedName~LateFee"
```

Save each test card's block at the path in its first comment. The last command runs only the tests whose names contain `LateFee`.
