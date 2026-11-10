## Transaction

A run at Lantern Press writes two rows in the press database. It marks plate P-14 used, and it takes 400 sheets from lot L-3, which held 800. Those two writes are one unit of work. Commit leaves the plate used and the lot at 400. Rollback leaves the plate free and the lot at 800.

A crash after the plate write and before the lot write leaves the plate used and the lot still at 800 when nothing ties the writes together. The sheets are on the press, and the lot still offers them to the next run. The four letters of the unit, including durability on the node that committed, are ACID Properties in [Databases Relational](../06_Databases_Relational/). The C in those letters is a different word from the C in CAP, and that distinction is on the same card.

```text
commit                         plate used, lot 400
rollback                       plate free, lot 800
crash between the two writes   plate used, lot 800
four letters, durability       ACID Properties
```

## Isolation Levels

Isolation is how much two concurrent runs on the press database can see of each other. Read committed hides rows another run has yet to commit, so west never reads east's half-finished lot. A later statement in west's run can still see a commit that landed in between: west reads L-3 at 800, east commits 400, and west's next read returns 400. That second answer is a non-repeatable read. A new row that matches a predicate west already read can show up the same way. West and east can also both read 800, both subtract 100 in application code, and both write 700, so one job's sheets vanish. An `UPDATE` that subtracts inside the database keeps that arithmetic on the row.

Snapshot isolation gives the run one snapshot from its start, so the second read of L-3 stays 800. PostgreSQL's repeatable read is that snapshot. InnoDB starts at repeatable read, and the locking details are ACID Properties in [Databases Relational](../06_Databases_Relational/). Write skew still fits under the snapshot. Lots A and B hold 300 sheets each, and the shop rule keeps their sum at or above 500. West reads the sum at 600 and takes 200 from A. East reads the same snapshot and takes 200 from B. Each wrote a different row, the updates miss each other, and the sum is 200. Serializable treats the two runs as if one finished before the other and aborts one of them. Pay for that when the rule spans rows and each writer updates a different one. A unique key on the plate already stops two runs from taking P-14, and that check is cheaper. These are concurrent transactions on one database. A later read of a replica, and a real-time order across clients, are Strong Consistency and Linearizability in [Consistency and Replication](../09_Consistency_and_Replication/). A lost increment inside a limiter's own counter is [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/).

```text
read committed    no uncommitted row; a later read can change
snapshot          one snapshot; write skew can remain
serializable      one of the skew pair aborts
one database      this card
replicas          Strong Consistency, Linearizability
```

## Optimistic or Pessimistic

Pessimistic control locks the row, then does the work. West takes the plate with a row lock, marks P-14 used, and commits. East waits. The lock fits the night poster, one plate and forty operators, where a conflict is the common case. The wait is the cost. Two runs that lock in opposite orders can deadlock, and that cycle is Two-Phase Locking.

Optimistic control does the work, then checks a version at commit. West read version 7. The update writes version 8 only where the version is still 7. One row changed means west claimed the plate. Zero rows means another operator committed, and west retries the run. The check fits day jobs, where each operator has a different plate and a conflict is rare. A retry throws away the work done since the read. Contention decides which of the two to use.

```text
night poster, one plate      lock first
day jobs, a plate each       check the version at commit
1 row updated                this run claimed the plate
0 rows updated               the version moved; retry
```

## Two-Phase Locking

Two-phase locking is a lock protocol a database can use to make runs serializable. In the growing phase a run acquires locks and releases none: a shared lock to read a lot, an exclusive lock to write it. In the shrinking phase it releases locks, usually all of them at commit or rollback, and it acquires none.

West holds P-14 and waits for L-3. East holds L-3 and waits for P-14. Each is waiting for a lock the other holds. That is a cycle in the wait-for graph. A lock timeout aborts the run that waited too long. Deadlock detection walks the graph, finds the cycle, and aborts one run. The aborted run retries. Taking P-14 before L-3 on every run makes the second run wait on P-14 while the first still holds it, so this cycle does not form. Holding locks until commit is why this path allows less concurrency than a snapshot. It is one way to reach serializable, and the level itself is Isolation Levels.

