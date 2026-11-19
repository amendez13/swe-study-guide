# Testing with xUnit

## Kinds of tests

Automated tests catch regressions before users do and let you change code with confidence. Unit tests check one class or method in isolation, with collaborators replaced by fakes. They're fast and precise, so you can have many. Integration tests run several real components together, such as the whole ASP.NET Core pipeline in memory or a real database, and catch wiring mistakes that unit tests miss. End-to-end tests drive the deployed app, often through a browser. They're the most realistic, and also the slowest and most fragile.

Most suites have many unit tests, fewer integration tests, and a handful of end-to-end tests. Test behavior through public methods, not private details, so refactoring doesn't break tests. The code below is the kind of logic worth unit testing. Later cards test it from a separate project.

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/fee", (int daysLate) => LateFees.For(daysLate));
app.Run();

public static class LateFees
{
    public static decimal For(int daysLate)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(daysLate);
        return Math.Min(daysLate * 0.25m, 10m);
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)

## Create a test project

Tests live in a separate project so they never ship with the app. `dotnet new xunit` creates a test project that references xUnit, its Visual Studio runner, and `Microsoft.NET.Test.Sdk`. Put the app and its tests in one solution, so one command builds and tests both. In .NET 10, `dotnet new sln` creates the XML-based `.slnx` format by default.

Name the project after the one it tests, such as `StudyApi.Tests`. xUnit v3, packaged as `xunit.v3`, is the current major version. Its tests are standalone executables, and it adds `TestContext.Current` with a cancellation token. The `[Fact]` and `[Theory]` model is the same in both versions. The new project starts with one test like this.

```csharp
// StudyApi.Tests/UnitTest1.cs
namespace StudyApi.Tests;

public class UnitTest1
{
    [Fact]
    public void Test1()
    {
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit)

## Run tests with dotnet test

`dotnet test` builds the projects, discovers tests, runs them, and prints a summary with the failures. Run it in the solution folder for every test project, or point it at one project. `--filter` selects tests by name, class, or trait. `--logger "console;verbosity=detailed"` shows each test as it runs. A non-zero exit code on failure makes the command work as a CI gate.

Tests in one class run sequentially, and test classes run in parallel by default, so tests must not share mutable state. .NET 10 can also run tests on Microsoft.Testing.Platform instead of VSTest, which you opt into in `global.json`. This test passes and shows up in the filtered run.

```csharp
// StudyApi.Tests/SmokeTests.cs
namespace StudyApi.Tests;

public class SmokeTests
{
    [Fact]
    public void Addition_works() => Assert.Equal(4, 2 + 2);
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test)

## Reference the app from the test project

A test project tests the app through a project reference: `dotnet add StudyApi.Tests reference StudyApi`. Public types in the app are then visible to the tests. For `internal` types, add `<InternalsVisibleTo Include="StudyApi.Tests" />` to the app's project file instead of making them public just for tests.

Keep testable logic out of `Program.cs` lambdas and in named classes or static methods that tests can call. The test below calls `LateFees.For` from the [first card](#12_ASP.NET_Core/35_Testing_with_xUnit/concepts/kinds-of-tests). It's declared in the app's `Program.cs`, which compiles into the referenced assembly.

```csharp
// StudyApi.Tests/LateFeeTests.cs
namespace StudyApi.Tests;

public class LateFeeTests
{
    [Fact]
    public void Fee_is_a_quarter_per_day()
    {
        var fee = LateFees.For(daysLate: 4);

        Assert.Equal(1.00m, fee);
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit#create-a-test-project)

## Facts

A `[Fact]` is a test with no parameters: one scenario that must always hold. Structure it as arrange, act, assert, and name it after the behavior, such as `Fee_is_capped_at_ten`. xUnit creates a new instance of the test class for every test, so fields set in the constructor are fresh each time. Put shared setup in the constructor and cleanup in `Dispose`.

`Assert` covers equality, collections, strings, types, and ranges, and the failure message shows expected and actual values. Use one logical assertion per test, so a failure points at one behavior. The example tests the cap and confirms that each test gets its own list.

```csharp
// StudyApi.Tests/LateFeeFacts.cs
namespace StudyApi.Tests;

public class LateFeeFacts
{
    private readonly List<decimal> _fees = [];

    [Fact]
    public void Fee_is_capped_at_ten()
    {
        _fees.Add(LateFees.For(daysLate: 100));

        Assert.Equal(10m, Assert.Single(_fees));
    }

    [Fact]
    public void No_fee_when_on_time()
    {
        _fees.Add(LateFees.For(daysLate: 0));

        Assert.Equal(0m, Assert.Single(_fees));
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit#add-more-features)

## Theories

A `[Theory]` is a parameterized test. Each `[InlineData]` row runs as a separate test case with its own result, so one failing row doesn't hide the others. Use theories when the same behavior should hold for several inputs, such as boundaries around a cap.

`[MemberData]` and `[ClassData]` supply rows from code when the values aren't constants, such as `decimal` or objects. xUnit's `TheoryData<T1, T2>` gives those rows type safety. The example checks the boundaries of the late fee with both styles.

```csharp
// StudyApi.Tests/LateFeeTheories.cs
namespace StudyApi.Tests;

public class LateFeeTheories
{
    [Theory]
    [InlineData(0, 0)]
    [InlineData(1, 0.25)]
    [InlineData(40, 10)]
    [InlineData(41, 10)]
    public void Fee_for_days_late(int daysLate, double expected) =>
        Assert.Equal((decimal)expected, LateFees.For(daysLate));

    public static TheoryData<int, decimal> Caps => new() { { 39, 9.75m }, { 400, 10m } };

    [Theory]
    [MemberData(nameof(Caps))]
    public void Fee_near_the_cap(int daysLate, decimal expected) =>
        Assert.Equal(expected, LateFees.For(daysLate));
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit#add-more-features)

## Test failure conditions

Error paths need tests too. `Assert.Throws<T>` runs a delegate and passes only when it throws exactly `T`, then returns the exception so you can check its details. `Assert.ThrowsAny<T>` also accepts derived types. For async code, use `Assert.ThrowsAsync<T>` and await it.

Check what matters to callers, such as the parameter name or the message, rather than the full text, which changes more often. Tests for failures document the contract as clearly as the success tests do. The example checks that negative days are rejected with the right parameter name.

```csharp
// StudyApi.Tests/LateFeeErrors.cs
namespace StudyApi.Tests;

public class LateFeeErrors
{
    [Fact]
    public void Negative_days_are_rejected()
    {
        var error = Assert.Throws<ArgumentOutOfRangeException>(() => LateFees.For(-1));

        Assert.Equal("daysLate", error.ParamName);
    }

    [Fact]
    public async Task Async_failures_use_ThrowsAsync()
    {
        await Assert.ThrowsAsync<InvalidOperationException>(() => Task.FromException(new InvalidOperationException()));
    }
}
```

[Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
