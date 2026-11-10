# Microservices and System Decomposition — Drills

Original practice for where a process should split, who owns a row, and what a failed later step undoes. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a ridge-path trail crew. The scale cube and stateless services stay in Scalability Fundamentals. Circuit breakers stay in High Availability and Reliability. Load-balancer algorithms stay in Load Balancing. The API gateway and connection-level state stay in Networking and Communication. The bus, When to Queue, and the transactional outbox stay in Message Queues and Async Processing. Stream processing, change data capture, and event sourcing stay in Storage and Data Processing at Scale. Two-phase commit stays in Transactions and Concurrency Control. Notification products stay in Real-Time and Notification Systems. Payment products stay in Payment and Financial Systems. Logs and request ids stay in Observability.

## Monolith or Microservices

Six maintainers ship the ridge-path desk once, on Friday. Work orders, the crew roster, and the cabin lockers live in one process. Saturday photo uploads of muddy segments are most of the CPU and have crashed that process twice, which took the work-order page down with them. Roster changes and work-order changes still land together. Pick the starting shape.

```python
TEAM = 6
HOT = "photos"
SHARED_CRASHES = True
```

**Answer:** One desk service for work orders, the roster, and the lockers, plus photo ingest as its own deploy. Six people cannot staff a service per noun, and the roster still ships with the work orders, so those stay one process. Photo ingest is the hot path, and its crash is the outage the crew leader feels. That is the one functional split worth a network hop. Cloning the whole desk would copy the quiet roster onto every extra machine. The scale cube's Y-axis is this split, and the rest of that cube stays in Scalability Fundamentals.

```python
TEAM = 6
HOT = "photos"
SHARED_CRASHES = True


def shape(team: int, hot: str, shared_crashes: bool) -> str:
    if team <= 8 and shared_crashes:
        return f"one-desk-plus-{hot}"
    if team <= 8:
        return "one-desk"
    return "per-noun"


print(shape(TEAM, HOT, SHARED_CRASHES))
# one-desk-plus-photos
```

## When to Decompose

The desk is still one process and it works. Three pains show up in the same month. Which split is justified, and which piece moves first?

```text
1. whiteboard — a sketch with a box per noun. Nothing is hot. One crew ships the whole path.
2. same-release — every roster change is in the same pull request as a work-order change.
3. partner-club — a neighboring club edits cabin-locker counts. Their bad release has taken down work orders. They need to ship on Tuesday, not on the Friday train.
```

```python
PAINS = ["whiteboard", "same-release", "partner-club"]
```

**Answer:** Only the partner club. Cabin lockers move first, because another team needs a release train and their failures are already taking down the work-order page. The whiteboard is a drawing. The roster and the work orders change together, so they stay one service. A modular split inside the process is enough for the first two pains. The third pain is a deploy boundary.

```python
PAINS = ["whiteboard", "same-release", "partner-club"]
FIRST = {"partner-club": "cabin-lockers"}


def move(pain: str) -> str:
    return FIRST.get(pain, "none")


print(" ".join(move(pain) for pain in PAINS))
# none none cabin-lockers
```

## Boundary Cut

Four proposed cuts. Keep the one that is a business capability. Reject the others.

```text
1. orders-and-roster — work orders in one service, the crew roster in another. Every work-order change still ships with a roster change.
2. database-service — one service that reads and writes every table for every caller.
3. segment-catalog — mile markers, surface, and closures. A work order stores a segment id. A closure change does not change the work-order schema.
4. validation-service — one service that checks every form, from crew certification to locker counts.
```

```python
CUTS = ["orders-and-roster", "database-service", "segment-catalog", "validation-service"]
```

**Answer:** Keep the segment catalog. A closure is a different capability from a work order, and the work order only needs the segment id. Merge the work orders and the roster, because they still ship as one change. Reject the database service and the validation service. Both are technical layers. Every feature would have to edit them, and the rule would sit apart from the rows it judges.

```python
CUTS = ["orders-and-roster", "database-service", "segment-catalog", "validation-service"]
KEEP = {"segment-catalog"}

print(" ".join("keep" if name in KEEP else "reject" for name in CUTS))
# reject reject keep reject
```

## Data Ownership

The work-order service and the segment catalog both run `UPDATE segments SET closed = ...`. What breaks, and what does ownership look like instead?

```python
SHARED = ["work-orders", "segment-catalog"]
```

**Answer:** Two deploys share one schema. The catalog renames `closed` and ships on Tuesday. The work-order service still writes the old column on Friday, and there is no API version between them. The segment catalog is the only writer of `segments`. A work order stores `segment_id` and does not write `closed`. It asks the catalog, or it applies a closure the catalog published. An unknown id means the segment was retired. A shared prepare-and-commit across the two databases is two-phase commit, and that protocol stays in Transactions and Concurrency Control. One writer is the repair.

```python
SHARED = ["work-orders", "segment-catalog"]
OWNED = ["segment-catalog"]


def coupled(writers: list[str]) -> bool:
    return len(writers) > 1


print(coupled(SHARED), coupled(OWNED), OWNED[0])
# True False segment-catalog
```

## Sync or Events

Four hops follow a closure. Which ones are a request that returns yes or no, and which ones are a published event?

