# Overloading, Overriding, and Dynamic Dispatch

These three ideas explain how OOP APIs handle variation. Overloading is API convenience, overriding is subtype specialization, and dynamic dispatch is what makes the subtype behavior actually run at runtime.

## Key Points

- **Overloading** — same method name, different parameter shapes.
- **Overriding** — a subtype replaces parent behavior with its own implementation.
- **Dynamic dispatch** — runtime object type determines which overridden method runs.
- **Different purposes** — overloading is about call shape; overriding is about behavior variation.
- **Parent contracts still matter** — overrides should preserve caller expectations.
- **Defaults vs specialization** — parent methods may share behavior or simply define required shape.
- **Tracing can get harder** — many overrides across a hierarchy increase cognitive load.
- **Use only where the variation is real** — these are tools, not mandatory ceremony.

## Example

```python
class Shape:
    def area(self) -> float:
        raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius * self.radius
```

Calling `shape.area()` uses dynamic dispatch to select the rectangle or circle implementation based on the actual runtime object.
