## Partial Failures

**What it is.** A partial failure is one part of a distributed system going silent while the rest keeps running. In a three-replica database, replica A can stop answering and replicas B and C can still serve requests.

**Why it exists.** One process fails as a whole. A cluster fails in pieces, and the pieces that remain are still the system. They have to keep answering while one member is missing, and the caller has to decide what a silence means.

**How it works.**

1. The client sends a read to replica A at t = 0 and waits up to 200 ms.
2. No bytes come back. From the client, three causes look the same: A crashed, A is slow and would have answered after the deadline, or the network path to A is cut.
3. This attempt stops at 200 ms and leaves the cause unnamed. The silence does not carry a reason.
4. An operation that needs two acknowledgements of the three replicas can still finish on B and C. A call that needed A itself ends here, and the caller may try another replica or return an error.

Whether A stays in a load-balancer pool is a repeated probe, Health Checks in [Load Balancing](../04_Load_Balancing/). The heartbeat or gossip round that leaves a replica out of one attempt, and the repair after a short absence or a long one, is Replica Failure Handling in [Consistency and Replication](../09_Consistency_and_Replication/). Switching callers to a spare, and what a whole site going dark requires, is Failover Strategies and Multi-DC and Geo Routing in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

**Trade-offs.** A longer wait gives a slow replica time to answer, and it holds the caller's thread for the whole wait. A shorter wait frees the thread, and it abandons a replica that was only slow. Taking a node out of service after one miss shifts traffic onto the survivors and can overload them. Leaving the node in place means later calls can meet the same silence until a health check or a failover decision says otherwise.

**In an interview.** Say that you assume partial failure. On a timeout, stop this attempt and leave the cause open. Name the neighbor that owns the next decision: health checks for pool membership, replica repair for catch-up, and failover for a spare or a dark site.

**Recap.**

- One replica can be silent while the other two still answer, and the cluster is still a system.
- A missed deadline leaves three causes open: a crash, a slow node, or a cut link.
- This attempt stops waiting. Pool membership, replica repair, and failover are later decisions.

