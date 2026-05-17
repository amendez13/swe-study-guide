# Abstraction

Abstraction is the art of choosing which details matter for the problem at hand and hiding everything else. In OOP it shows up at multiple scales: at the class level (what does this class model?), at the method level (what does this operation expose?), and at the architecture level (how are layers of detail organized?).

## Key Points

- **Abstraction as a principle** — Model only what is relevant; ignore the rest. The first design decision when translating a domain into classes.
- **Abstract class** — A class that provides partial implementation and cannot be instantiated. Use when subclasses share state or common code.
- **Abstract method** — A method with no body that forces concrete subclasses to provide an implementation, turning missing behavior into a compile-time error.
- **CRC cards** — A whiteboard technique (Class–Responsibility–Collaborator) for discovering classes, their responsibilities, and their collaborators before writing code.
- **Domain modeling** — Identifying entities, attributes, and relationships using the language of the domain to drive class design from requirements.
- **Levels of abstraction** — Each method should operate at one consistent level; high-level methods read like summaries and delegate details downward.
- **Premature abstraction** — Abstracting before the pattern is clear can hurt more than duplication. Wait for three concrete cases before extracting.

## Example

```java
public abstract class Notification {
    private final String recipient;

    public Notification(String recipient) {
        this.recipient = recipient;
    }

    public void send(String message) {
        String formatted = format(message);
        deliver(formatted);
    }

    protected abstract String format(String message);
    protected abstract void deliver(String content);

    public String getRecipient() { return recipient; }
}

public class EmailNotification extends Notification {
    public EmailNotification(String email) { super(email); }

    @Override
    protected String format(String message) {
        return "<html><body>" + message + "</body></html>";
    }

    @Override
    protected void deliver(String content) {
        System.out.println("Emailing " + getRecipient() + ": " + content);
    }
}
```

`Notification` abstracts the send workflow into a template (`format` then `deliver`) while leaving the channel-specific details to subclasses. The caller just calls `send()` — the abstraction hides whether it is an email, SMS, or push notification.
