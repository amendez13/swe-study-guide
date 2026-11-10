# Real-Time and Notification Systems — Drills

Original practice for which channel leaves the desk, which switch stops a send, and which fan-out a recipient count selects. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Northwick Allotments, where plot holders share taps, a tool shed, and a Saturday seed list. How a socket is held stays in Networking and Communication. The broker's promise, the queue, and a parked message stay in Message Queues and Async Processing. The provider adapter stays in Microservices and System Decomposition. The wait between tries stays in Distributed System Failure Modes. The counter that enforces a budget stays in Rate Limiting and Throttling. A polygon test stays in Geospatial and Location-Based Services. The chat screen, feed ranking, and a feed cache stay in Classic Design Problems.

## Which Channel

Three notices are ready, and the matching channel switch is on. Which path does each one take?

```python
EVENTS = (
    ("frost", True),
    ("frost", False),
    ("seed-list", True),
)
```

**Answer:** Frost with a device token is a platform push. Frost with no token is SMS, because it cannot wait and push has nowhere to go. The seed list can wait, so it is email even though a token is on file. APNs and FCM are the push providers. The open-app path is a different choice, on In-App or Push, and it applies when the member is in the app watching the board.

```python
EVENTS = (
    ("frost", True),
    ("frost", False),
    ("seed-list", True),
)


def channel(kind: str, has_token: bool) -> str:
    if kind == "seed-list":
        return "email"
    if has_token:
        return "push"
    return "sms"


print(*(channel(kind, has_token) for kind, has_token in EVENTS))
# push sms email
```

## Preference Gate

Member 14's switches: push on, SMS off, email on, seed-list off, frost on. What happens to a seed-list push, a frost text, and a frost push?

```python
TYPE_ON = {"frost": True, "seed-list": False}
CHANNEL_ON = {"push": True, "sms": False, "email": True}
NOTICES = (("seed-list", "push"), ("frost", "sms"), ("frost", "push"))
```

**Answer:** The seed-list push stops because the type is off. The frost text stops because SMS is off. The frost push passes both switches. Stopping means the service renders nothing and writes nothing to a queue. The frost push that passes still has to fit the transactional budget on Push Notification System. The counter under that budget is the Rate Limiter.

```python
TYPE_ON = {"frost": True, "seed-list": False}
CHANNEL_ON = {"push": True, "sms": False, "email": True}
NOTICES = (("seed-list", "push"), ("frost", "sms"), ("frost", "push"))


def gate(kind: str, channel_name: str) -> str:
    if not TYPE_ON[kind] or not CHANNEL_ON[channel_name]:
        return "stop"
    return "send"


print(*(gate(kind, channel_name) for kind, channel_name in NOTICES))
# stop stop send
```

## Token Book

Member 14 has a shed handset and a pocket handset. The shed install refreshes its token to `tok-shed-2`. The provider then calls that current shed token unregistered. What is stored after the refresh, and what remains after the rejection?

```python
ROWS = (("shed", "tok-shed"), ("pocket", "tok-pocket"))
REFRESHED = "tok-shed-2"
```

**Answer:** The refresh replaces the shed row. The book still has two installs: `tok-shed-2` and `tok-pocket`. Appending the new token beside `tok-shed` would leave a stale address in the book. The rejection deletes the row that now holds `tok-shed-2` and leaves the pocket handset. The membership email and the shed phone number are other rows in the same book. They are addresses, and this rejection does not drop them.

```python
ROWS = (("shed", "tok-shed"), ("pocket", "tok-pocket"))
REFRESHED = "tok-shed-2"


def refresh(rows: tuple[tuple[str, str], ...], install: str, token: str) -> tuple[tuple[str, str], ...]:
    return tuple((name, token if name == install else current) for name, current in rows)


def drop(rows: tuple[tuple[str, str], ...], token: str) -> tuple[str, ...]:
    return tuple(name for name, current in rows if current != token)


updated = refresh(ROWS, "shed", REFRESHED)
print(updated, drop(updated, REFRESHED))
# (('shed', 'tok-shed-2'), ('pocket', 'tok-pocket')) ('pocket',)
```

## Notify Cap

Promotional push is capped at 2 per member each week. Transactional push is capped at 20 per member each day. Member 14 has already been sent 2 seed-list pushes this week and 3 tap pushes today. A third seed-list push, a fourth tap push, and a 21st tap push arrive. Which ones leave?

```python
PROMO_CAP = 2
TX_CAP = 20
PROMO_SENT = 2
TX_SENT = 3
TX_FULL = 20
```

**Answer:** The third seed-list push stops. The fourth tap push leaves, because 3 is under 20. The 21st tap push stops. The two budgets are separate, so a spent promotional week does not block frost or a tap turn. This card states the product numbers. Token bucket, leaky bucket, and the window counters are the Rate Limiter. None of those shapes is selected here.

