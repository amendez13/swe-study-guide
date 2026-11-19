## Transaction

A transaction is a set of reads and writes that the database applies as one unit. Commit keeps every write in the set, and rollback removes every write in it. A transfer moves $400 from checking to savings. Checking starts at $800 and savings at $0, so the transfer is two writes: checking becomes $400 and savings becomes $400. Those two balances are one fact. With nothing tying the writes together, a crash after the debit and before the credit leaves checking at $400 and savings at $0. The $400 is in neither account, and a later read treats that as the truth.

Inside a transaction, the debit and the credit are followed by a commit, and commit returns only after this node's log has a commit record. Both new balances are then what a later read sees, even after a crash and restart, because recovery replays the log. A rollback leaves checking at $800 and savings at $0. A crash before commit ends the same way, because recovery undoes the debit that never committed.

The promise is about this node's log. A commit that never reached another node can still disappear if this node is discarded, which is Failover and Promotion in [Databases Relational](../06_Databases_Relational/). The four letters around the unit are ACID Properties in the same topic. The C there means declared constraints still hold after commit, such as checking staying at or above $0. The C in CAP is a different word, about replicas. In an interview, walk the two balances through commit, rollback, and a crash between the writes. When both rows live in one database, the answer is a local transaction. When the debit and credit are two services, use two-phase commit or a saga.

```text
commit              checking $400, savings $400
rollback            checking $800, savings $0
crash, no txn       checking $400, savings $0, the $400 is lost
crash before commit recovery undoes the debit
```

