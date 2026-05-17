## Singleton

Ensures a class has exactly one instance and provides a global access point to it. Useful for shared resources like configuration registries or connection pools, but the global state it introduces can make testing and concurrency harder.

```java
public class AppConfig {
    private static final AppConfig INSTANCE = new AppConfig();

    private AppConfig() {}   // private constructor prevents external instantiation

    public static AppConfig getInstance() {
        return INSTANCE;
    }

    private String dbUrl = "jdbc:postgresql://localhost/mydb";
    public String getDbUrl() { return dbUrl; }
}
```

In modern codebases, dependency injection often replaces Singleton: the framework manages the single instance while still allowing tests to substitute it.

## Factory Method

Defines a method for creating objects but lets subclasses or implementations decide which concrete class to instantiate. This decouples object creation from the code that uses the object, so adding a new product type doesn't require editing the consumer.

```java
public abstract class Dialog {
    public void render() {
        Button btn = createButton();   // factory method
        btn.paint();
    }
    protected abstract Button createButton();
}

public class WindowsDialog extends Dialog {
    @Override
    protected Button createButton() { return new WindowsButton(); }
}

public class LinuxDialog extends Dialog {
    @Override
    protected Button createButton() { return new LinuxButton(); }
}
```

The `Dialog` code never mentions a concrete button — it delegates creation to subclasses, keeping the rendering logic closed for modification.

## Abstract Factory

Provides an interface for creating families of related objects without specifying their concrete classes. Each factory implementation produces a consistent set of products that work together.

```java
public interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

public class MaterialFactory implements UIFactory {
    public Button createButton()     { return new MaterialButton(); }
    public Checkbox createCheckbox() { return new MaterialCheckbox(); }
}

public class CupertinoFactory implements UIFactory {
    public Button createButton()     { return new CupertinoButton(); }
    public Checkbox createCheckbox() { return new CupertinoCheckbox(); }
}
```

Swapping the factory switches the entire product family at once — the calling code only depends on `UIFactory` and never imports concrete classes.

## Builder

Separates the construction of a complex object from its representation. Particularly useful when a constructor would need many parameters, most of them optional. The builder collects configuration step by step and produces the object in a final `build()` call.

```java
public class HttpRequest {
    private final String url;
    private final String method;
    private final Map<String, String> headers;

    private HttpRequest(Builder b) {
        this.url = b.url; this.method = b.method; this.headers = b.headers;
    }

    public static class Builder {
        private final String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();

        public Builder(String url)                 { this.url = url; }
        public Builder method(String m)            { this.method = m; return this; }
        public Builder header(String k, String v)  { headers.put(k, v); return this; }
        public HttpRequest build()                 { return new HttpRequest(this); }
    }
}

// Usage
HttpRequest req = new HttpRequest.Builder("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();
```

## Prototype

Creates new objects by cloning an existing instance rather than calling a constructor. Useful when object creation is expensive (deep configuration, network calls) or when you want to produce variations of a template object.

```java
public class ServerConfig implements Cloneable {
    private String host;
    private int port;
    private Map<String, String> properties;

    @Override
    public ServerConfig clone() {
        try {
            ServerConfig copy = (ServerConfig) super.clone();
            copy.properties = new HashMap<>(this.properties);   // deep copy
            return copy;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

ServerConfig template = loadDefaultConfig();
ServerConfig staging  = template.clone();
staging.setHost("staging.example.com");
```

In Java, `Cloneable` and `clone()` are the traditional mechanism, though copy constructors or static factory methods are often preferred for clarity.
