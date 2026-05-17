# Object-Oriented Programming — Concept Reference

A distilled, sectioned concept reference synthesized from five highly rated OOP courses. Every entry is something a student should be able to explain, recognize in code, and apply.

---

## 1. Classes and Objects

**Class** — A blueprint that defines the structure (fields) and behavior (methods) of a type. A class declares what data an object holds and what operations it supports.

**Object** — A runtime instance of a class. Each object occupies its own memory, holds its own state in fields, and responds to method calls defined by its class.

**Instance Variable (Field / Attribute)** — A variable declared inside a class that stores per-object state. Each object gets its own copy.

**Method** — A function defined on a class that operates on or returns information about an object's state. Methods give objects behavior.

**Constructor** — A special method invoked when an object is created. Constructors initialize fields and enforce invariants before the object is usable.

**The `this` / `self` Reference** — An implicit reference inside a method that points to the object the method was called on. Used to disambiguate fields from parameters and to pass the current object to other methods.

**Object Identity vs. Equality** — Identity (`==` in Java) checks whether two references point to the same object in memory. Equality (`.equals()`) checks whether two objects are logically equivalent based on their state.

**Reference Semantics** — In most OOP languages, variables hold references (pointers) to objects, not the objects themselves. Assignment copies the reference, not the object — both variables then alias the same object.

---

## 2. Encapsulation

**Access Modifiers** — Keywords (`public`, `private`, `protected`, package-private) that control which code can read or write a class's fields and methods. The primary mechanism for enforcing encapsulation.

**Information Hiding** — The practice of exposing only the operations callers need (the interface) and hiding internal representation. Lets the implementation change without breaking clients.

**Getters and Setters (Properties)** — Methods that provide controlled read and write access to private fields. Setters can enforce validation; getters can compute derived values.

**Interface vs. Implementation** — The interface is the set of public methods a class exposes. The implementation is the private internal logic. Encapsulation keeps the two independent so either can evolve.

**Immutability** — An object whose state cannot change after construction. Immutable objects are simpler to reason about, safe to share across threads, and free from aliasing bugs.

---

## 3. Abstraction

**Abstraction (Principle)** — Modeling only the relevant characteristics of a real-world entity for the problem at hand, ignoring irrelevant detail. The first step in translating a domain into classes.

**Abstract Class** — A class that cannot be instantiated directly. It exists to define a partial implementation and common interface that concrete subclasses complete.

**Abstract Method** — A method declared without a body, requiring every concrete subclass to supply its own implementation. Forces subclasses to honor a contract.

**CRC Cards (Class–Responsibility–Collaborator)** — A lightweight analysis technique for identifying candidate classes, what each class is responsible for, and which other classes it works with.

**Domain Modeling** — The process of identifying the key entities, their attributes, and their relationships in a problem domain before writing code. Drives class design from requirements.

---

## 4. Inheritance

**Subclass / Superclass** — A subclass (child) extends a superclass (parent), inheriting its fields and methods. The subclass can add new members or override inherited behavior.

**Method Overriding** — Redefining an inherited method in a subclass to change or extend its behavior. The overriding method must match the signature of the parent method.

**Constructor Chaining** — When a subclass constructor explicitly calls its superclass constructor (via `super()`) to ensure the parent's state is initialized before the child adds its own.

**The Singly Rooted Hierarchy** — In languages like Java, every class ultimately extends `Object`. This guarantees a common baseline interface (`toString()`, `equals()`, `hashCode()`) for all objects.

**`final` and Sealed Classes** — `final` prevents a class from being subclassed or a method from being overridden. Sealed classes restrict which classes may extend them, offering controlled extensibility.

**Protected Access** — A visibility level that allows subclasses (and same-package code, in Java) to access a member. Sits between `private` (too restrictive for inheritance) and `public` (too open).

**Fragile Base Class Problem** — The risk that changes to a superclass inadvertently break subclass behavior. A core reason to favor composition over inheritance and to design carefully for extension.

---

## 5. Polymorphism

**Polymorphism (Runtime / Dynamic Dispatch)** — The ability to call a method on a superclass reference and have the actual subclass implementation execute at runtime. The cornerstone of extensible OOP code.

**Upcasting** — Treating a subclass object as an instance of its superclass type. Happens implicitly and is always safe because the subclass "is-a" superclass.

