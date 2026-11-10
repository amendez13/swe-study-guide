# Consistency and Replication — Drills

Original practice for choosing a consistency model and for counting copies. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a municipal bike-share. Relational lag and promotion stay in Databases Relational. The hash ring stays in Data Partitioning and Consistent Hashing. Store types stay in Databases NoSQL and Specialized. A whole site going dark stays in High Availability and Reliability.

## CAP or PACELC

The link between dock clusters is either cut or healthy. Assign each case to CP, AP, PA/EL, or PC/EC, and say what the rider sees.

```text
1. free-count-split — the link is cut. The kiosk shows how many bikes look free.
2. one-reservation-split — the link is cut. Only one rider may reserve bike b-17.
3. free-count-healthy — the link is up. The map should paint from one local hop.
4. last-bike-healthy — the link is up. Two kiosks race for the last bike at a dock.
```

```python
CASES = ["free-count-split", "one-reservation-split", "free-count-healthy", "last-bike-healthy"]
```

**Answer:** AP, CP, PA/EL, then PC/EC. During the cut the free-count kiosk answers from the local copy, so the rider can see a count the other cluster has already changed. CP returns an error from a kiosk that cannot complete a single order. The rider sees a refusal, and b-17 is reserved on at most one side of the cut. On a healthy day the map still paints from one local replica, and that count can be a moment old: availability during a split, latency the rest of the time. The last bike waits for one winner on a healthy day too. One rider gets it, and the other sees a refusal. That wait is the consistency choice with no partition in progress.

```python
CASES = ["free-count-split", "one-reservation-split", "free-count-healthy", "last-bike-healthy"]
CHOICE = {
    "free-count-split": "AP",
    "one-reservation-split": "CP",
    "free-count-healthy": "PA/EL",
    "last-bike-healthy": "PC/EC",
}

print(" ".join(CHOICE[name] for name in CASES))
# AP CP PA/EL PC/EC
```

## Quorum Overlap

For each `(N, W, R)`, does `W + R > N` hold? How many replicas may stay silent and the write still succeed?

```python
CASES = [(3, 2, 2), (3, 1, 1), (5, 3, 3), (5, 1, 3)]
```

**Answer:** Overlap, then the write's silence budget: `(True, 1)`, `(False, 2)`, `(True, 2)`, `(False, 4)`. The budget is `N - W`. With three replicas, W = 2 and R = 2, one replica may be silent and every read pair still meets the write. W = 1 and R = 1 still accepts a write with two replicas silent, and the one replica you read can be one of those two. Five replicas with W = 3 and R = 3 tolerate two silent replicas and still overlap. W = 1 and R = 3 tolerates four silent replicas on the write, and the three you read can all be replicas that missed it.

```python
CASES = [(3, 2, 2), (3, 1, 1), (5, 3, 3), (5, 1, 3)]


def report(n: int, w: int, r: int) -> tuple[bool, int]:
    return (w + r > n, n - w)


print([report(*case) for case in CASES])
# [(True, 1), (False, 2), (True, 2), (False, 4)]
```

## Stale Replica

A write of version 7 for bike b-17 met W = 2. Replicas A and B store 7. Replica C still stores 6. N is 3. Which newest version does every read of R = 2 return, what does a read of C alone return, and does W + R > N hold for that R?

```python
VERSIONS = {"A": 7, "B": 7, "C": 6}
R = 2
N, W = 3, 2
```

**Answer:** Every pair returns 7 as its newest version. The pairs are A with B, A with C, and B with C. C's 6 is in two of those pairs, and the other replica in the pair has 7, so the read keeps 7. A read of C alone returns 6. That read has R = 1, and W + R is 3, so W + R > N fails. The overlap promise is the one for R = 2. This is the quorum form of seeing the write you waited for. Which replica a relational primary would have you read is Databases Relational.

```python
from itertools import combinations

VERSIONS = {"A": 7, "B": 7, "C": 6}
R = 2
N, W = 3, 2

newest = [max(VERSIONS[name] for name in pair) for pair in combinations(sorted(VERSIONS), R)]
print(newest, VERSIONS["C"], W + R > N)
# [7, 7, 7] 6 True
```

## Model per Feature

Assign each bike-share feature to eventual, read-after-write, strong, or linearizable.

```text
1. map-count — the city map shows free bikes at a dock.
2. display-name — a rider saves a display name and reloads their own page.
3. desk-fee — support opens the charge after the kiosk was told the fee was saved.
4. one-bike — two kiosks submit a claim for bike b-17 at the same moment.
```

```python
FEATURES = ["map-count", "display-name", "desk-fee", "one-bike"]
```

**Answer:** Eventual, read-after-write, strong, then linearizable. The map can show a dock count from a moment ago and still be the right product, because a rider who arrives to an empty dock retries. The rider who just saved a display name has to see that name on the next load of their own page, while another rider can still see the previous one. The support desk is a different client, and its next read of that charge has to return the fee the kiosk was already told had succeeded. Two kiosks racing for b-17 need one winner whose claim lines up with real time, so the kiosk that starts after the winner finished sees the winner.

