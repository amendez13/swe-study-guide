# Object Oriented Programming Concepts

A distilled concept reference for studying object-oriented programming, synthesized from the five course outlines in [course_outlines.md](course_outlines.md). The strongest OOP courses usually teach through a host language such as Java, Python, or C#, but the durable value is the model: how to represent behavior, state, collaboration, and change in software.

---

## 1. OOP As a Modeling Approach

- **Object-oriented programming** — a way to structure software around collaborating objects that combine state and behavior, rather than treating data and procedures as completely separate concerns.
- **Why OOP exists** — its real goal is not "making code look like the real world," but managing complexity so large systems stay understandable, changeable, and reusable.
- **Objects as software boundaries** — well-designed objects give you stable seams where behavior can evolve without forcing unrelated code to change.

## 2. Classes, Objects, and Instances

- **Class** — the blueprint that defines what data an object carries and what operations it supports.
- **Object / instance** — a runtime realization of a class with its own current state in memory.
- **Instantiation** — the act of creating an object from a class, usually through a constructor or equivalent creation mechanism.
- **Object identity** — one object can be distinct from another even if their field values currently match; identity matters for references, lifecycle, and behavior.

## 3. State, Behavior, and Responsibility

- **State** — the data stored inside an object that determines its current condition.
- **Behavior** — the methods an object exposes to act on its own state or collaborate with other objects.
- **Responsibility** — the specific reason an object exists in the design; if a class accumulates unrelated responsibilities, it usually becomes hard to change safely.
- **Thread of identity** — some objects represent long-lived entities whose identity persists even as their fields change over time.

## 4. Abstraction

- **Abstraction** — highlighting the properties and operations that matter while hiding irrelevant detail.
- **Conceptual abstraction** — the design-level question of what concepts belong in the model at all.
- **Programmatic abstraction** — the code-level interface that lets callers use a capability without needing its internals.
- **Useful abstraction boundary** — a good abstraction makes code easier to read and easier to change; a bad one just renames complexity.

## 5. Encapsulation and Information Hiding

- **Encapsulation** — bundling state and behavior so that the object controls how its data changes.
- **Information hiding** — preventing callers from depending on internals they should not know about.
- **Access modifiers** — language features such as `private`, `protected`, and `public` that enforce visibility boundaries.
- **Integrity-preserving methods** — instead of exposing raw fields everywhere, objects should expose operations that preserve invariants.

## 6. Messages and Collaboration

- **Message passing** — objects interact by calling methods or sending requests to one another rather than reaching into each other's internals.
- **Behavior-first design** — a useful object model focuses on what collaborators ask an object to do, not just what data it stores.
- **Collaboration graph** — software behavior often emerges from many objects working together, so relationships matter as much as single classes.

## 7. Finding Classes from Requirements

- **Noun-based class discovery** — a common starting point is scanning requirements for domain nouns that may represent entities, value types, or services.
- **Use cases and actors** — requirements become clearer when you map who interacts with the system and what goals they are trying to accomplish.
- **CRC cards** — Class-Responsibility-Collaborator cards are a lightweight way to test whether classes have coherent jobs and realistic collaborators.
- **Domain vocabulary** — naming should reflect the actual language of the problem domain, not arbitrary implementation details.

## 8. Relationships Between Objects

- **Association** — a general relationship where one object knows about or works with another.
- **Aggregation** — a whole-part relationship where parts can exist independently of the whole.
- **Composition** — a stronger whole-part relationship where the whole owns the lifecycle of its parts.
- **Collaboration vs containment** — some objects merely work together; others are structurally part of one another, and the design should make that distinction explicit.

## 9. Inheritance and Generalization

- **Inheritance** — defining a subtype in terms of a more general supertype so shared behavior and contracts can be reused.
- **Generalization** — the modeling move from specific classes to a more abstract shared concept.
- **Abstract classes** — partially specified types that provide common structure or behavior but are not intended to be instantiated directly.
- **Subclassing tradeoff** — inheritance can be powerful, but it tightly couples subclasses to superclass design decisions.

## 10. Polymorphism

- **Polymorphism** — the ability to treat different concrete types through a common contract and let runtime dispatch choose the right behavior.
- **Subtype polymorphism** — the classic OOP case where subclasses override behavior from a shared base type.
- **Interface-based polymorphism** — multiple unrelated types can still be interchangeable if they implement the same interface.
- **Why polymorphism matters** — it reduces conditional logic and lets new behavior be added by extension rather than by editing central decision code.

## 11. Interfaces and Contracts

- **Interface** — a behavior contract that says what operations a type supports without fixing one implementation.
- **Programming to an interface** — depend on capabilities, not concrete classes, so collaborators stay swappable.
- **Contract stability** — interfaces are promises to callers; once other code depends on them, changes become expensive and risky.
- **Generalization with interfaces** — interfaces often model roles better than deep inheritance hierarchies do.

## 12. Composition Over Inheritance

- **Favor composition over inheritance** — reuse behavior by wiring objects together rather than always subclassing.
- **Why composition is safer** — it avoids fragile base-class coupling and makes dependencies more explicit.
- **Composition root** — in larger systems, object assembly is often centralized so the rest of the code can focus on behavior rather than construction.
- **Dependency injection** — supplying collaborators from the outside instead of constructing them internally, which improves flexibility and testability.

## 13. Construction and Lifecycle

