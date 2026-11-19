# Testing with xUnit — Drills

Predict the result before running the example.

## Count the test results

`LateFees.For` caps fees at 10. How many tests does `dotnet test` report for this class, and how many fail?

```csharp
// StudyApi.Tests/FeeDrill.cs
namespace StudyApi.Tests;

public class FeeDrill
{
    [Theory]
    [InlineData(2, 0.5)]
    [InlineData(8, 2)]
    [InlineData(60, 15)]
    public void Fee(int daysLate, double expected) =>
        Assert.Equal((decimal)expected, LateFees.For(daysLate));

    [Fact]
    public void Zero_days() => Assert.Equal(0m, LateFees.For(0));
}
```

**Answer**

Four tests: three theory rows and one fact. One fails, the `60` row, because the cap makes the fee 10, not 15. Each `InlineData` row is a separate test case, so the first two rows still pass and the failure message names the row's arguments.

## Throws and a derived exception

`LateFees.For(-1)` throws `ArgumentOutOfRangeException`, which derives from `ArgumentException`. Which tests pass?

```csharp
// StudyApi.Tests/ThrowsDrill.cs
namespace StudyApi.Tests;

public class ThrowsDrill
{
    [Fact]
    public void Exact() => Assert.Throws<ArgumentException>(() => LateFees.For(-1));

    [Fact]
    public void Any() => Assert.ThrowsAny<ArgumentException>(() => LateFees.For(-1));
}
```

**Answer**

Only `Any` passes. `Assert.Throws<T>` requires the exact type, so `Exact` fails and reports that it expected `ArgumentException` but got `ArgumentOutOfRangeException`. `Assert.ThrowsAny<T>` accepts `T` or any type derived from it.