**Downcasting** — Casting a superclass reference back to a subclass type. Requires an explicit cast and a runtime check (`instanceof`) because it can fail if the object is not actually that subclass.

**The "Is-a" Relationship** — The semantic test for inheritance: if "a Dog is-a Animal" makes sense in the domain, then `Dog extends Animal` is appropriate. If it doesn't, use composition instead.

**Method Overloading** — Defining multiple methods with the same name but different parameter lists within a single class. Resolved at compile time (static polymorphism), not runtime.

**Type Substitutability** — Any code that works with a superclass type should work correctly with any subclass instance, without knowing the concrete type. The behavioral foundation of polymorphism.

---

## 6. Interfaces and Abstract Types

**Interface** — A contract that declares method signatures without implementations. A class "implements" an interface by providing bodies for all declared methods.

**Multiple Interface Implementation** — A class can implement several interfaces, gaining multiple roles without the diamond-problem ambiguity of multiple inheritance.

**Default Methods** — Methods defined in an interface with a body (Java 8+). Allow interfaces to evolve without breaking all existing implementors.

**Programming to Interfaces** — Declaring variables, parameters, and return types as interface types rather than concrete classes. Decouples calling code from specific implementations.

**Functional Interface** — An interface with exactly one abstract method (Java). Can be instantiated with a lambda expression, bridging OOP and functional style.

---

## 7. Object Composition and Relationships

**Association** — A general relationship where one object uses or interacts with another. The weakest form of coupling between classes.

**Aggregation** — A "has-a" relationship where the container holds references to parts, but the parts can exist independently (e.g., a department has employees, but employees outlive the department).

**Composition** — A strong "has-a" relationship where the container owns the parts and controls their lifecycle. When the container is destroyed, so are the parts (e.g., a house and its rooms).

**Dependency** — A transient relationship where one class uses another only within a method scope (parameter, local variable). The weakest and most desirable form of coupling.

**Favor Composition Over Inheritance** — A design guideline that recommends building behavior by composing objects rather than extending classes. Composition is more flexible, avoids the fragile base class problem, and makes testing easier.

**Delegation** — A pattern where an object forwards a request to a contained helper object instead of handling it directly. The mechanism behind composition-based reuse.

---

## 8. SOLID Principles

**Single Responsibility Principle (SRP)** — A class should have only one reason to change. Each class should encapsulate one concern; when a class does too much, split it.

**Open/Closed Principle (OCP)** — Classes should be open for extension but closed for modification. New behavior is added by creating new subclasses or implementations, not by editing existing code.

**Liskov Substitution Principle (LSP)** — Subtypes must be substitutable for their base types without altering the correctness of the program. If a subclass weakens a postcondition or strengthens a precondition, it violates LSP.

**Interface Segregation Principle (ISP)** — Clients should not be forced to depend on methods they do not use. Prefer several small, focused interfaces over one large, general-purpose interface.

**Dependency Inversion Principle (DIP)** — High-level modules should not depend on low-level modules; both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

---

## 9. Design Principles and Heuristics

**Coupling** — The degree to which one class depends on the internals of another. Low coupling means classes interact through narrow, well-defined interfaces and are easier to change independently.

**Cohesion** — The degree to which the members of a class belong together. High cohesion means a class has a focused purpose; low cohesion means it mixes unrelated responsibilities.

**Separation of Concerns** — Dividing a system so that each module addresses a distinct concern (e.g., UI, business logic, persistence). Reduces coupling and improves maintainability.

**Conceptual Integrity** — A system designed as if one mind conceived it. Achieved by consistent naming, uniform patterns, and resisting ad-hoc special cases.

**Principle of Least Knowledge (Law of Demeter)** — An object should only talk to its immediate neighbors — its own fields, parameters, and objects it creates — not to objects returned by those neighbors.

**Tell, Don't Ask** — Instead of querying an object's state and making decisions externally, tell the object what to do and let it use its own state internally.

