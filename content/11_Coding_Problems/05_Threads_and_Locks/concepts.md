## Threads share the heap

Threads in the same process run independently and share the heap. That sharing is the reason to use them and the reason they are dangerous: one thread can read a field while another is halfway through updating it. Stack locals are private. Anything reachable from an object both threads can name is shared, including objects those locals point at.

## A race is an unlucky interleaving

A race condition is a bug that appears only for some orders of steps. The classic shape is a read-modify-write: both threads read `count` as 5, both compute 6, both write 6, and one increment is lost. "It worked when I ran it" is not evidence. The interleaving that loses the update may be rare. Name the shared variable and the steps that must not overlap.

```text
Thread A reads  count = 5
Thread B reads  count = 5
Thread A writes count = 6
Thread B writes count = 6
-- one increment disappeared
```

## A lock guards a critical section

A lock (mutex) lets one thread at a time execute a critical section, the stretch of code that touches the shared state. Acquire the lock, do the whole read-modify-write, release it. Hold the lock only around the shared data. Doing network or disk work while holding it stalls every other thread that needs the same data, and it makes deadlocks easier to build.

## Deadlock needs a cycle

Deadlock is a set of threads each waiting for a lock that another thread in the set holds. You need a cycle in the "waits for" graph, which in practice means threads acquire the same locks in different orders, or a thread acquires a lock and then waits for something that needs that lock. Four conditions are usually listed together: mutual exclusion, hold-and-wait, no preemption, and circular wait. Breaking any one of them prevents deadlock. The one you can usually break in ordinary code is circular wait.

## Order the locks

Pick a global order for the locks and acquire them only in that order. If every thread that needs both the patron lock and the copy lock takes the patron lock first, they cannot wait on each other in a circle. When the set of locks is dynamic, order them by identity (for example by object id) so the order is still global. Releasing in reverse order is the usual pairing. A try-lock with a backoff can also break a cycle, at the cost of a more complicated retry.

## Wait on a condition, do not spin

A thread that needs a state change should wait on a condition variable (or a similar primitive) and release the lock while it sleeps, so the thread that can make the change is able to take the lock. Re-check the condition in a loop after waking: wakeups can be spurious, and another thread may have consumed the event. Spinning in a `while` that rereads a flag burns a core and can still be wrong if the flag is not published safely.

## Describe the shared state first

In an interview, start from the data that is shared, not from the thread API. Say which fields are shared, which lock guards them, what the critical section contains, and the order locks are acquired. Then describe what a thread does when it cannot proceed: wait, fail, or retry. A design you cannot explain at that level is a design you cannot debug.
