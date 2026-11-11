## Partial Failures

A partial failure is one part of a distributed system going silent while the rest keeps running. In a three-replica database, replica A can stop answering while B and C still serve requests. One process fails as a whole. A cluster fails in pieces, and the pieces that remain are still the system. They have to keep answering while one member is missing, and the caller has to decide what a silence means.

The client sends a read to replica A at t = 0 and waits up to 200 ms. No bytes come back. From the client, three causes look the same: A crashed, A is slow and would answer after the deadline, or the network path to A is cut. The attempt stops at 200 ms and leaves the cause unnamed, because silence carries no reason. An operation that needs two acknowledgements out of three can still finish on B and C. A call that needed A itself ends here, and the caller tries another replica or returns an error.

A longer wait gives a slow replica time to answer and holds the caller's thread the whole time. A shorter wait frees the thread and abandons a replica that was only slow. Pulling a node after one miss shifts traffic onto the survivors and can overload them. Leaving it in means later calls can hit the same silence. Each of those later decisions has an owner. Pool membership is Health Checks in [Load Balancing](../04_Load_Balancing/). Leaving a replica out and repairing it is Replica Failure Handling in [Consistency and Replication](../09_Consistency_and_Replication/). Switching to a spare or a second site is Failover Strategies and Multi-DC and Geo Routing in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

```text
silence at 200 ms   crashed, slow, or cut, the caller cannot tell
this attempt        stops and leaves the cause open
2 of 3 acks         the write still finishes on B and C
what comes next     health checks, replica repair, failover
```

