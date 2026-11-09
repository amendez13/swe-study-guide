# Threads and Locks

This topic is an outline of the concurrency ideas an interview expects you to say clearly: shared memory, lost updates, locks, deadlock, a lock order, and waiting without spinning. The cards are a skeleton. Language-specific memory models and lock-free structures are a later pass.

## Key Points

- **Threads share the heap** — locals are private; objects both threads can reach are shared.
- **A race is an unlucky interleaving** — a split read-modify-write drops updates even if most runs look fine.
- **A lock guards a critical section** — hold it only around the shared data, and release it before slow work.
- **Deadlock needs a cycle** — mutual exclusion, hold-and-wait, no preemption, and circular wait. Break the cycle.
- **Order the locks** — one global order, including an identity order when the set of locks is dynamic.
- **Wait on a condition, do not spin** — sleep without holding the lock, and re-check the condition after waking.
- **Describe the shared state first** — fields, the lock that guards them, the critical section, then the wait policy.

## Example

```text
Shared:  balance, guarded by account_lock

deposit(amount):
  acquire account_lock
  balance = balance + amount
  release account_lock

transfer(src, dst, amount), with locks ordered by account id:
  acquire the lower id, then the higher id
  if src.balance < amount: release both and fail
  src.balance -= amount
  dst.balance += amount
  release both
```

The transfer sketch is the outline of a lock-ordering argument. A later pass should say what happens if the two accounts are the same object, and how a waiting withdrawal sleeps on a condition instead of holding `account_lock` while it blocks.