```text
1. mile-open — the crew leader asks whether mile 40 is open before leaving the barn. The page is that answer.
2. cache-pick — after the closure is saved, the cabin locker stages paint. The leader already has the closure on screen.
3. lead-named — the response must name the crew lead, or the page is a failure.
4. season-hours — the winter tally of volunteer hours, printed in March.
```

```python
STEPS = ["mile-open", "cache-pick", "lead-named", "season-hours"]
```

**Answer:** `mile-open` and `lead-named` stay calls. The page would be a guess without them. `cache-pick` and `season-hours` are events. The closure is already on screen, the locker can catch up, and March is a later reader. How the event waits on a bus, and the test for leaving the request, are When to Queue in Message Queues and Async Processing. Which broker stores it is that topic's choice. Put a request id on the event so a log search can follow the closure. The search stays in Observability.

```python
STEPS = ["mile-open", "cache-pick", "lead-named", "season-hours"]
SYNC = {"mile-open", "lead-named"}

print(" ".join("sync" if step in SYNC else "event" for step in STEPS))
# sync event sync event
```

## Discovery Style

The work-order service calls the segment catalog. Pick client-side, server-side, or mesh for each constraint.

```text
1. many-languages — four services, four languages. Callers know one stable address. An extra hop is acceptable. You will not ship a registry client in each language.
2. no-extra-hop — both sides are the one language you already ship. You will not put a proxy in the path.
3. uniform-mtls — every service-to-service hop must present a certificate, and the handlers must not contain that handshake.
```

```python
CASES = ["many-languages", "no-extra-hop", "uniform-mtls"]
```

**Answer:** Server-side, client-side, then mesh. Several languages and one stable address means a balancer reads the registry and the callers stay simple. The algorithm that picks an instance stays in Load Balancing. No extra hop, with code you ship, means the caller reads the registry and connects. Uniform certificates, with handlers that do not implement them, means a sidecar on each instance. The public trail map is the API gateway in Networking and Communication. That host is the browser's front door, not this lookup.

```python
CASES = ["many-languages", "no-extra-hop", "uniform-mtls"]
CHOICE = {
    "many-languages": "server-side",
    "no-extra-hop": "client-side",
    "uniform-mtls": "mesh",
}

print(" ".join(CHOICE[name] for name in CASES))
# server-side client-side mesh
```

## Saga Compensation

A closure is three local commits. The segment catalog marks mile 40 closed. The work-order service opens repair `r-40`. The crew desk then fails to assign a Saturday sawyer, because nobody certified is free. What does each earlier step undo, and is an orchestrator or choreography the better fit?

```python
DONE = ["close-mile-40", "open-r-40"]
FAILED = "assign-sawyer"
```

**Answer:** Cancel `r-40`, then mark mile 40 open. Those are new writes, in reverse order of the commits that succeeded. The catalog does not roll back the work-order database. An orchestrator is the better fit. The desk is one team, the chain is three steps, and a crew leader asks what happens when Saturday falls through. One coordinator can read that path back. Choreography would also compensate, with each service reacting to the last event, and the story would be spread across three codebases. The bus those events would ride, and the outbox the first event may need, stay in Message Queues and Async Processing. A prepare-and-commit across the three databases is two-phase commit, and that protocol stays in Transactions and Concurrency Control.

```python
DONE = ["close-mile-40", "open-r-40"]
FAILED = "assign-sawyer"
UNDO = {"close-mile-40": "reopen-mile-40", "open-r-40": "cancel-r-40"}


def compensate(done: list[str]) -> list[str]:
    return [UNDO[step] for step in reversed(done)]


print(compensate(DONE), FAILED)
# ['cancel-r-40', 'reopen-mile-40'] assign-sawyer
```

## Vendor on the Path

A forecast vendor has a slow tail of 8 seconds, and it was down this morning. The page budget for saving a closure is 300 ms. Saving the closure has to succeed even when the forecast is stale. The Saturday go-or-no-go page may show the last forecast the desk stored. What sits in an adapter, what stays on the request, and when does a queue help?

```python
VENDOR_P99_MS = 8000
PAGE_BUDGET_MS = 300
STEPS = ["save-closure", "refresh-forecast", "vendor-url"]
```

**Answer:** The adapter is the only code that knows the vendor URL, the odd status codes, and the timeout. It stores the last good forecast. The closure save stays on the request and reads that stored forecast. It does not call the vendor. Eight seconds does not fit a 300 ms page. Refreshing the forecast goes on a queue, because the closure is already saved and the leader can leave. A vendor outage then fails the refresh, not the save. That split is When to Queue in Message Queues and Async Processing. The adapter is not a design for sending the forecast to a phone, and it is not a payment flow.

```python
VENDOR_P99_MS = 8000
PAGE_BUDGET_MS = 300
STEPS = ["save-closure", "refresh-forecast", "vendor-url"]
PLACE = {"save-closure": "request", "refresh-forecast": "queue", "vendor-url": "adapter"}


def on_request(vendor_ms: int, budget_ms: int) -> bool:
    return vendor_ms <= budget_ms


print(" ".join(PLACE[step] for step in STEPS), on_request(VENDOR_P99_MS, PAGE_BUDGET_MS))
# request queue adapter False
```
