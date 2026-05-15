## Adapter

Converts the interface of an existing class into one that a client expects. Lets two classes with incompatible interfaces work together without modifying either — you write a thin wrapper that translates between them.

```java
// Existing library class with an incompatible interface
public class LegacyPrinter {
    public void printDocument(String text) { System.out.println(text); }
}

// Interface the client expects
public interface Printer {
    void print(String content);
}

// Adapter bridges the gap
public class PrinterAdapter implements Printer {
    private final LegacyPrinter legacy;
    public PrinterAdapter(LegacyPrinter legacy) { this.legacy = legacy; }

    @Override
    public void print(String content) { legacy.printDocument(content); }
}
```

## Facade

Provides a simplified interface to a complex subsystem. Instead of requiring callers to coordinate multiple objects and understand their interaction, a facade offers a single entry point that does the orchestration internally.

```java
public class VideoConverter {
    public File convert(String filename, String format) {
        VideoFile file = new VideoFile(filename);
        Codec codec = CodecFactory.extract(file);
        byte[] result = BitrateReader.read(file, codec);
        byte[] converted = Encoder.convert(result, format);
        return new File(converted);
    }
}

// Caller only touches one class
VideoConverter converter = new VideoConverter();
File mp4 = converter.convert("video.ogg", "mp4");
```

## Composite

Composes objects into tree structures to represent part-whole hierarchies. Clients treat individual objects and compositions uniformly through the same interface — they don't need to know whether they are talking to a leaf or a branch.

```java
public interface FileSystemEntry {
    int size();
    String name();
}

public class File implements FileSystemEntry {
    private final String name;
    private final int bytes;
    public File(String name, int bytes) { this.name = name; this.bytes = bytes; }
    public int size()   { return bytes; }
    public String name() { return name; }
}

public class Directory implements FileSystemEntry {
    private final String name;
    private final List<FileSystemEntry> children = new ArrayList<>();

    public Directory(String name) { this.name = name; }
    public void add(FileSystemEntry entry) { children.add(entry); }

    public int size() {
        return children.stream().mapToInt(FileSystemEntry::size).sum();
    }
    public String name() { return name; }
}
```

Calling `size()` on a `Directory` recursively sums its children — files and subdirectories alike.

## Proxy

Provides a surrogate or placeholder for another object to control access to it. Common uses include lazy initialization (create the real object only when needed), access control, logging, and caching.

```java
public class LazyImageProxy implements Image {
    private final String path;
    private RealImage realImage;

    public LazyImageProxy(String path) { this.path = path; }

    @Override
    public void display() {
        if (realImage == null) {
            realImage = new RealImage(path);   // expensive load deferred
        }
        realImage.display();
    }
}
```

The proxy has the same interface as the real object, so callers can't tell the difference — they just see an `Image`.

## Decorator

Attaches additional behavior to an object dynamically by wrapping it in another object with the same interface. Unlike subclassing, decorators can be stacked and composed at runtime.

```java
public interface DataSource {
    void write(String data);
    String read();
}

public class FileDataSource implements DataSource {
    public void write(String data) { /* write to file */ }
    public String read()           { return "raw data"; }
}

public class EncryptionDecorator implements DataSource {
    private final DataSource wrapped;
    public EncryptionDecorator(DataSource wrapped) { this.wrapped = wrapped; }

    public void write(String data) { wrapped.write(encrypt(data)); }
    public String read()           { return decrypt(wrapped.read()); }

    private String encrypt(String s) { return "ENC(" + s + ")"; }
    private String decrypt(String s) { return s.replace("ENC(", "").replace(")", ""); }
}

// Stack decorators
DataSource ds = new EncryptionDecorator(new FileDataSource());
```

## Bridge

Separates an abstraction from its implementation so the two can vary independently. Instead of creating a subclass for every combination of abstraction and implementation, you compose them.

```java
public interface Color {
    String fill();
}
public class Red implements Color   { public String fill() { return "Red"; } }
public class Blue implements Color  { public String fill() { return "Blue"; } }

public abstract class Shape {
    protected Color color;
    public Shape(Color color) { this.color = color; }
    public abstract String draw();
}

public class Circle extends Shape {
    public Circle(Color color) { super(color); }
    public String draw() { return color.fill() + " Circle"; }
}
```

Without Bridge, you would need `RedCircle`, `BlueCircle`, `RedSquare`, `BlueSquare` — an explosion of subclasses.