- **Constructor** — the mechanism that creates an object and establishes its initial valid state.
- **Default vs parameterized construction** — some objects can start from sensible defaults, while others require explicit data to be valid.
- **Initialization invariants** — the object should be usable immediately after construction; if callers must remember extra setup steps, the design is usually weak.
- **Lifecycle ownership** — when one object creates or owns another, it often also owns cleanup, replacement, or persistence decisions.

## 14. Mutability, Immutability, and Object Parameters

- **Mutable object** — an object's state can change after creation.
- **Immutable object** — once created, the object's observable state does not change; this often simplifies reasoning and sharing.
- **Objects as parameters** — passing objects between methods shares behavior and identity, not just copied primitive values.
- **Returning objects** — methods often return richer domain objects instead of raw data so behavior stays close to the state it belongs to.

## 15. Class-Level vs Instance-Level Members

- **Instance members** — fields and methods that belong to a specific object.
- **Class / static members** — members that belong to the class itself rather than any one instance.
- **Static overuse risk** — static utilities are convenient, but overusing them can push behavior out of objects and weaken encapsulation.
- **Shared state caution** — class-level mutable state increases coupling and can introduce hidden dependencies.

## 16. Overloading, Overriding, and Dynamic Dispatch

- **Method overloading** — multiple methods share a name but differ by parameter list; this is compile-time convenience, not polymorphism by itself.
- **Method overriding** — a subtype provides specialized behavior for a method defined higher in the hierarchy.
- **Dynamic dispatch** — runtime type determines which overridden implementation actually runs.
- **Behavioral substitutability** — overriding is only safe when the subtype still honors the expectations established by the supertype.

## 17. Data Structures vs Objects

- **Object** — encapsulates both data and the operations that maintain its rules.
- **Data structure** — mainly exposes data and relies on external code to decide behavior.
- **Anemic model warning** — if "objects" are just bags of fields and all logic lives elsewhere, you often lose most benefits of OOP.
- **Pragmatic balance** — some systems legitimately use both objects and data structures; the key is making the tradeoff intentional.

## 18. Cohesion, Coupling, and Separation of Concerns

- **Cohesion** — how strongly the contents of a class or module belong together.
- **Coupling** — how much one part of the system depends on details of another.
- **Separation of concerns** — each part of the system should focus on a distinct problem so changes stay localized.
- **Conceptual integrity** — a design feels coherent when similar ideas are expressed consistently across the codebase.
- **Single Responsibility Principle** — a class should have one main reason to change, which is a practical cohesion test.

## 19. SOLID Principles

- **SOLID** — a five-part set of object-oriented design heuristics that push code toward lower coupling, clearer responsibilities, and safer extension.
- **Single Responsibility Principle (SRP)** — a class should have one primary reason to change; if one type mixes policy, persistence, formatting, and orchestration, it usually needs to be split.
- **Open/Closed Principle (OCP)** — software should be open to extension but closed to risky modification, so new behavior is usually added by introducing new types or strategies instead of editing stable core logic.
- **Liskov Substitution Principle (LSP)** — a subtype must remain safely usable anywhere its supertype is expected; overriding methods must preserve the base contract instead of surprising callers.
- **Interface Segregation Principle (ISP)** — prefer small, focused interfaces over large omnibus ones so clients depend only on the capabilities they actually use.
- **Dependency Inversion Principle (DIP)** — high-level policy should depend on abstractions, not low-level concrete details; this keeps orchestration code from being tightly bound to specific implementations.

## 20. Reusable Components and Patterns

- **Reusable component** — a class or module designed so other code can adopt it without dragging in accidental assumptions.
- **Observer pattern** — one object publishes change notifications to interested subscribers.
- **Strategy pattern** — interchangeable algorithms share one interface so callers can swap behavior cleanly.
- **Facade pattern** — a simplified front door over a more complex subsystem.
- **Singleton caution** — a single global instance can be useful in narrow cases, but it often hides dependencies and makes tests harder.

## 21. UML and Visual Modeling

- **UML class diagram** — shows classes, attributes, operations, and structural relationships.
- **UML sequence diagram** — models the order of messages exchanged during a scenario.
- **UML state diagram** — shows how an object moves between states over time.
- **Model-to-code translation** — good OOP practice includes moving fluently between visual models, requirements, and code.

## 22. Persistence, Components, and Distributed OO

- **Persistence** — storing object state beyond process lifetime; this forces you to think about identity, reconstruction, and consistency.
- **Component architecture** — larger systems group objects into higher-level components with clearer boundaries.
- **Distributed objects** — once objects cross process or network boundaries, latency, serialization, and failure become part of the design.
- **Local-vs-remote mindset** — code that looks object-oriented at the call site may behave very differently when collaborators are remote.

## 23. Testing and Evolution

- **Unit testing object behavior** — tests should verify the public behavior and invariants of an object, not its private implementation trivia.
- **Mocking through interfaces** — interface boundaries make it easier to isolate collaborators during tests.
- **Refactoring** — object models improve over time; good OOP design supports renaming, extracting classes, and moving behavior without breaking callers.
- **Inheritance pitfalls** — deep hierarchies, hidden side effects, and base-class assumptions are common sources of maintenance pain.

---

## How to use this list

This is a self-check, not a memorization contest. Pick any concept and ask:

1. Can I explain what it is in plain language?
2. Can I recognize it in unfamiliar Java, Python, or C# code?
3. Can I write or refactor a small example that uses it well?

If any answer is "no," that concept is a study target.