![Transaction](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-1-transaction.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 1.*

## Isolation Levels

Isolation is how much one transaction may see of another's work on the same database. The levels differ by which anomalies they still allow. Name the anomaly the requirement forbids, then pick the cheapest level that forbids it.

Read committed hides uncommitted rows, and it is PostgreSQL's default. Each statement sees what was committed before it started. A transfer reads checking at $800, another transaction debits $400 and commits, and the next read returns $400. That is a non-repeatable read. A count of on-call doctors can also grow between two counts because a new matching row committed, and that row is a phantom. Read committed also loses updates when the application does the arithmetic. The stock is 8, two checkouts each read 8 and write 7, and two units are gone while the stock says 7. `UPDATE inventory SET qty = qty - 1` keeps the subtraction on the row, so the second update waits for the lock and the stock ends at 6.

Snapshot isolation gives the transaction one snapshot from its first statement, so checking stays $800. PostgreSQL's repeatable read is this snapshot, and a second update of the same row fails and retries. Write skew still gets through. Alex and Blake are on call, and the rule is that at least one doctor stays on. Each transaction counts 2 and takes its own doctor off. The updates hit different rows, both commit, and the count is 0. Serializable requires the outcome to match some serial order. PostgreSQL detects this pair and aborts one, and the retry reads 1 and keeps that doctor on. Serializable aborts more under contention. Cheaper checks often do the job. A unique key rejects a second reservation for seat 14, and `SELECT ... FOR UPDATE` on the on-call rows makes the second doctor wait. InnoDB's default is repeatable read, covered in ACID Properties in [Databases Relational](../06_Databases_Relational/). Replica reads and real-time order are Strong Consistency and Linearizability in [Consistency and Replication](../09_Consistency_and_Replication/).

```text
read committed   sees new commits, phantoms, lost read-then-write updates
snapshot         stable reads, write skew across rows
serializable     aborts one of the pair, the application retries
cheaper          unique key, or SELECT ... FOR UPDATE
```

![Isolation Levels](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-2-isolation-levels.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 2.*

## Optimistic or Pessimistic

Pessimistic control locks the row and then does the work. Optimistic control does the work and then checks a version at commit. Two buyers can both try to reserve the last unit. One has to be refused, and the stock has to end at 0 with a single reservation. The choice is whether the loser waits up front or finds out at commit, and contention decides it.

A flash sale has one unit of `sku-14` and 40 buyers, so a conflict is the common case. The buyer runs `SELECT qty FROM inventory WHERE sku = 'sku-14' FOR UPDATE`, sees 1, decrements it, inserts the reservation, and commits. The next buyer waits on the lock, then sees 0. The lock has to be on the reservation path, because a plain read that does not take it still sees the last committed quantity.

Ordinary catalog traffic spreads buyers across SKUs, so conflicts are rare. The buyer reads version 7, does the checkout, and claims the row only if the version has not moved:

```sql
UPDATE inventory
SET qty = qty - 1, version = 8
WHERE sku = 'sku-14' AND version = 7;
```

One row updated means this buyer got the unit. Zero rows means another buyer committed first, so this checkout retries from the read or reports the unit gone. In the flash sale, a version check would throw away most of the 40 checkouts. In the catalog, a lock held across a slow checkout makes unrelated buyers wait. The lock costs a wait, plus a deadlock when two transactions lock rows in opposite orders, which is Two-Phase Locking. The version check costs a retry.

```text
common conflict   lock first, the others wait
rare conflict     check the version at commit
1 row updated     this buyer won
0 rows updated    the version moved, retry
```

![Optimistic or Pessimistic](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-3-optimistic-or-pessimistic.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 3.*

## Two-Phase Locking

Two-phase locking is a lock protocol a database can use to make transactions serializable. In the growing phase a transaction acquires locks and releases none. In the shrinking phase it releases locks and acquires none. Taking and releasing locks in any order does not by itself produce a serial order, and these two phases are what produce it. Releasing a write lock before commit would let another transaction read a value that might still roll back, so engines hold locks until commit or rollback. That form is strict two-phase locking.

A shared lock is enough to read a row, and many transactions can hold one. An exclusive lock is needed to write, and it conflicts with both. A deadlock is a cycle in the wait-for graph. Transfer 1 locks account A and waits for account B, while transfer 2 locks B and waits for A. A lock timeout aborts whichever waited too long, and it retries. Deadlock detection walks the graph, finds the cycle, and aborts one side. A fixed lock order prevents the cycle: every transfer locks the lower account id first, so the second transfer waits on A while the first holds it.

Holding locks until commit is why this path allows less concurrency than a snapshot, because readers and writers queue for the whole unit of work. Snapshot isolation lets them overlap and leaves write skew possible, as the Isolation Levels card shows. Two-phase locking orders locks inside one database. Two-phase commit, the next card, is one commit decision across databases. Say which one you mean.

```text
growing     acquire, release nothing
shrinking   release at commit or rollback, acquire nothing
deadlock    1 holds A wants B, 2 holds B wants A
fixes       timeout, detect and abort, lock lower id first
```

![Two-Phase Locking](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-4-two-phase-locking.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 4.*

## Two-Phase Commit

Two-phase commit, 2PC, is one commit decision for two or more databases. An order row in the order database and a charge row in the payment database should agree, because a local commit in only one leaves an order with no charge or a charge with no order. A coordinator sends prepare to both. A participant that can commit records that promise in its own log, votes yes, and keeps its locks. One that cannot votes no. If every vote is yes, the coordinator records commit and sends it, and each participant commits and releases its locks. If any vote is no, the coordinator sends abort.

The wait is the cost. A coordinator that dies after both yes votes and before the decision leaves each participant stuck. It has promised to follow a decision it has not heard, guessing could disagree with the other participant, and its locked rows stay unavailable until the coordinator returns. Three-phase commit adds a pre-commit round so a participant can finish on a timeout. That only stays correct if a missing coordinator has truly crashed, a partition can split the decision, and production systems almost never run it.

That blocking is a poor fit for an order service and a payment service that must keep answering. Across services, each commits locally, and a failed charge is repaired by a compensating write that cancels the order. The order can show as pending and then cancelled, because no lock spans both databases. That is the Saga Pattern in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/), and a retried charge uses Idempotency in Payments in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/). Saving the order and an outbox row in one local commit, then publishing, is the Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
all yes            commit, locks released
any no             abort
coordinator dies   participants wait, locks held
two services       local commits plus compensation, a saga
save then publish  Transactional Outbox
```

![Two-Phase Commit](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-5-two-phase-commit.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 5.*

## Consensus Algorithms

Consensus is how a group of nodes agrees on the next entry in a replicated log when some of them have stopped or cannot be reached. One node that records "order 19 is paid" loses that fact when it dies. Two nodes that each record it independently can record different facts. The log needs a single next entry that survives a minority of nodes being down. Raft is the algorithm to name for that log.

Raft picks one leader. The leader appends "order 19 is paid" locally and sends it to the followers, and each follower stores it and acknowledges. The entry is committed once a majority has stored it, and then the leader applies it and tells the followers they may too. With 3 nodes the majority is 2, so the group survives 1 failure. With 5 nodes the majority is 3, and it survives 2. A fourth node still needs 3 acknowledgements and still survives only 1, so the useful sizes are odd. Paxos agrees on a value as well. Raft is the name to give because its leader, term, and majority acknowledgement are pieces you can walk through.

A majority write waits for the slowest acknowledgement it needs, and a cluster that cannot gather a majority refuses the entry. In a design, call a store that already runs this protocol: etcd runs Raft, and ZooKeeper runs Zab. The order a caller observes is Linearizability, and overlapping read and write sets are Quorum Reads and Writes, both in [Consistency and Replication](../09_Consistency_and_Replication/). Two sides both writing after a cut is Split Brain in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). Choosing the writer is Leader Election, and a timed key in the same store is Distributed Locks.

```text
3 nodes   majority 2, survives 1 failure
4 nodes   majority 3, still survives 1
5 nodes   majority 3, survives 2
stores    etcd (Raft), ZooKeeper (Zab)
```

![Consensus Algorithms](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-6-consensus-algorithms.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 6.*

## Leader Election

Leader election picks the one node allowed to accept new entries in the log, and the other nodes replicate what it commits. Two leaders that both commit produce two logs. A client can be told both writes succeeded while the entries disagree. A majority vote keeps a single leader in each term.

In Raft, a candidate increments the term and asks for votes. A node votes once per term, and only for a candidate whose log is at least as new as its own. The candidate with a majority becomes leader. Take three nodes, and a cut that leaves A alone with B and C together. A holds 1 vote of 3, so it cannot win, and since a commit needs a majority acknowledgement it cannot commit either. A client that reaches only A gets no successful commit. Anything A appended but did not commit is dropped when it rejoins and follows the pair's log at the higher term. B and C hold 2 of 3, so they may elect a leader and keep committing.

The lone node can still be up and answering, and the safe answer is to refuse the write. That is a short outage for clients who can only reach it. Letting it commit avoids the outage and forks the log, which is Split Brain in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). The majority that commits an entry is Consensus Algorithms. A relational primary that keeps accepting commits after another node is promoted has to be fenced, which is Failover and Promotion in [Databases Relational](../06_Databases_Relational/). In an interview, draw the cut and count each side.

```text
vote        once per term, for a log at least as new
1 of 3      cannot elect, cannot commit
2 of 3      may elect and keep committing
both commit the log forks, split brain
```

![Leader Election](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-7-leader-election.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 7.*

## Distributed Locks

A distributed lock is a lease on a key in a consensus store. The holder may do the work while the lease is valid, and when it expires another worker may take the key. Two workers should not both run the nightly billing job, and a lock inside one process does not stop the other process. The store agrees on the key the way Consensus Algorithms agrees on a log entry. The lease adds an expiry, so the winner's right ends when it stops renewing.

The key is `locks/nightly-billing`, with a 10-second lease in etcd or ZooKeeper. The holder renews it while running the job. Then the holder pauses for 14 seconds, for example in a long garbage-collection pause, and misses the renewal. At 10 seconds the lease ends, and a second worker takes the key and starts the job. At 14 seconds the first worker resumes, still believing it holds the lock. If its writes count, both workers have billed the same accounts. Checking the lease just before writing does not help, because the pause can come right after the check.

The fix is a storage token that increases with every grant: 1 for the first holder, 2 for the next. The billing store rejects any write whose token is older than the highest it has accepted, so token 1 is refused after token 2. The check happens on the write itself. A short lease spots a dead holder fast and costs more renewals. A long one delays takeover, so size it from how long the job may pause. When every worker shares one database, a row lock or advisory lock ending with the transaction is enough. A relational primary is fenced the same way, in Failover and Promotion in [Databases Relational](../06_Databases_Relational/).

```text
lease      10 s on locks/nightly-billing, renewed while working
pause      14 s, the lease expires, a second worker takes over
resumed    the first worker still thinks it holds the lock
token      the store rejects token 1 after accepting token 2
```

![Distributed Locks](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions-8-distributed-locks.png)

*Source: [`diagrams/transactions.drawio`](/content/09_System_Design_Interview/16_Transactions_and_Concurrency_Control/diagrams/transactions.drawio), page 8.*