```text
growing     acquire, release nothing
shrinking   release at commit, acquire nothing
cycle       west holds P-14 and waits for L-3
            east holds L-3 and waits for P-14
break       timeout, or abort one side of the cycle
```

## Two-Phase Commit

Two-phase commit, 2PC, is one commit decision for two databases. The press book and the paper ledger are the participants. A coordinator asks each to prepare. A participant that can commit records that promise and votes yes. When every vote is yes, the coordinator tells them to commit. When any vote is no, it tells them to abort.

A coordinator that dies after both votes are yes, and before it sends the decision, leaves each participant waiting. The participant has promised to follow a decision it has not heard, and the locks it took at prepare stay held until the coordinator returns and finishes. When the press book and the paper ledger belong to two services, each service commits locally and a failed later step is repaired by a compensating write. Those compensations are the Saga Pattern in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). The press row and an outbox row in one local commit, followed by a publish, are the Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Three-phase commit adds a pre-commit round so a participant can time out. Almost nobody runs it.

```text
prepare                        each participant votes yes or no
commit                         every vote was yes
abort                          any vote was no
coordinator dies after yes     participants wait
across services                Saga Pattern
local commit, then a publish   Transactional Outbox
```

## Consensus Algorithms

Consensus is how the west, east, and loft nodes agree on the next entry in the schedule log when one of them has stopped. Raft is the algorithm to name. The leader appends an entry and counts acknowledgements. The entry is committed once a majority has acknowledged it. With 3 nodes that majority is 2, so the group still commits after 1 failure. With 5 nodes the majority is 3, and the group still commits after 2 failures. Paxos agrees on a value too. Raft is the name to give for this log.

Call etcd or ZooKeeper, which already run a majority protocol. etcd runs Raft. ZooKeeper runs Zab. The order a caller of those stores observes is Linearizability in [Consistency and Replication](../09_Consistency_and_Replication/). How many replicas a read set and a write set must share is Quorum Reads and Writes there. This count is the majority on the log. Two nodes that both accept schedule writes after a cut are Split Brain in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). Choosing the one writer is Leader Election. A timed key in the same store is Distributed Locks.

```text
Raft         the name to give
3 nodes      2 acks, survives 1 failure
5 nodes      3 acks, survives 2 failures
call         etcd or ZooKeeper
the order    Linearizability
two writers  Split Brain
```

## Leader Election

One node writes the night schedule. The others follow. A majority of the three coordination nodes has to choose that writer. West, cut off from east and loft, has 1 of 3 and must stop writing. East and loft have 2 of 3 and may elect. A schedule entry from the side of one would diverge from an entry the pair commits.

Both sides writing is Split Brain in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). The majority that commits a log entry is Consensus Algorithms. When the writer is a relational primary that still accepts commits after another node has been promoted, fencing that primary is Failover and Promotion in [Databases Relational](../06_Databases_Relational/).

```text
west alone         1 of 3, stops writing
east and loft      2 of 3, may elect
both sides write   Split Brain
relational primary Failover and Promotion
```

## Distributed Locks

A distributed lock is a lease on a key in a consensus store. Lantern Press puts `press/folio` in etcd. The holder renews a 10-second lease while it prints. Another operator who finds the key absent may take it. The store agrees on that key the way Consensus Algorithms agrees on a log entry. The lease is the part this card adds.

A holder that pauses for 14 seconds misses the renewal. The lease ends, and a new holder may take `press/folio`. The paused process can resume and still act as the holder. An expired holder has to be fenced before its later writes count. When that holder is a relational primary, fencing it so the old node cannot commit is Failover and Promotion in [Databases Relational](../06_Databases_Relational/).

```text
key                  press/folio
lease                10 seconds, renewed while the holder works
paused 14 seconds    a new holder may take the key
expired holder       must be fenced
relational primary   Failover and Promotion
```
