# Coding Problems Concepts

A distilled checklist for the Coding Problems section. The teachable writeups live in the topic directories. This list is a self-check. It does not copy book text, problem statements, or solutions.

---

## 1. Math and Logic Puzzles

- **Divisibility** — remainder zero; digit-sum rules for 3 and 9; last-two-digits rule for 4.
- **Checking for primality** — trial division through `floor(sqrt(n))`; 1 is not prime; prefer `math.isqrt`.
- **Sieve of Eratosthenes** — cross off multiples starting at `p*p` when you need every prime up to `n`.
- **Probability of A and B** — `P(A) * P(B | A)`; the product of the bare probabilities requires independence.
- **Probability of A or B** — add both, then subtract the overlap so it is not counted twice.
- **Independence** — one event gives no information about the other.
- **Mutual exclusivity** — empty overlap; "or" becomes a sum; positive disjoint events are dependent.
- **Start talking** — restate the assumption and solve a smaller case out loud.
- **Develop rules and patterns** — first cases, differences, then a fresh case that tries to break the rule.
- **Worst case shifting** — split as evenly as the number of test outcomes allows; `k` tests cover at most `b^k` cases.
- **Algorithm approaches** — name the brute force, then match sieve, Euclid, or squaring to what the question asks for.
- **GCD and LCM** — Euclid's remainder loop; divide out the GCD before multiplying to get the LCM.
- **Modular arithmetic** — reduce before add and multiply; a negative remainder may need normalizing.
- **Fast exponentiation** — square for each bit of the exponent and reduce mod `m` on every multiply.
- **Overflow awareness** — `lo + (hi - lo) / 2` instead of adding the endpoints; do not build a huge power just to reduce it once.

## 2. Object-Oriented Design

- **Handle ambiguity** — pin actors, rules, and what is out of scope, then design.
- **Define the core objects** — a type owns changing state; barcodes and limits are fields.
- **Analyze relationships** — has-a, knows-a, or is-a, with cardinality.
- **Investigate actions** — the method sits on the object that has the data. Walk one scenario.
- **Encapsulation** — operations protect the invariant; callers do not assign the fields.
- **Inheritance** — a child must be usable wherever the parent is.
- **Polymorphism** — call the interface; do not switch on the concrete type.
- **Composition over inheritance** — vary a part or a policy by holding it, not by subclassing combinations.
- **Interfaces vs abstract classes** — a capability with no shared data is an interface. An abstract class needs real shared code.
- **SOLID** — one reason to change, extension by new types, safe subtypes, small interfaces, depend on those interfaces.
- **Singleton** — one global instance. Pass the object in unless uniqueness is real.
- **Factory method** — one place picks the concrete type. Callers keep the interface.
- **Strategy** — a swappable algorithm in a field.
- **Observer** — the subject notifies listeners it does not import.
- **Decorator and Adapter** — same interface plus behavior, versus a translation of a foreign interface.
- **State machines** — name the legal edges. A table is enough until each state has real behavior.

## 3. Testing

- **What the interviewer is looking for** — cases and reasons, not a framework name.
- **Testing a real-world object** — happy path, invalid input, already-done, and two actors at once.
- **Manual vs automated** — explore by hand; automate a check you can state and will re-run.
- **Black-box vs white-box** — the promise first, then paths you only see in the code.
- **Testing a function** — one call, one promise, including a boundary and a refusal.
- **Unit, integration, and end-to-end** — the layer that can name the bug.
- **The test pyramid** — many function tests, fewer seam tests, few end-to-end tests.
- **Equivalence classes** — one representative for inputs the promise treats alike.
- **Boundary values** — the last input of one class and the first of the next.
- **Edge and error cases** — legal extremes versus refused inputs.
- **Stubs, fakes, and mocks** — a canned value, a working stand-in, or a record of calls.
- **Property-based testing** — a rule that holds across many inputs.
- **Flaky tests and determinism** — inject the clock and isolate state. Do not retry the cause away.
- **Load and security basics** — a workload with a pass line, and refusals for unauthorized input.
- **Troubleshooting questions** — pin who, where the number appears, and one example.
- **A troubleshooting sequence** — expected behavior, reproduction, layer, boundary, then a test.

