# Architectural Patterns

Architectural patterns organize an entire application's structure, defining how major components are separated and how they communicate. They apply the same separation-of-concerns idea seen at the class level, but at the scale of modules and layers.

## Key Points

- **MVC** — Model holds data and rules, View renders output, Controller handles input. Changes in one area don't cascade.
- **Layered architecture** — Presentation → Business Logic → Data Access. Each layer depends only on the one below.
- **Repository pattern** — Collection-like interface over storage, decoupling business logic from database details and enabling easy test substitution.

## Example

```java
// Repository interface (data access layer)
public interface TaskRepository {
    List<Task> findAll();
    void save(Task task);
}

// Service (business logic layer)
public class TaskService {
    private final TaskRepository repo;
    public TaskService(TaskRepository repo) { this.repo = repo; }

    public List<Task> listOpen() {
        return repo.findAll().stream()
                   .filter(t -> !t.isDone())
                   .toList();
    }

    public void complete(Task task) {
        task.markDone();
        repo.save(task);
    }
}

// Controller (presentation layer)
public class TaskController {
    private final TaskService service;
    public TaskController(TaskService service) { this.service = service; }

    public String handleListRequest() {
        return service.listOpen().toString();
    }
}
```

Each layer has a single concern: the controller translates HTTP, the service enforces rules, and the repository handles persistence. Swapping the database or the UI framework touches only one layer.
