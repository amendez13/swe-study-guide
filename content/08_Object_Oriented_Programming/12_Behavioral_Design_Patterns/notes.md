# Behavioral Design Patterns

Behavioral patterns focus on how objects communicate and distribute responsibility. They define protocols for interaction so that the system stays flexible and individual classes remain focused.

## Key Points

- **Observer** — One-to-many notification: when the subject changes, all observers are updated. Foundation of event systems.
- **Strategy** — Swap algorithms at runtime through a common interface. Eliminates conditional algorithm selection.
- **Template Method** — Fix the algorithm skeleton in a base class; subclasses fill in the variable steps.
- **Command** — Encapsulate a request as an object, enabling queuing, logging, and undo/redo.
- **State** — Delegate behavior to state objects so an object appears to change class when its state changes.
- **Chain of Responsibility** — Pass a request through a chain of handlers; each decides to handle or forward.
- **Iterator** — Sequential access to collection elements without exposing internal structure.
- **Mediator** — Centralize communication between components to reduce direct dependencies.

## Example

```java
public interface Command {
    void execute();
}

public class LightOnCommand implements Command {
    private final Light light;
    public LightOnCommand(Light light) { this.light = light; }
    public void execute() { light.turnOn(); }
}

public class LightOffCommand implements Command {
    private final Light light;
    public LightOffCommand(Light light) { this.light = light; }
    public void execute() { light.turnOff(); }
}

public class RemoteControl {
    private final List<Command> history = new ArrayList<>();

    public void press(Command cmd) {
        cmd.execute();
        history.add(cmd);
    }

    public List<Command> getHistory() { return Collections.unmodifiableList(history); }
}

public class Main {
    public static void main(String[] args) {
        Light lamp = new Light();
        RemoteControl remote = new RemoteControl();

        remote.press(new LightOnCommand(lamp));
        remote.press(new LightOffCommand(lamp));

        System.out.println("Commands executed: " + remote.getHistory().size());
    }
}
```

The `RemoteControl` has no idea what the commands do — it just executes and logs them. Adding a `FanOnCommand` requires no changes to the remote.