**DRY (Don't Repeat Yourself)** — Every piece of knowledge should have a single, unambiguous representation in the system. Duplicated logic is a sign of missing abstraction.

---

## 10. Creational Design Patterns

**Singleton** — Ensures a class has exactly one instance and provides a global access point to it. Useful for shared resources (configuration, connection pools) but can hinder testability.

**Factory Method** — Defines an interface for creating objects but lets subclasses decide which concrete class to instantiate. Decouples object creation from the code that uses the object.

**Abstract Factory** — Provides an interface for creating families of related objects without specifying their concrete classes. Common when a system must support multiple product variants.

**Builder** — Separates the construction of a complex object from its representation, allowing the same construction process to produce different representations. Useful when constructors have many optional parameters.

**Prototype** — Creates new objects by cloning an existing instance rather than calling a constructor. Useful when object creation is expensive or configuration-heavy.

---

## 11. Structural Design Patterns

**Adapter** — Converts the interface of an existing class into one that a client expects. Lets classes with incompatible interfaces work together without modifying either.

**Facade** — Provides a simplified interface to a complex subsystem. Reduces the number of objects a client must interact with.

**Composite** — Composes objects into tree structures to represent part-whole hierarchies. Lets clients treat individual objects and compositions uniformly.

**Proxy** — Provides a surrogate or placeholder for another object to control access to it (lazy loading, access control, logging).

**Decorator** — Attaches additional behavior to an object dynamically by wrapping it in another object with the same interface. An alternative to subclassing for extending functionality.

**Bridge** — Separates an abstraction from its implementation so the two can vary independently. Useful when both the interface and the implementation need to be extended.

---

## 12. Behavioral Design Patterns

**Observer** — Defines a one-to-many dependency so that when one object (the subject) changes state, all dependents (observers) are notified and updated automatically. Foundation of event-driven systems.

**Strategy** — Defines a family of interchangeable algorithms, encapsulates each one, and makes them interchangeable at runtime. Eliminates conditional logic for algorithm selection.

**Template Method** — Defines the skeleton of an algorithm in a base class method, deferring some steps to subclasses. Subclasses customize behavior without changing the algorithm's structure.

**Command** — Encapsulates a request as an object, allowing parameterization of clients with different requests, queuing, logging, and undo/redo support.

**State** — Allows an object to change its behavior when its internal state changes, appearing to change its class. Eliminates large conditional state-transition logic.

**Chain of Responsibility** — Passes a request along a chain of handlers until one handles it. Decouples sender from receiver and allows dynamic handler composition.

**Iterator** — Provides a way to access elements of a collection sequentially without exposing the collection's internal structure.

**Mediator** — Defines an object that centralizes communication between components, reducing direct dependencies between them.

---

## 13. Architectural Patterns

**Model-View-Controller (MVC)** — Separates an application into three concerns: the Model (data and business logic), the View (presentation), and the Controller (input handling and coordination). The most widely taught architectural pattern for interactive applications.

**Layered Architecture** — Organizes code into horizontal layers (presentation, business logic, data access), each depending only on the layer below. Enforces separation of concerns at the architectural level.

**Repository Pattern** — Abstracts data access behind a collection-like interface, decoupling business logic from the specifics of storage (database, file, API).

---

## 14. UML and Visual Modeling

**UML Class Diagram** — Shows classes, their fields and methods, and the relationships (inheritance, composition, association, dependency) between them. The primary visual tool for OOP design.

**UML Sequence Diagram** — Shows how objects interact over time by depicting the order of method calls between them. Useful for understanding dynamic behavior of a use case.

**UML State Diagram** — Models the states an object can be in and the transitions between those states triggered by events. Useful for objects with complex lifecycle behavior.

**UML Use Case Diagram** — Captures the functional requirements of a system by showing actors and the use cases they interact with. A high-level view before diving into class design.

**Model Checking** — Verifying that a UML model satisfies certain properties or constraints before translating it into code. Catches design errors early.

---

## 15. Object Lifecycle and Memory

**Object Creation and Initialization** — The sequence of allocating memory, calling the constructor, initializing fields, and returning a reference. Understanding this sequence prevents partially-initialized-object bugs.

**Garbage Collection** — Automatic reclamation of memory occupied by objects that are no longer reachable. Eliminates manual memory management but requires understanding of object reachability.

**Null Reference** — A reference that points to nothing. The source of `NullPointerException` / `NullReferenceException`, one of the most common runtime errors. Defensive coding, Optional types, and null-object patterns mitigate it.

**Aliasing** — When multiple references point to the same object. Changes through one alias are visible through all others — a common source of bugs when mutability and aliasing combine.

**Autoboxing / Unboxing** — Automatic conversion between primitive types and their wrapper objects (e.g., `int` ↔ `Integer` in Java). Convenient but has performance and equality-comparison pitfalls.

---

## 16. Generics and Type Parameterization

**Generic Class** — A class parameterized by one or more types (e.g., `List<T>`). Provides type safety and code reuse without casting.

**Generic Method** — A method that declares its own type parameters, independent of the enclosing class. Useful for utility methods that operate on arbitrary types.

**Bounded Type Parameters** — Constraints on type parameters (e.g., `<T extends Comparable<T>>`) that guarantee the type supports certain operations. Combines generics with polymorphism.

**Wildcards** — Flexible type arguments (`?`, `? extends T`, `? super T`) that allow methods to accept a range of parameterized types while preserving type safety.

**Type Erasure** — The mechanism (in Java) by which generic type information is removed at compile time and replaced with casts. Explains why you cannot create generic arrays or use `instanceof` with type parameters.

---

## 17. Code Smells and Refactoring

**Code Smell** — A surface-level indicator in code that often corresponds to a deeper design problem. Not a bug, but a hint that the design may need improvement.

**Long Method / Large Class** — A method or class that does too much. Violates SRP and is harder to test, understand, and modify. Fix by extracting methods or splitting classes.

**Feature Envy** — A method that uses more data from another class than from its own. Suggests the method belongs in the other class.

**Shotgun Surgery** — A single change requires modifications across many classes. Indicates scattered responsibility that should be consolidated.

**Refused Bequest** — A subclass inherits methods or data it doesn't need or use. Suggests the inheritance hierarchy is wrong; composition may be more appropriate.

**Refactoring** — Restructuring existing code without changing its external behavior. Extract Method, Move Method, Replace Conditional with Polymorphism, and Introduce Parameter Object are common refactorings in OOP contexts.

---

## 18. Testing Object-Oriented Code

**Unit Testing** — Testing individual classes and methods in isolation to verify they behave correctly. The primary feedback loop for OOP code quality.

**Test-Driven Development (TDD)** — Writing a failing test before writing the production code that makes it pass. Forces design to emerge from usage rather than speculation.

**Test Doubles (Mocks, Stubs, Fakes)** — Objects that stand in for real dependencies during testing. Enable isolation of the class under test from its collaborators.

**Testability and Design** — Classes with low coupling, dependency injection, and interface-based collaborators are easier to test. Difficulty writing tests is itself a design feedback signal.

---

## 19. Dependency Injection and Inversion of Control

**Dependency Injection (DI)** — Supplying an object's dependencies from the outside (via constructor, setter, or method parameter) rather than having the object create them itself. Decouples creation from use.

**Inversion of Control (IoC)** — A broader principle where the flow of control is inverted: a framework or container calls your code, rather than your code calling library functions. DI is one form of IoC.

**Constructor Injection** — Passing all required dependencies through the constructor. The most common and recommended form of DI because it makes dependencies explicit and enforces completeness.

**Service Locator** — A registry that objects query to find their dependencies at runtime. An alternative to DI that centralizes dependency resolution but hides dependencies from the class signature.

---

## 20. Event-Driven and Reactive Patterns

**Event-Driven Programming** — A paradigm where program flow is determined by events (user actions, sensor outputs, messages). Objects publish events; other objects subscribe and react.

**Event Handler / Listener** — A method or object registered to respond to a specific event. The Observer pattern is the OOP realization of this concept.

**Callback** — A method (or lambda) passed to another object to be invoked later when a condition is met. A lightweight form of the strategy and observer patterns.

**Lambda Expression** — An anonymous function that can be passed as a value. In OOP languages, lambdas implement functional interfaces and reduce boilerplate for event handlers, comparators, and strategy objects.

---

## Self-Check Rubric

For each concept above, ask yourself:

1. **Can I explain it?** — Could I describe this concept clearly to another developer in two sentences without looking it up?
2. **Can I recognize it?** — If I saw this concept in unfamiliar code, would I identify it and understand why it's there?
3. **Can I apply it?** — Could I write a small, correct example demonstrating this concept from scratch?

If the answer is "no" to any of these for a given concept, that concept is a study gap worth revisiting.