![Partial Failures](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-1-partial-failures.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 1.*

## Unreliable Networks

**What it is.** The path between a payment service and the card processor can lose a message, delay it, deliver a copy twice, or deliver a later message first. Those four outcomes are ordinary network behavior.

**Why it exists.** The payment service has to charge a card across a network. The confirmation is the only evidence that the processor accepted the charge, and that evidence can fail in any of the four ways above. The service still has to end with one charge.

**How it works.** Four things happen to confirmations the processor sends back:

1. Lost. The confirmation for payment 12 never arrives. That silence matches a delay that has not ended yet, and it matches a processor that has stopped. A timeout still leaves the cause open, which is the partial-failure point.
2. Delayed. The confirmation arrives after the service has moved on: it has already returned an error to its caller, or it has already sent the charge again.
3. Duplicated. The same confirmation, or the same charge request, is delivered twice. The second copy has to leave the original charge as it was.
4. Reordered. Update 12 was sent first and update 18 was sent second. Update 18 arrives first. A receiver that stores whichever update arrives last will keep update 12, the older one, once it shows up. Send order and arrival order are different facts.

One TCP connection delivers its own bytes in order and retransmits a segment it treats as lost. Two charges on two connections can still finish out of the order they were sent. A retry above TCP can apply the same charge twice when the first confirmation was the thing that got lost. The handler has to absorb that second attempt.

The deadline, the gap before a retry, and the spread between retries are Timeouts and Retries.

**Trade-offs.** UDP hands loss, delay, duplication, and reorder to the application. TCP hides loss and reorder inside one connection, and the application still sees a timeout, a reset, and its own retry. A sequence number lets the receiver notice that update 18 jumped ahead of update 12. An idempotency key lets a repeated charge return the first result. The key, and the rule that a second call keeps the first outcome, is Idempotency in [Networking and Communication](../10_Networking_and_Communication/).

**In an interview.** Name the four modes, then say which one the design absorbs. A lost or delayed confirmation is why the call has a deadline. A duplicate is why the retried charge carries an idempotency key. Reorder is why arrival order is a poor record of the order the processor applied.

**Recap.**

| What happened on the path | What the payment service sees | What has to hold |
| --- | --- | --- |
| The confirmation was lost | Silence until the deadline | The cause stays open |
| The confirmation was delayed | It arrives after the service has moved on | A late reply attaches to the original charge |
| The same charge arrives twice | A second copy of one request | One charge, one result |
| Update 18 arrives before update 12 | Arrival order differs from send order | The receiver needs its own order |

![Unreliable Networks](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-2-unreliable-networks.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 2.*

## Timeouts and Retries

**What it is.** A timeout is the caller's decision to stop waiting. A retry is a later attempt. The gap between attempts, the spread that keeps those attempts off one instant, and the cap on how many of the attempts may be retries belong to the same decision.

**Why it exists.** The card processor does not announce that it has crashed. The payment service only sees time pass. With no deadline, one crashed call holds every payment thread queued behind it. With no gap and no cap, the retries become the next outage.

**How it works.** Healthy processor calls answer in 40 to 90 ms.

1. A deadline of 30 ms sits under that whole range. Every healthy answer looks like a failure, so the service can move traffic off a processor that was fine.
2. A deadline of 200 ms sits above the healthy range. A processor that answers on time stays in use. A processor that is gone is abandoned at 200 ms, and that is when this caller can try another path. A long deadline is a late failover for this call, because the caller waits out the deadline before it gives up.
3. A deadline of 30 seconds treats a crashed processor as still in progress. Each payment thread waits the full 30 seconds, and the queue behind that call waits with it.
4. After a miss, the gap doubles: wait 1 second, then 2, then 4. A short blip is tried again soon. A long outage is tried less often. Cap the doubling so the gap stays bounded.
5. Jitter adds a spread around that gap. Six payment clients that failed together would otherwise send on the same second and become the load that keeps the processor down.
6. A retry budget caps how many calls in a window may be retries. Past the cap, the client fails the attempt and sends nothing more. In a window of 100 charges, a budget of 10 retries means the 11th failure returns to its caller with no further try. The 10 is an illustration of the cap, chosen for this window.

Send the retry when a second call leaves the first charge as it was. That property is Idempotency in [Networking and Communication](../10_Networking_and_Communication/), and the key itself stays on that card. After N failed tries, a queued charge parks aside and the main queue moves on. That park is the Dead Letter Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). N is chosen there.

```python
HEALTHY_MS = range(40, 91)


def marks_healthy_as_dead(deadline_ms: int) -> bool:
    return deadline_ms < max(HEALTHY_MS)


print(marks_healthy_as_dead(30), marks_healthy_as_dead(200))
# True False
```

**Trade-offs.** A short deadline notices a dead processor sooner and marks a slow one dead. A long deadline keeps the slow one in the attempt and delays failover. Retries give a lost confirmation another chance to complete, and they multiply load on a processor that is already failing. A hedge, a second call sent before the first deadline, shortens the tail and multiplies load in the same way. The budget is the brake. Past the budget, the caller gets a fast failure, and the charge stays unfinished until another path retries it, such as the queue.

**In an interview.** Start from the latency you measured, here 40 to 90 ms. Place the deadline above that band and well under the time a thread can sit, then add capped exponential backoff, jitter, a retry budget, and an idempotency key. Leave the key's storage and the dead-letter count on the cards that own them.

**Recap.**

| Knob | A concrete setting | What it decides |
| --- | --- | --- |
| Deadline of 30 ms | Below the 40–90 ms healthy band | A live processor looks dead |
| Deadline of 200 ms | Above that band | On-time answers stay; a gone processor is noticed at 200 ms |
| Deadline of 30 s | Far above the band | A crashed call holds the queue, and failover waits |
| Backoff of 1 s, 2 s, 4 s | The gap doubles, then stops growing | A short blip is retried soon; a long outage is retried less often |
| Jitter | A spread around the gap | Six clients miss the same second |
| Retry budget | 10 retries in a window of 100 charges | Past the cap, the attempt fails and is not sent again |

![Timeouts and Retries](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-3-timeouts-and-retries.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 3.*

## Unreliable Clocks

**What it is.** A wall clock is the time of day a machine would show a person. It drifts, and a time-sync correction can step it forward or backward. A monotonic clock is a counter on one machine that moves forward, and it measures a duration on that machine.

**Why it exists.** Last-write-wins needs an order between two replicas. Reading each machine's wall clock and keeping the greater stamp looks like that order. Each stamp comes from a different clock, so the greater stamp can belong to the earlier write.

**How it works.** Two replicas each stamp a write to the same row with their own wall clock. The numbers are milliseconds.

1. Replica A writes value 4 at a wall time of 1300. In real time that write happened at 1000, so A's clock was 300 ms ahead.
2. Replica B writes value 7 at a wall time of 1100. In real time that write happened at 1180, so B's clock was 80 ms behind.
3. Last-write-wins keeps the greater stamp. 1300 is greater than 1100, so value 4 stays.
4. Value 7 is the later write in real time, because 1180 comes after 1000. The stamp that won belongs to the earlier write.
5. A later correction can step a wall clock backward. A write that happens after the step then receives a smaller stamp than a write that happened before it.

```python
def last_write_wins(stamps: list[tuple[int, int]]) -> int:
    """Each pair is (wall time ms, value). The greater wall time stays."""
    return max(stamps)[1]


print(last_write_wins([(1300, 4), (1100, 7)]))
# 4
```

A monotonic clock on replica A can time a local call: read it at the start, read it at the end, and subtract. Suppose A's counter reads 4,200,000,000 nanoseconds and B's reads 90,000,000. Those are 4.2 seconds and 90 milliseconds since each machine's own boot. B's smaller reading means B booted more recently. It says nothing about whether value 4 or value 7 was written first. The counters do not share an origin, so subtracting one from the other does not order the writes.

Why a wall-clock stamp is a weak input to that pick, and what a version vector does with concurrent writes, is Conflict Resolution in [Consistency and Replication](../09_Consistency_and_Replication/).

**Trade-offs.** Wall-clock order is a single comparison, and skew can make it keep the earlier write. A leader can order the writes by the order it accepts them, which moves the problem to electing one leader. A logical clock or a version vector follows which write observed which, using the messages among replicas. A clock source that also reports an error bound lets a commit wait until that bound has passed; the wait is the cost. A monotonic clock stays the right tool for "this call on this host took 70 ms."

**In an interview.** Put these two stamps on the board. Say that last-write-wins keeps value 4, and that value 7 happened later in real time. Then say a wall-clock comparison is a weak order across machines. Point at conflict resolution for the merge, or at one leader for a single order.

**Recap.**

| Clock | What the reading means | What it can decide |
| --- | --- | --- |
| Wall clock | Time of day on that machine. A correction can step it. | The greater stamp can be the earlier write: 1300 kept value 4, and value 7 happened later. |
| Monotonic clock | Elapsed time on one machine since its own boot. | A duration on that machine: end minus start. |
| Two monotonic clocks | Two boot origins, here 4.2 s and 90 ms. | The readings share no origin, so the write order stays open. |

![Unreliable Clocks](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-4-unreliable-clocks.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 4.*

## Byzantine Faults

**What it is.** A crash-stop fault is a node that follows the protocol until it stops answering. A Byzantine fault is a participant that can contradict itself: one peer receives one claim, and another peer receives a different claim, or the participant reports a value it did not compute.

**Why it exists.** The recovery you design follows the fault you assume. An etcd or ZooKeeper ensemble you operate is built for nodes that work or stop. A voter you do not operate can send two claims. A bug that corrupts a node's state sits in that second model too, because the node is no longer running the protocol you deployed.

**How it works.**

1. Three ensemble nodes you run each answer according to the protocol, or they stop answering. One stopped node leaves two that still agree. Tolerating one crash in an ensemble of three is a majority of two.
2. An untrusted client can tell node A that a booking is seat 4 and tell node B that the same booking is seat 7. Both messages can be well formed. Crash-stop has no place for that pair of claims.
3. The usual count for f Byzantine faults is 3f + 1 nodes. One liar needs four nodes. The usual count for f crash faults is 2f + 1 nodes. One crash needs three. The extra node is the cost of assuming lies, and the protocol is a different one. That protocol stays outside this catalog.

**Trade-offs.** Stating crash-stop keeps the design on a majority of the nodes you run, which is the family etcd (Raft) and ZooKeeper (Zab) use. A node that later restarts and rejoins with its own log is crash-recovery, still in that non-Byzantine family: it comes back with the one log it had. The sentence you say for the nodes you run stays crash-stop, because they follow the protocol or they stop. Checksums catch many bit flips before they become a second history. A peer that deliberately sends two well-formed claims still passes a checksum. Building the Byzantine protocol on this card would replace the rest of the catalog. For a bug in code you ship, the usual response is to fix and watch the process, and to keep the crash-stop assumption for the nodes you run.

**In an interview.** State the assumption in one sentence: the nodes we operate follow the protocol or they stop. Use that for a database, a service cluster, and an etcd or ZooKeeper leader. When the voters are untrusted peers, say the assumption no longer holds and that the Byzantine protocol is out of scope for this design.

**Recap.**

- Crash-stop fits the ensemble you run: a node works, or it stops. Say that in the interview.
- Byzantine fits an untrusted peer that can present two claims, and a bug that corrupts state.
- One crash fits three nodes. One liar needs four nodes, and that protocol stays outside this catalog.

![Byzantine Faults](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-5-byzantine-faults.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 5.*

## Split Brain

**What it is.** Split brain is a network cut after which both sides accept writes. One booking then has two histories, and each side will keep the history it has.

**Why it exists.** A cut can leave a three-node ensemble as one node alone and two nodes together. If both sides elect a leader and take writes, the booking diverges. The rule that prevents that is small: only a side that still holds a majority of the ensemble may take writes.

**How it works.** Three nodes, the same shape as an etcd or ZooKeeper ensemble.

1. A cut leaves node A alone and leaves nodes B and C together.
2. Majority is counted against all three configured nodes, including the ones this side cannot reach. A side may continue when `side * 2 > nodes`. Two continues, because 4 > 3. One stops, because 2 is not greater than 3. One node is every node it can see, and it is still a minority of the ensemble.
3. The side of two may elect a leader and keep taking writes. The side of one refuses writes, including when clients can still reach it.
4. If that single node keeps accepting writes, booking 12 can be stored as seat 4 there and as seat 7 on the pair. Those two books are the split brain.

```python
def may_take_writes(side: int, nodes: int = 3) -> bool:
    return side * 2 > nodes


print(may_take_writes(1), may_take_writes(2))
# False True
```

A relational primary that still accepts writes after another node has been promoted has to be fenced, so its later commits do not land. That fence is Failover and Promotion in [Databases Relational](../06_Databases_Relational/). A replicated write that must see an overlapping set of copies cannot finish on a side that cannot gather the set. With three replicas and a write quorum of two, the side of one cannot collect two acknowledgements. That overlap is Quorum Reads and Writes in [Consistency and Replication](../09_Consistency_and_Replication/). How the three nodes agree on a single leader is Consensus Algorithms in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/).

**Trade-offs.** Requiring a majority keeps one history, and the minority is unavailable for the length of the cut. Letting either side write keeps both sides available and leaves two histories to merge. An ensemble of four can split into two and two. Neither side satisfies `side * 2 > 4`, so both stop. That is why these ensembles are usually an odd size, 3 or 5. Fencing covers a leader that should have stopped and kept accepting writes: a lease, a storage token, or cutting that node off from commits. The fence itself is the relational failover card.

**In an interview.** Draw the cut of one against two. Say the side of two may write and the side of one must stop, and say what booking 12 looks like if the one keeps writing. Point at fencing for a relational primary, at the quorum overlap for a replicated write, and at consensus for the single leader.

**Recap.**

| Side of a 3-node cut | May it take writes? | What follows |
| --- | --- | --- |
| Two nodes | Yes. Two is a majority of three. | That side may elect a leader and keep one history. |
| One node | No. One is a minority of the ensemble. | That side refuses writes even if clients can reach it. |
| Both sides | This is split brain. | Booking 12 is seat 4 on one side and seat 7 on the other. |

![Split Brain](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-6-split-brain.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 6.*

## Cascading Failures

**What it is.** A cascading failure is one failure that recruits the next. A slow call from a booking service to an inventory API fills a thread pool, the clients retry together, and a status page that shares the pool goes blank.

**Why it exists.** The booking service survives a slow inventory API when the slowness stays inside the inventory calls. Shared threads, retries that land on one second, and callers that keep sending turn that slowness into an outage of the booking service.

**How it works.** Inventory calls normally return in 40 to 90 ms. Then the inventory API slows, and the booking service has no deadline on that call.

1. Each booking thread sits on the inventory call. A pool of 8 workers fills with 8 stuck calls. The next booking finds no free worker.
2. Six clients retry on the same second. Those six extra calls are a new failure, and they spend the capacity the pool had left. That pile-up is the retry storm.
3. The status page uses the same pool, so it stops rendering. One slow inventory API has become a blank page.

Cut the chain at each step:

1. A deadline on the inventory call lets a thread stop waiting and return to the pool.
2. A retry budget and a spread, from Timeouts and Retries, keep the six retries off one second and cap how many run.
3. A bulkhead gives the status page its own pool, so stuck booking calls leave the page's threads free.
4. Past a queue cap, shed the extra booking with an immediate rejection.
5. Callers stop sending to a dependency that is already failing. That stop is the Circuit Breaker Pattern in [High Availability and Reliability](../03_High_Availability_and_Reliability/).
6. The status page answers "bookings paused" where a blank page would have been. That reduced answer is Graceful Degradation in the same topic.

**Trade-offs.** A deadline returns the thread to the pool, and it can abandon an inventory call that would have succeeded a moment later, so a retry of that booking has to be safe to send twice. A bulkhead holds threads for the status page that sit idle while inventory is healthy. Shedding rejects a booking quickly, which is a failed booking for that caller, and it keeps the process accepting the work it can finish. A circuit breaker stops the calls that would have piled up, and it also stops calls during the window after the inventory API has recovered, until the breaker lets a probe through. The paused page tells the caller that bookings are paused, and the live inventory stays hidden until the dependency returns.

**In an interview.** Walk the chain in order: slow call, full pool, retry storm, shared pool, blank page. Name the cut at each link: deadline, retry budget with jitter, bulkhead, shed, breaker, degraded response. The breaker and the reduced answer live in High Availability and Reliability. Design them there.

**Recap.**

| What the slow call recruits | What cuts it |
| --- | --- |
| Booking threads wait with no deadline, and the pool of 8 fills | A deadline, so the thread stops waiting |
| Six clients retry on the same second | A retry budget, plus jitter |
| The status page shares the booking pool | A bulkhead: the page has its own pool |
| The queue is past its cap and still accepts work | Shed the extra booking with an immediate rejection |
| Callers keep sending to the failing inventory API | A circuit breaker |
| The status page goes blank | A degraded answer: "bookings paused" |

![Cascading Failures](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-7-cascading-failures.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 7.*
