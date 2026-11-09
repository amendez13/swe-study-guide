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

- **Behaviors before classes** — actions and rules first.
- **Core types** — a type owns state or a cluster of actions.
- **One job** — the holder of the data is the object you ask.
- **Collaboration** — one scenario, as messages.
- **Composition** — the default relationship; inherit only for real substitutability.
- **Interface** — when the implementation is allowed to change.
- **Stop early** — leave storage and UI out until asked.

## 3. Testing

- **Promises** — the caller-visible behavior worth pinning.
- **Unit vs integration** — one function, or a seam between two parts.
- **Arrange, act, assert** — one behavior per test.
- **Edges** — empty, zero, the limit, the first illegal value.
- **Doubles** — stub a value, fake a dependency, mock a call you must observe.
- **Fail first** — the test should fail for the reason you named.

## 4. Databases and SQL

- **Keys** — primary key identifies, foreign key references.
- **Joins** — inner drops unmatched rows, left keeps them, one-to-many multiplies.
- **Filter and group** — `WHERE` on rows, `HAVING` on groups.
- **Indexes** — justified by a named lookup, paid for on writes.
- **Transactions** — the pair of writes that must commit together.
- **Normalization** — one fact in one place, unless a stated read justifies a copy.

## 5. Threads and Locks

- **Shared heap** — the objects both threads can name.
- **Race** — a read-modify-write split across threads drops an update.
- **Critical section** — the lock is held only around that shared update.
- **Deadlock** — a cycle of waits; a global lock order breaks it.
- **Condition wait** — sleep without holding the lock, then re-check.

## 6. Moderate Problems

- **One insight** — bookkeeping or an ordering, not a new algorithm.
- **Brute force first** — a specification and a fallback.
- **Named lookup** — the structure exists to answer one question cheaply.
- **Safe discard** — a reason a region cannot hold the answer.
- **Cross-check** — faster idea and brute force agree on a tiny input.

## 7. Hard Problems

- **Model first** — the subproblem in one sentence.
- **Shrinking argument** — plus a base case in the same vocabulary.
- **Cache key** — exactly the arguments the answer depends on.
- **Math rewrite** — only after it matches the brute force on small inputs.
- **Small state** — extra fields multiply the work.
- **Slow and correct** — hand it in, and label the faster idea as a plan.

---

## How to use this list

Pick a line and explain it with a fresh example. For Math and Logic Puzzles, the drills are the check. For the outline topics, being able to expand the line into a short paragraph is the check; those chapters are not written out yet.