```python
PROMO_CAP = 2
TX_CAP = 20
PROMO_SENT = 2
TX_SENT = 3
TX_FULL = 20


def allow(sent: int, cap: int) -> bool:
    return sent < cap


print(allow(PROMO_SENT, PROMO_CAP), allow(TX_SENT, TX_CAP), allow(TX_FULL, TX_CAP))
# False True False
```

## Presence Grace

The connection grace is 12 seconds. Three things happen on member 14's socket: a drop that reconnects at 8 seconds, an explicit logout, and a drop that is still open at 20 seconds. What is the mark each time? Shed partners are m2 (listed, online), m3 (listed, offline), and m4 (online, not listed). Who is told when the mark becomes offline?

```python
GRACE_S = 12
PEERS = (("m2", True, True), ("m3", True, False), ("m4", False, True))
CASES = ((8, False), (0, True), (20, False))
```

**Answer:** The 8-second reconnect stays online, and nobody is told, because the mark did not change. Logout is offline immediately, and the grace does not apply. The drop that lasts 20 seconds is past 12, so the mark is offline. Offline is told to m2 only. m3 is a shed partner and will read the mark on the next open. m4 is online and is not waiting on member 14. A beat every 20 seconds with a key that lives 50 is the other grace: a 20-second gap stays online, and a 50-second gap expires. The socket those marks sit on is WebSockets and SSE.

```python
GRACE_S = 12
PEERS = (("m2", True, True), ("m3", True, False), ("m4", False, True))
CASES = ((8, False), (0, True), (20, False))


def mark(drop_s: int, logout: bool) -> str:
    if logout:
        return "offline"
    if drop_s <= GRACE_S:
        return "online"
    return "offline"


def told(state: str) -> tuple[str, ...]:
    if state != "offline":
        return ()
    return tuple(name for name, interested, online in PEERS if interested and online)


states = tuple(mark(drop_s, logout) for drop_s, logout in CASES)
print(states, *(told(state) for state in states))
# ('online', 'offline', 'offline') () ('m2',) ('m2',)
```

## Fan-Out Pick

Three events name a recipient count. The write line is 500. The read line is 5,000. Which shape does each count take?

```python
WRITE_MAX = 500
READ_MIN = 5000
COUNTS = (("west-tap", 6), ("tool-recall", 900), ("pump", 18000))
```

**Answer:** Six neighbors are a write: one row in each list, and the read is that list. Eighteen thousand members are a read: one stored alert, pulled on open. Nine hundred is the hybrid. The on-duty stewards inside that set get a written row, and the other recipients pull one shared notice. The screen that sets those two beside each other, any ranking of it, and any cache of it are News Feed / Timeline. Those steps are not part of this choice.

```python
WRITE_MAX = 500
READ_MIN = 5000
COUNTS = (("west-tap", 6), ("tool-recall", 900), ("pump", 18000))


def pick(recipients: int) -> str:
    if recipients <= WRITE_MAX:
        return "write"
    if recipients >= READ_MIN:
        return "read"
    return "hybrid"


print(*(pick(count) for _name, count in COUNTS))
# write hybrid read
```

## Offline Summary

Member 14 was away from the tap board. Nine tap updates are waiting. Earlier in the week, three tool reminders were waiting. What does the handset receive in each case?

```python
EACH_MAX = 3
PILES = (9, 3)
```

**Answer:** Nine is past 3, so the handset receives one summary: the count, and the latest turn. The nine rows stay on the server. Three is at the line, so the handset receives each reminder. A pile delivered one by one is how a night of sensor flaps becomes a lock screen of stale turns. The summary is the notice. The stored rows are the record.

```python
EACH_MAX = 3
PILES = (9, 3)


def plan(waiting: int) -> tuple[str, int]:
    if waiting > EACH_MAX:
        return ("summary", 1)
    return ("each", waiting)


print(*(plan(waiting) for waiting in PILES))
# ('summary', 1) ('each', 3)
```

## Dup Send

The provider accepted notice `n-18`. The accept was lost, so the worker sent `n-18` again, and then sent `n-19`. The handset observes `n-18`, `n-18`, `n-19`. What does it show?

```python
ARRIVED = ("n-18", "n-18", "n-19")
```

**Answer:** The handset shows `n-18` once and then `n-19`. The second `n-18` is the same notice. The worker's retry until accept is at-least-once, and a lost accept is how the duplicate is produced. Message Delivery Guarantees is that broker promise. The pause before the resend is Timeouts and Retries. A per-plot sequence still orders the screen when `n-19` arrives first. The queue is at-least-once, and the id is the handset's record of what it has already shown.

```python
ARRIVED = ("n-18", "n-18", "n-19")


def shown(ids: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    kept: list[str] = []
    for notice_id in ids:
        if notice_id in seen:
            continue
        seen.add(notice_id)
        kept.append(notice_id)
    return tuple(kept)


print(shown(ARRIVED))
# ('n-18', 'n-19')
```