![Partial Failures](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-1-partial-failures.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 1.*

## Unreliable Networks

The path between a payment service and the card processor can lose a message, delay it, deliver it twice, or deliver a later message first. Those four outcomes are ordinary network behavior. The confirmation is the service's only evidence that a charge went through, and the service still has to end with exactly one charge.

A lost confirmation for payment 12 looks exactly like a delay that has not ended, or a processor that stopped, so a timeout leaves the cause open. A delayed confirmation arrives after the service has moved on, having already returned an error or sent the charge again, and it has to attach to the original charge. A duplicated request or confirmation must leave the first charge as it was. In a reorder, update 12 was sent first and update 18 second, but 18 arrives first. A receiver that keeps whichever update arrives last ends up with 12, the older one, because send order and arrival order are different facts.

One TCP connection delivers its own bytes in order and retransmits lost segments. Two charges on two connections can still finish out of order, and a retry above TCP can apply the same charge twice when it was the first confirmation that got lost. UDP hands all four modes to the application. A sequence number lets the receiver notice that 18 jumped ahead of 12. An idempotency key makes a repeated charge return the first result, which is Idempotency in [Networking and Communication](../10_Networking_and_Communication/). In an interview, name the four modes, then say what absorbs each: a deadline for loss and delay, a key for duplicates, and the receiver's own order for reordering. The deadline and retry gaps are Timeouts and Retries.

```text
lost         silence until the deadline, the cause stays open
delayed      arrives late, attaches to the original charge
duplicated   one charge, one result, via an idempotency key
reordered    18 before 12, the receiver needs its own order
```

![Unreliable Networks](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-2-unreliable-networks.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 2.*

## Timeouts and Retries

A timeout is the caller's decision to stop waiting, and a retry is a later attempt. The gap between attempts, the spread that keeps them off one instant, and the cap on how many attempts may be retries are part of the same decision. The card processor does not announce a crash, so the payment service only sees time pass. With no deadline, one dead call holds every thread queued behind it. With no gap and no cap, the retries become the next outage.

Healthy processor calls answer in 40 to 90 ms. A 30 ms deadline sits under that band, so every healthy answer looks like a failure and traffic moves off a processor that was fine. A 200 ms deadline sits above it: on-time answers stay, and a processor that is gone is abandoned at 200 ms, which is also the earliest this call can fail over. A 30 second deadline treats a crashed processor as still working, and every thread and the queue behind it wait. After a miss, the gap doubles, 1 s, then 2 s, then 4 s, up to a cap, so a short blip is retried soon and a long outage less often. Jitter spreads that gap, so six clients that failed together do not send on the same second and keep the processor down. A retry budget caps retries per window. With 10 retries allowed in a window of 100 charges, the 11th failure returns to its caller untried.

Retry only when a second call leaves the first charge as it was, which is Idempotency in [Networking and Communication](../10_Networking_and_Communication/). After N failed tries, a queued charge moves to the Dead Letter Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). A short deadline catches a dead processor sooner and marks a slow one dead. Retries and hedged calls shorten the tail and multiply load on a processor that is already failing, and the budget is the brake on both.

```text
30 ms      under the 40-90 ms band, a live processor looks dead
200 ms     above the band, a gone processor is noticed at 200 ms
30 s       a crashed call holds the queue
backoff    1 s, 2 s, 4 s, capped, plus jitter
budget     10 retries per 100 charges, then fail fast
```

![Timeouts and Retries](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-3-timeouts-and-retries.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 3.*

## Unreliable Clocks

A wall clock is the time of day a machine would show a person. It drifts, and a time-sync correction can step it forward or backward. A monotonic clock is a counter on one machine that only moves forward, and it measures a duration on that machine. Last-write-wins needs an order between two replicas, and keeping the greater wall-clock stamp looks like one. But each stamp comes from a different clock, so the greater stamp can belong to the earlier write.

Two replicas stamp a write to the same row, in milliseconds. Replica A writes value 4 at wall time 1300. In real time that was 1000, so A's clock ran 300 ms ahead. Replica B writes value 7 at wall time 1100. In real time that was 1180, so B ran 80 ms behind. Last-write-wins keeps 1300, so value 4 stays, even though value 7 happened later. A correction that steps a clock backward makes it worse, because a write after the step gets a smaller stamp than one before it.

A monotonic clock times a local call correctly: read it at the start and at the end, then subtract. Readings from two machines share no origin. A's counter at 4.2 s and B's at 90 ms only say B booted more recently, and they say nothing about which write came first. There are other ways to order writes. One leader can order them as it accepts them, which moves the problem to electing that leader. A logical clock or version vector follows which write saw which, and that is Conflict Resolution in [Consistency and Replication](../09_Consistency_and_Replication/). A clock that reports an error bound lets a commit wait the bound out, and that wait is the cost.

```text
A   wall 1300, real 1000, value 4, kept by last-write-wins
B   wall 1100, real 1180, value 7, the later write, lost
monotonic   durations on one host, never order across hosts
```

![Unreliable Clocks](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-4-unreliable-clocks.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 4.*

## Byzantine Faults

A crash-stop fault is a node that follows the protocol until it stops answering. A Byzantine fault is a participant that can contradict itself: it tells one peer one thing and another peer something else, or it reports a value it did not compute. The recovery you design follows the fault you assume. An etcd or ZooKeeper ensemble you operate is built for nodes that work or stop. A voter you do not operate can send two claims, and so can a node whose state a bug has corrupted, because it is no longer running the protocol you deployed.

Three ensemble nodes you run either answer by the protocol or stop. One stopped node leaves two that still agree, so tolerating one crash takes three nodes, and in general f crashes take 2f + 1. An untrusted client can tell node A that a booking is seat 4 and tell node B it is seat 7, with both messages well formed. Crash-stop has no place for that. Tolerating f Byzantine faults takes 3f + 1 nodes, so one liar needs four, and a different protocol that stays outside this catalog.

Assuming crash-stop keeps the design on a majority of the nodes you run, which is the family etcd (Raft) and ZooKeeper (Zab) use. A node that restarts and rejoins with its own log is crash-recovery, still in that family. Checksums catch many bit flips before they become a second history, but a peer that deliberately sends two well-formed claims passes a checksum. For a bug in code you ship, fix it, watch the process, and keep the crash-stop assumption. In an interview, say it in one sentence: the nodes we operate follow the protocol or they stop. When the voters are untrusted peers, say the assumption no longer holds.

```text
crash-stop   works or stops, f faults need 2f + 1 nodes
Byzantine    can send two claims, f faults need 3f + 1 nodes
your cluster crash-stop, Raft or Zab
untrusted    Byzantine, out of scope here
```

![Byzantine Faults](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-5-byzantine-faults.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 5.*

## Split Brain

Split brain is a network cut after which both sides accept writes. One booking then has two histories, and each side keeps its own. A cut can leave a three-node ensemble, the shape of etcd or ZooKeeper, as node A alone and nodes B and C together. If both sides elect a leader and take writes, the booking diverges. The rule that prevents it is small: only a side that still holds a majority of the whole ensemble may take writes.

Majority is counted against all three configured nodes, including the ones a side cannot reach. A side may continue when `side * 2 > nodes`. Two continues, because 4 > 3. One stops, because 2 is not greater than 3. A lone node can reach every node it sees and is still a minority. The pair may elect a leader and keep writing. The single node refuses writes even when clients can still reach it. If it kept accepting them, booking 12 could be seat 4 there and seat 7 on the pair. Those two books are the split brain.

Requiring a majority keeps one history, and the minority is unavailable for the length of the cut. An ensemble of four can split two and two, and then neither side passes `side * 2 > 4`, so both stop. That is why ensembles are usually 3 or 5. A leader that should have stopped but kept writing needs a fence, such as a lease, a storage token, or cutting it off from commits. That is Failover and Promotion in [Databases Relational](../06_Databases_Relational/). With three replicas and a write quorum of two, the lone side cannot collect two acknowledgements, which is Quorum Reads and Writes in [Consistency and Replication](../09_Consistency_and_Replication/). Electing the single leader is Consensus Algorithms in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/).

```text
rule        side * 2 > nodes
2 of 3      may write, 4 > 3
1 of 3      refuses writes, 2 is not > 3
2 and 2     both stop, so use an odd size
both write  booking 12 is seat 4 and seat 7
```

![Split Brain](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-6-split-brain.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 6.*

## Cascading Failures

A cascading failure is one failure that recruits the next. The booking service survives a slow inventory API as long as the slowness stays inside the inventory calls. Shared threads, retries that land on the same second, and callers that keep sending turn that slowness into an outage of the booking service itself.

Inventory calls normally return in 40 to 90 ms. Then the API slows, and the booking service has no deadline on the call. Each booking thread sits on an inventory call, a pool of 8 workers fills with 8 stuck calls, and the next booking finds no free worker. Six clients retry on the same second, and those extra calls spend whatever capacity was left. That pile-up is the retry storm. The status page shares the same pool, so it stops rendering. One slow API has become a blank page.

Cut the chain at each link. A deadline lets a thread stop waiting and return to the pool. A retry budget with jitter, from Timeouts and Retries, keeps the six retries off one second and caps them. A bulkhead gives the status page its own pool. Past a queue cap, shed extra bookings with an immediate rejection. A Circuit Breaker Pattern stops callers from sending to a dependency that is already failing, and the page answers "bookings paused" through Graceful Degradation, both in [High Availability and Reliability](../03_High_Availability_and_Reliability/). Each cut has a cost. A deadline can abandon a call that would have succeeded, so the retry must be safe to send twice. A bulkhead holds idle threads. Shedding is a failed booking for that caller. A breaker keeps blocking for a while after recovery, until a probe gets through.

```text
no deadline     8 threads stuck  ->  deadline
same-second     retry storm      ->  budget + jitter
shared pool     blank page       ->  bulkhead
queue past cap  still accepting  ->  shed
keep sending    to a failing API ->  circuit breaker
blank page                       ->  "bookings paused"
```

![Cascading Failures](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes-7-cascading-failures.png)

*Source: [`diagrams/failure-modes.drawio`](/content/09_System_Design_Interview/15_Distributed_System_Failure_Modes/diagrams/failure-modes.drawio), page 7.*