```python
FEATURES = ["map-count", "display-name", "desk-fee", "one-bike"]
CHOICE = {
    "map-count": "eventual",
    "display-name": "read-after-write",
    "desk-fee": "strong",
    "one-bike": "linearizable",
}

print(" ".join(CHOICE[name] for name in FEATURES))
# eventual read-after-write strong linearizable
```

## Concurrent Writes

Dock A writes the defect "flat" with timestamp 100 and version vector `{A: 1, B: 0}`. Dock B writes "brake" with timestamp 140 and `{A: 0, B: 1}`. What does last-write-wins keep, are the vectors concurrent, and what does a merge of a defect set keep?

```python
A = {"ts": 100, "vec": {"A": 1, "B": 0}, "value": "flat"}
B = {"ts": 140, "vec": {"A": 0, "B": 1}, "value": "brake"}
```

**Answer:** Last-write-wins keeps brake and drops flat, because 140 is the greater stamp. The stamp is a wall clock, so the greater number is weak evidence of which dock wrote later. Neither version vector dominates: each is ahead on its own component, so the writes are concurrent and both stay. A defect set merges to flat and brake. A descendant vector such as `{A: 1, B: 1}` would have replaced `{A: 1, B: 0}`. These two vectors have no such order, so a person, or a CRDT set, does the combine.

```python
A = {"ts": 100, "vec": {"A": 1, "B": 0}, "value": "flat"}
B = {"ts": 140, "vec": {"A": 0, "B": 1}, "value": "brake"}


def dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    keys = set(left) | set(right)
    greater_or_equal = all(left.get(key, 0) >= right.get(key, 0) for key in keys)
    strictly_greater = any(left.get(key, 0) > right.get(key, 0) for key in keys)
    return greater_or_equal and strictly_greater


lww = A["value"] if A["ts"] >= B["ts"] else B["value"]
concurrent = not dominates(A["vec"], B["vec"]) and not dominates(B["vec"], A["vec"])
merged = sorted({A["value"], B["value"]})
print(lww, concurrent, merged)
# brake True ['brake', 'flat']
```

## Hinted Handoff

Preferred replicas for bike b-17 are A, B, and C. C is down for a few minutes. The write is acknowledged by A and by D, a stand-in. Where does the hint sit, which preferred replica does it name, and which preferred replicas hold the write before C returns?

```python
PREFERRED = ("A", "B", "C")
DOWN = "C"
ACKS = ("A", "D")
```

**Answer:** The hint sits on D and names C. Before C returns, A is the only preferred replica that holds the write. D counted toward W, which makes this a sloppy quorum. When C returns, D forwards the hint and C applies it. Until that forward, a strict read of two preferred replicas can be B and C, and both can miss the value that A and D stored. The silence that let the coordinator pick D is a missed heartbeat. A replica that never returns is a Merkle repair, the next card.

```python
PREFERRED = ("A", "B", "C")
DOWN = "C"
ACKS = ("A", "D")
HINT = {"on": "D", "for": DOWN}

preferred_holding = [node for node in ACKS if node in PREFERRED]
print(HINT["on"], HINT["for"], preferred_holding)
# D C ['A']
```

## Merkle Repair

Replica C was gone long enough to miss an unknown set of keys. The key space is 1,000,000 keys, and each Merkle leaf covers 1,000 of them. After the roots differ, three leaves differ. How many leaves are in the tree, and how many keys sit under the leaves you still have to exchange? What does one differing leaf tell you?

```python
KEYS = 1_000_000
LEAF = 1_000
DIFFER = 3
```

**Answer:** The tree has 1,000 leaves, and the three that differ cover 3,000 keys. Those 3,000 are the ones the replicas exchange. A matching hash higher in the tree means that whole branch agrees, so the keys under it stay put. One differing leaf names a range of 1,000 keys. Finding which key inside it changed means comparing that range. Read repair would have fixed only the keys a rider happened to read while C was gone.

```python
KEYS = 1_000_000
LEAF = 1_000
DIFFER = 3

print(KEYS // LEAF, DIFFER * LEAF)
# 1000 3000
```

## Write Path Ack

The coordinator sends one put to replicas A, B, and C. W is 2. In the first attempt, A and B acknowledge and C times out. In the second attempt, only A acknowledges. What is the client told in each attempt?

```python
W = 2
CASES = [("A", "B"), ("A",)]
```

**Answer:** The client is told ok, then fail. Two acknowledgements meet W, so the first put succeeds. C can still hold an older value, and a later read that includes C can write the newer value back. One acknowledgement is W - 1. The client is told the write failed even though A stored the put. A retry sends the put again, with a version, so a racing write has an order. The coordinator is the node that collected the acknowledgements. It can be a replica of the bike, or a node that only forwarded the put.

```python
W = 2
CASES = [("A", "B"), ("A",)]


def verdict(acks: tuple[str, ...], w: int) -> str:
    return "ok" if len(acks) >= w else "fail"


print(" ".join(verdict(acks, W) for acks in CASES))
# ok fail
```
