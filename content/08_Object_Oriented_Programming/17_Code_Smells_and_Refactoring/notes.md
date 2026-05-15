# Code Smells and Refactoring

Code smells are patterns in code that suggest a design problem without being outright bugs. Learning to recognize them — and knowing the standard refactorings that fix them — is a core skill for keeping OOP codebases healthy over time.

## Key Points

- **Code smell** — A surface indicator of a deeper design problem. Not a bug, but a maintenance warning sign.
- **Long Method / Large Class** — Too much in one place. Fix with Extract Method or Extract Class.
- **Feature Envy** — A method uses another class's data more than its own. Move the method or the data.
- **Shotgun Surgery** — One change touches many classes. Consolidate the scattered responsibility.
- **Refused Bequest** — A subclass inherits things it doesn't need. Use composition or a narrower interface instead.
- **Refactoring** — Restructuring without changing behavior. Always backed by tests.

## Example

```java
// Before: Feature Envy — formatAddress reaches deep into Customer
public class InvoicePrinter {
    public String formatAddress(Customer c) {
        return c.getStreet() + "\n"
             + c.getCity() + ", " + c.getState() + " " + c.getZip();
    }
}

// After: Move the method to where the data lives
public class Customer {
    private String street, city, state, zip;

    public String formattedAddress() {
        return street + "\n" + city + ", " + state + " " + zip;
    }
}

public class InvoicePrinter {
    public String formatAddress(Customer c) {
        return c.formattedAddress();   // delegates, no envy
    }
}
```

The refactored version places `formattedAddress()` on `Customer` where the data lives, eliminating the envy and making `Customer` responsible for its own formatting.
