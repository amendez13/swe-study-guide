# Coding Problems Source Outline

Original study outline for the coding-problem chapters that are not already covered elsewhere in this guide. Data structures, bit manipulation, recursion, and sorting stay in `07_Data_Structures_and_Algorithms`. System design stays in `09_System_Design_Interview`. Language-specific chapters are omitted. This file names themes and section headings. It does not copy book text, problem statements, or solutions.

---

## 1. Math and Logic Puzzles (Chapter 6)

**Scope:** Number facts used in interviews, probability of combined events, and a way to talk through a puzzle when the algorithm is not obvious.

**Status:** Fully written topic, with concepts, notes, and drills.

### Section headings to cover

- Prime numbers
  - Divisibility
  - Checking for primality
  - Generating a list of primes with the Sieve of Eratosthenes
- Probability
  - Probability of A and B
  - Probability of A or B
  - Independence
  - Mutual exclusivity
- Start talking
- Develop rules and patterns
- Worst case shifting
- Algorithm approaches

### Also required for an interview-complete pass

- GCD and LCM via Euclid's algorithm, dividing before multiplying
- Modular addition and multiplication, and the sign of a remainder
- Exponentiation by squaring, including reduction at every step
- Overflow awareness, including a midpoint that does not add two large endpoints
- A few classic puzzle-reasoning drills, written in original words

---

## 2. Object-Oriented Design (Chapter 7)

**Scope:** Turning a short product description into types, relationships, and one walked scenario, then naming the object rules and patterns that keep the design extensible.

**Status:** Concepts, notes, and drills.

### Themes

- Handle ambiguity, name the core objects, analyze relationships, investigate actions
- Encapsulation, inheritance, polymorphism, composition over inheritance
- Interfaces versus abstract classes, and SOLID as a check on a design you already drew
- Singleton and factory method
- Strategy, Observer, Decorator, Adapter, and state machines
- Say the extensibility trade-off out loud, including what this round will not build

---

## 3. Testing (Chapter 11)

**Scope:** How to choose cases for a real object, a program, and a function, and how to narrow a reported symptom.

**Status:** Concepts, notes, and drills.

### Themes

- What an interviewer is listening for
- Manual versus automated, and black-box versus white-box
- Unit, integration, end-to-end, and the test pyramid
- Equivalence classes, boundaries, edges, and refusals
- Stubs, fakes, mocks, properties, and deterministic tests
- Load and security checks at the level of a pass line and a refusal
- A troubleshooting sequence that finds the layer before the patch

---

## 4. Databases and SQL (Chapter 14)

**Scope:** Writing interview queries and drawing a logical schema. Replication and sharding stay in the system-design section.

**Status:** Concepts, notes, and drills.

### Themes

- Explicit joins, inner and outer joins, self joins, and anti-joins
- `WHERE`, `GROUP BY`, `HAVING`, NULL, subqueries, CTEs, and window functions
- Normal forms, keys, index order, transactions, and isolation anomalies
- When a copy of a fact is justified
- A small schema from an ambiguous sentence, and what to do when one table grows large

---

## 5. Threads and Locks (Chapter 15)

**Scope:** Shared-memory concurrency at the level of races, locks, and deadlock. Language runtimes are out of scope.

**Status:** Outline only. No drills yet.

### Themes

- Threads share the heap
- Lost updates from a split read-modify-write
- Critical sections and how long a lock is held
- The deadlock cycle and a global lock order
- Condition waits instead of spinning
- Explaining a design by starting from the shared fields

---

## 6. Moderate Problems (Chapter 16)

**Scope:** How to approach a coding problem that has one structural trick. This outline does not list published problems.

**Status:** Outline only. No drills yet.

### Themes

- Restate limits before choosing a tool
- A correct brute force as a specification
- Bookkeeping that removes a repeated scan
- Discarding a region of the input with a reason
- Checking a faster idea against the brute force on a tiny input
- Practice organized by trigger, not by problem title

---

## 7. Hard Problems (Chapter 17)

**Scope:** How to approach a problem whose state is not obvious. This outline does not list published problems.

**Status:** Outline only. No drills yet.

### Themes

- Spend the first minutes defining the subproblem
- An argument that strictly shrinks, plus a base case
- Caching a subproblem under the arguments it actually depends on
- A mathematical rewrite checked against the brute force
- Keeping the state small
- Handing in a correct slower solution, with the faster plan labeled as a plan

---

## Summary

| Topic | Chapter | Status | Focus |
|-------|---------|--------|-------|
| Math and Logic Puzzles | 6 | Concepts, notes, and drills | Primes, probability, puzzle reasoning, Euclid, modular arithmetic |
| Object-Oriented Design | 7 | Concepts, notes, and drills | Types, relationships, SOLID, and a few patterns |
| Testing | 11 | Concepts, notes, and drills | Cases, layers, doubles, and troubleshooting |
| Databases and SQL | 14 | Concepts, notes, and drills | Queries, schema, and indexes, not sharding |
| Threads and Locks | 15 | Outline | Races, locks, deadlock, waiting |
| Moderate Problems | 16 | Outline | One-insight problems, without a problem list |
| Hard Problems | 17 | Outline | State, recursion, caching, without a problem list |
