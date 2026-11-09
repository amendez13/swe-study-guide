# Threads and Locks

Threads share a heap and keep private stacks. The bugs are interleavings: a split update, a lock cycle, a missed wakeup, a write another thread never sees. The interview answer names the shared fields, the lock, the wait, and the order. Java's monitor and Python's `Lock` are two syntaxes for that story. The GIL is a limit on CPU-bound Python, not a substitute for your lock.

## Key Points

- **Threads and processes** — a process has its own heap. Threads in one process share the heap and not the stack.
- **Threads in Java** — `start` creates concurrency, `run` does not. `synchronized (obj)` locks that object, not the source line.
- **Race conditions** — a read-modify-write or a check-then-act can lose an update. A green run is not a proof.
- **Locks** — one thread at a time through the section that touches the data. Do not hold the lock across a slow call.
- **Mutex, semaphore, and monitor** — one holder, a count of permits, or a lock plus a wait set. Pick the rule you actually have.
- **Wait and notify** — sleep on a condition, in a loop, while holding the monitor. `wait` releases the lock. Recheck after waking.
- **Producer and consumer** — a bounded queue. Producers wait when it is full, consumers when it is empty. Make the item outside the lock.
- **Reader-writer locks** — many readers or one writer. Do not let a stream of readers starve a writer unless you say so.
- **Atomics and CAS** — one variable, one indivisible step. Not a tool for two fields that must move together.
- **Thread pools** — a fixed set of workers and a bounded queue, plus a rejection policy. Do not wait for the same pool you are running on.
- **Coffman conditions** — exclusion, hold-and-wait, no preemption, and a cycle. All four, or it is not deadlock.
- **Lock ordering** — acquire by a global order, usually by id. A later lock then an earlier one closes a cycle.
- **Livelock and starvation** — retrying in lockstep makes no progress. A thread that is never chosen is starved, not deadlocked.
- **Visibility** — a lock or a `volatile` write publishes values. `volatile` does not make `count++` atomic.
- **The GIL** — one thread runs Python bytecode at a time. I/O overlaps. Your invariants still need a lock.
- **What you say first** — shared fields, the lock, the critical section, the lock order, and what a thread does when it must wait.

## Example

```python
"""A kiln with three permits, and a counter that does not lose increments."""
import threading

kiln = threading.Semaphore(3)
lock = threading.Lock()
done = 0

def fire_one() -> None:
    global done
    with kiln:
        with lock:
            done += 1

threads = [threading.Thread(target=fire_one) for _ in range(6)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
print(done)  # 6. The semaphore caps overlap, the lock protects the counter.
```

Six firings share three permits, so at most three hold the semaphore at once. The counter is a separate critical section. The semaphore does not protect `done`, and the lock does not cap the kiln. Each tool matches one rule.

## More practice

Work the original exercises on the **Drills** tab. They ask which tool applies, where a race or a cycle is, and what the thread should do instead of spinning. The snippets are Python and are deterministic. They do not depend on winning a real race.