## 4. Databases and SQL

- **Explicit joins** — the match belongs in `ON`. A comma join with no predicate is a cross join.
- **Inner, left, and full** — inner drops unmatched rows. Left keeps the left side. Full keeps both.
- **Self join and anti-join** — alias a table to pair rows with each other. `NOT EXISTS` means no partner.
- **Statements** — name the rows an `UPDATE` or `DELETE` will touch.
- **WHERE, GROUP BY, HAVING** — filter rows, collapse, then filter groups.
- **NULL** — unknown. Use `IS NULL`. `COUNT(col)` skips nulls.
- **CTE** — name a grouped result so a later filter can average it.
- **Windows** — `ROW_NUMBER` picks one row. `RANK` ties and skips. A running sum does not collapse rows.
- **Normal forms** — one value per column, dependence on the whole key, no dependence between non-key columns.
- **Keys** — primary key identifies. Foreign key rejects a child with no parent.
- **Indexes** — equality columns, then the range. Cover the columns you return.
- **Transactions and isolation** — commit related writes together. Add to a total in one `UPDATE`.
- **Denormalize** — copy a fact only with the query and the refresh story.
- **Small design** — pin what a sale is, then name tables, cardinality, and the first statement.
- **Large design** — partition or archive by the date you already filter. Leave shards to system design.

## 5. Threads and Locks

- **Threads vs processes** — threads share a heap. Processes do not, unless you ask them to.
- **Java threads** — `start` is concurrent. `synchronized (obj)` locks that object.
- **Race** — a split read-modify-write loses an update.
- **Mutex, semaphore, monitor** — one holder, a count of permits, or a lock plus a wait set.
- **Condition** — wait in a loop. The wait releases the lock.
- **Producer-consumer** — bound the queue. Signal after the item is visible.
- **Readers and writers** — many readers or one writer. Do not starve the writer.
- **CAS** — one word. Not two fields that must move together.
- **Pool** — fixed workers, bounded queue, a rejection policy. Do not wait on the same pool.
- **Deadlock** — four Coffman conditions. Break the cycle with a lock order.
- **Livelock and starvation** — motion without progress, or a thread that is never chosen.
- **Visibility** — a lock or `volatile` publishes a write. `volatile` is not an increment.
- **GIL** — one Python bytecode thread. I/O overlaps. Invariants still need a lock.

## 6. Moderate Problems

- **One insight** — a count, an order, a window, or a formula, plus its cost.
- **Bits and swaps** — flags in a word. XOR swap only when the two locations differ.
- **Overflow** — subtract before you add a midpoint. Reduce a product early.
- **Map, pointers, window, prefix** — expected O(n) counts, a sorted scan, a monotone window, a range in O(1).
- **Sort, then scan** — neighbors answer closest and next-change.
- **Intervals and machines** — merge overlaps after sorting by start. Name states before the event loop.
- **Digits, modulo, gcd** — peel digits, wrap with `%`, cut two lengths with Euclid.
- **Edges** — empty, one element, all equal, and the boundary value. Check the shortcut on a tiny input.

## 7. Hard Problems

- **Brute force first** — a correct slow answer, then one layer of repeated work removed.
- **Bits** — XOR for differing flags. Carry is `(a & b) << 1`.
- **Shuffle and reservoir** — Fisher-Yates on the suffix. `k` uniform items from a stream in O(k) memory.
- **Heaps** — size-k heap for top-k. Two heaps for a running median.
- **Trie and union-find** — shared prefixes for many patterns. Roots for "joined or not."
- **Monotonic stack** — next taller item in one left-to-right pass.
- **String DP and divide and conquer** — prefix cells for a subsequence. Merge sort counts inversions.
- **One-change search** — BFS on codes that differ by one character.
- **Majority and buckets** — cancel pairs, then verify. Small integer ranges sort by counting.
- **Candidate** — if the check fails, the answer is none.

---

## How to use this list

Pick a line and explain it with a fresh example. For every Coding Problems topic, the drills are the check.
