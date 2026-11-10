## CAP Theorem

A partition stops some nodes from receiving messages from the others. A request that arrives during the split can keep the copies from diverging, or it can return whatever the reachable copy holds. The missing messages leave that request unable to do both.

Partition tolerance stays assumed, because the split belongs to the network. A CA label describes a deployment that is only offered while the network stays whole. During a split the live choice is CP or AP. CP refuses the request that would let the two sides accept different values for the same key. AP answers from the reachable copy, and that answer can be older than a write the other side already acknowledged. A product is rarely one label for every key. The same store can refuse a second claim on a shelf label and still answer the lobby board. The choice on a day with no split is PACELC.

```text
during a split
  CP   refuse, so the sides keep a single value
  AP   answer from the copy still reachable
CA     a label that assumes the network never splits
```

## PACELC Theorem

PACELC separates the rare case from the request you serve every day. If a partition is underway, choose availability or consistency. Else, with every replica reachable, choose latency or consistency.

A lobby count that returns from one local replica is PA/EL. During a split it still answers, and on a healthy day it answers without waiting for the other copies. A shelf label that waits until one claim is the winner is PC/EC. The wait is part of the healthy path, and during a split the side that cannot finish the order refuses. Partitions are uncommon. The latency-or-consistency choice is on every read and write, and it can differ by operation. A single CP or AP sticker leaves that everyday choice off the diagram.

```text
PA/EL   one local copy answers
PC/EC   the operation waits until the required copies agree
```

## Replication Topologies

The topology says which node may accept a write and how the other copies learn it.

Single-leader replication has one node accept writes and ship its log to followers. Synchronous shipping waits for a follower before the acknowledgement. Asynchronous shipping acknowledges from the leader's own commit, and followers apply later. The relational form of that log, including promotion and fencing, is Database Replication and Failover and Promotion in [Databases Relational](../06_Databases_Relational/).

Multi-leader replication lets more than one node accept writes, often one leader in each site. Each leader ships its log to the others, synchronously or asynchronously. Two leaders can accept different values for one key, and those values meet under Conflict Resolution. A second site, including a site that goes dark, is Multi-DC and Geo Routing in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

Leaderless replication lets any replica accept the write. A coordinator waits for W of N acknowledgements, and replicas past W catch up after the client has been told. A read asks R replicas. The copies of one key sit on successive nodes of the hash ring. The walk that finds those nodes is Consistent Hashing in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/).

```text
single-leader    one writer; sync waits, async acks at the leader
multi-leader     a writer per site; overlapping keys can diverge
leaderless       any replica accepts; W and R set the wait
```

## Strong Consistency

Strong consistency means an acknowledged write to a key is what a later read of that key returns, whoever asks. The copies those reads are allowed to use already hold the write, or the serving node withholds an older copy. A desk that opens a shelf card after the save was acknowledged sees the new clay body.

The guarantee is about that key and about writes that have already finished. Two writes that overlap still need a rule for which value is newer. A real-time total order, the kind a lock or a single winner needs, is Linearizability. Read-after-write is the same visibility limited to the writer's own session. The cost is the wait on the acknowledgement: it includes the replicas the later read will trust. A silent replica can hold that wait open. One primary shipping its log synchronously is the single-leader form, in Database Replication in [Databases Relational](../06_Databases_Relational/). A quorum whose read set meets the write set is the leaderless form, in Quorum Reads and Writes.

```text
ack, then a later read of that key    returns that write
the writer's own next read            read-after-write
a lock or a single winner             linearizable
```

## Eventual Consistency

Eventual consistency means that once writes to a key stop, every replica of that key arrives at the same value. Before that, a read can return an older copy. The lobby board "pots fired today" can trail the kiln by a short gap, and the board still answers from a nearby replica.

The gap is often small. The model itself gives it no deadline. A stuck replica, a backlog, or a partition stretches it. This is the availability side of a split and the latency side of an ordinary request. A kiln slot, a balance, or a lock belongs on a stronger card.

```text
writes stop, then the replicas match
until then a read can be older
the gap has no promised bound
```

## Read-After-Write Consistency

Read-after-write consistency is a session guarantee. The writer sees their own write on the next read in that session. Other sessions can still see the older value. A member who changes the display name on a shelf and reloads the page sees the new name. The lobby board can keep the previous name for a while.

A monotonic read is the companion guarantee. A later read in the same session stays at least as new as a version that session has already observed. With read-after-write alone, the reload can show the new name and a following read can land on a replica that still has the old one, so the name moves backward. A monotonic read keeps the session on a copy that has caught up to what the session already saw. Placing that read on a relational primary, or waiting until a replica applies, is Read Replicas in [Databases Relational](../06_Databases_Relational/).

```text
read-after-write    this session's next read sees this session's write
monotonic read      a later read in the session stays at least that new
other sessions      can still see the older value
```

## Linearizability

Linearizability places each operation at a single instant between its invocation and its response, in an order that respects real time. When a write completes before a read begins, the read sees the write. Every client observes that same order of instants. Clients share one timeline for those operations, while several replicas still hold the bytes.

That order is what a lock, a leader lease, or a shelf label claimed by only one pot requires. Two racing claims have one winner, and a client that arrives after the winner finished sees the winner. A page the writer just saved is read-after-write. A lobby count is eventual. Per-key quorum freshness, on Quorum Reads and Writes, makes an acknowledged write visible to a later read of that key. The real-time order across racing clients is the extra property here. During a partition, the side that cannot complete the order refuses the operation. etcd and ZooKeeper are stores that offer this order to callers. Raft and Paxos are the protocols that produce it, and their steps are Consensus Algorithms in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/).

```text
one shelf label, one pot       linearizable
the member reloads their card  read-after-write
pots fired today               eventual
```

## Quorum Reads and Writes

N replicas hold a key. A write waits until W of them acknowledge. A read waits until R of them respond, and the caller keeps the newest version among those responses. When W + R > N, every such read set shares a replica with every such write set, so one of the responses carries the latest acknowledged write.

W = 1 and R = 1 can miss: the read can land on replicas that missed the write. W = N forces every replica to take the write, so a later read can ask any one of them, and a single silent replica stalls the write. The overlap is a count of acknowledgements. The coordinator that collects them is the Read and Write Path. A sloppy quorum counts a stand-in when a preferred replica is silent. The hint on that stand-in is Replica Failure Handling. Which version counts as newest, when two writes carry different histories, is Conflict Resolution.

```text
N=3, W=2, R=2    the sets share a replica; one replica may be silent
N=3, W=1, R=1    the sets can miss; a read can miss the write
N=3, W=3, R=1    every replica took the write
a write still completes with up to N - W replicas silent
```

## Conflict Resolution

Concurrent writes leave two values for one key when neither writer observed the other. The replicas still have to settle.

Last-write-wins keeps the value with the greater timestamp and drops the other. A wall-clock timestamp is a weak input to that comparison. Clocks drift and step, so the greater stamp can belong to the write a person made earlier. Unreliable Clocks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) is that clock.

A version vector, also called a vector clock, counts updates per replica. A vector that is greater or equal in every component, and greater in one, happened after the other and replaces it. When each vector is greater in some component, the writes are concurrent, and both versions stay until something merges them. The application merge uses the type: defect tags on a pot become the union of the two sets, while a single glaze sentence needs a person to pick. A CRDT is a type that already contains its merge, so replicas converge with no coordinator choosing a winner. Last-write-wins stays the short default, and the value it drops is gone.

```text
LWW              the greater timestamp stays
version vector   "after" replaces; concurrent writes both stay
app merge        the type combines them, or a person picks
CRDT             the merge is part of the type
```

## Read and Write Path

The coordinator is the node a client contacts for a key in a leaderless cluster. It can be one of the replicas, or a node that forwards.

On the write path the coordinator sends the put to the N replicas. It tells the client the write succeeded once W acknowledgements are in. Replicas that stayed silent can still hold an older value. When the acknowledgements stop at W - 1, the client is told the write failed. A replica may already have stored the put. The client treats that attempt as a failure and retries with a version, so a later winner is explicit.

On the read path the coordinator asks R replicas and returns the newest version in the answers. If one answer is older, the coordinator can write the newest value back to that replica. That write-back is read repair. It updates replicas this read touched. Ranges nobody read, and a replica that was gone for a long time, are Replica Failure Handling.

```text
write     send to N, succeed after W acks, fail at W - 1
read      ask R, return the newest version
repair    write that version onto an older answer
```

## Replica Failure Handling

The coordinator stops waiting on a replica that has missed its deadline. A missed heartbeat, or a gossip round with no answer, is enough to leave that replica out of this attempt. Partial Failures and Split Brain in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) describe how a slow link imitates a dead node, and how two sides can both act as leader. Fencing the old relational primary is Failover and Promotion in [Databases Relational](../06_Databases_Relational/).

A short outage uses hinted handoff. The coordinator writes the value to a stand-in and stores a hint that names the preferred replica. A quorum that counted the stand-in is a sloppy quorum. When the preferred replica returns, the stand-in forwards the hint and the replica applies the write. Until that forward finishes, a read that asks only the preferred replicas can miss the value, because the stand-in was what made W.

A replica that will stay gone is repaired by anti-entropy. Replicas compare in the background and copy the keys that differ. A Merkle tree hashes each range of keys, then hashes those hashes up to a root. The replicas exchange roots. A matching hash means that whole branch agrees, so the range stays as it is. A hash that differs is opened, down to a leaf. The leaf is one range whose keys get compared and copied. The leaf hash names the range, and the keys inside it are what the exchange resolves. A whole site going dark is a separate case: another region must already hold a copy, which is Multi-DC and Geo Routing in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

```text
detect       a missed heartbeat or gossip round ends the wait
temporary    hint on a stand-in, forwarded when the replica returns
permanent    Merkle tree, then copy the ranges whose hashes differ
```
