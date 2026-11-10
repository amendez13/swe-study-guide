# Rate Limiting and Throttling — Drills

Original practice for where a budget sits, which key it counts, and which counter enforces it. Each card is one exercise: commit to an answer, then check it. The numbers are invented for Copperline Tram, a hillside line with three cars, alder, beech, and cedar. Riders ask the desk for a seat. The gateway that can host the check stays in Networking and Communication. Slowing a producer stays in Message Queues and Async Processing. Shedding because the hill is full stays in High Availability and Reliability. Pinning a rider to one car stays in Load Balancing. How a client waits stays in Distributed System Failure Modes. A lock around the counter stays in Transactions and Concurrency Control.

## Where to Put

The desk is choosing a home for the check. Who can you trust, and which paths share a budget?

```text
1. phone-pause — the app can delay its own asks. A modified app can skip the delay.
2. every-path — seat asks and timetable recomputes share one public budget, and both services sit behind one host.
3. timetable-only — only the timetable path is expensive, and seat asks keep their own budget.
```

```python
CASES = ["phone-pause", "every-path", "timetable-only"]
```

**Answer:** The phone is a client, and a pause there is a courtesy. The desk cannot trust it. Every public path sharing one budget belongs on the gateway, the API Gateway, which already sees those calls and applies the decision. The timetable-only budget belongs on the timetable service, as a library in its request pipeline, so seat asks never spend it. The gateway's other jobs, the token check and the route, stay on the API Gateway card.

```python
CASES = ["phone-pause", "every-path", "timetable-only"]
PLACE = {
    "phone-pause": "client",
    "every-path": "gateway",
    "timetable-only": "service",
}

print(" ".join(PLACE[name] for name in CASES))
# client gateway service
```

## Limit By

Three keys are proposed for the lower station. What goes wrong with the weak ones?

```text
1. cafe-nat — twenty riders share one address. The counter key is that address.
2. one-path — rider 14's seat asks and timetable recomputes share one counter, capped like a seat ask.
3. split-key — seat asks are one key for rider 14, and timetable recomputes are another, capped at 4 a minute.
```

```python
CASES = ["cafe-nat", "one-path", "split-key"]
```

**Answer:** The cafe address treats twenty riders as one caller. Rider 14 spends the stop, and riders 15 through 19 are refused with them. A rider who changes networks starts a fresh budget. One shared path lets the timetable recompute run as often as a seat ask, so the expensive path has no cap of its own. The split key counts the person who holds the credential, and the timetable key stops at 4 a minute. A day quota of 500 seat asks can sit beside the short rate, so a script that never bursts still stops. A cap on notification sends stays on the Push Notification System card.

```python
CASES = ["cafe-nat", "one-path", "split-key"]
FAULT = {
    "cafe-nat": "shared-address",
    "one-path": "expensive-path-uncapped",
    "split-key": "none",
}

print(" ".join(FAULT[name] for name in CASES))
# shared-address expensive-path-uncapped none
```

## Token Burst

Rider 14's bucket holds 8 permits and refills 2 permits a second. It starts full. How many seat asks pass in a burst that arrives together, and how many pass one second later? From empty, what does a quiet stretch of 5 seconds leave in the bucket?

```python
CAPACITY = 8
REFILL = 2
QUIET_S = 5
```

**Answer:** The burst takes 8, which empties the bucket. One second later the refill has put 2 permits back, so 2 asks pass. Five quiet seconds from empty would add 10, and the cap leaves 8. Idle time does not raise the burst.

```python
CAPACITY = 8
REFILL = 2
QUIET_S = 5


def burst_then_one_second(capacity: int, refill: int) -> tuple[int, int]:
    return capacity, min(capacity, refill)


def after_quiet_from_empty(capacity: int, refill: int, quiet_s: int) -> int:
    return min(capacity, refill * quiet_s)


print(
    burst_then_one_second(CAPACITY, REFILL),
    after_quiet_from_empty(CAPACITY, REFILL, QUIET_S),
)
# (8, 2) 8
```

## Token or Leaky

Ten seat asks arrive together from a rider who expects a short burst to succeed. Fifteen timetable recomputes arrive together, and the planner must see them leave at 1 per second. The timetable queue holds 6. Which algorithm fits each path, how many seat asks pass, how many are refused at once, and how many timetable asks wait?

```python
SEAT_ARRIVED = 10
CAPACITY = 8
TIMETABLE_ARRIVED = 15
QUEUE = 6
```

**Answer:** A token bucket for the seat asks. Eight pass. The two past the capacity are 429 in the moment they arrive, and the bucket keeps no queue. A leaky bucket for the timetable. Six wait in the short queue and leave at 1 per second, so the queue is empty 6 seconds later. Nine are dropped because the queue is already full. Slowing a producer the desk can reach, and the depth of a broker queue, stay on Backpressure. The seat path refuses at once. The timetable path waits while the queue has room.

```python
SEAT_ARRIVED = 10
CAPACITY = 8
TIMETABLE_ARRIVED = 15
QUEUE = 6


def token(arrived: int, capacity: int) -> tuple[int, int]:
    passed = min(arrived, capacity)
    return passed, arrived - passed


def leaky(arrived: int, queue: int) -> tuple[int, int]:
    waiting = min(arrived, queue)
    return waiting, arrived - waiting


print(token(SEAT_ARRIVED, CAPACITY), leaky(TIMETABLE_ARRIVED, QUEUE))
# (8, 2) (6, 9)
```

## Window Seam

A fixed window allows 20 seat asks in a clock minute. Twenty land in the last three seconds of minute 12. Twenty land in the first three seconds of minute 13. Does each window allow its own count, and how many asks crossed the edge?

```python
LIMIT = 20
LATE = 20
EARLY = 20
```

**Answer:** Each window shows 20, which the rule allows, so both sides look fine. The six seconds around the edge carried 40 asks, two windows of traffic. A fixed window admits that seam. A sliding count would see the asks that are still inside the last minute.

```python
LIMIT = 20
LATE = 20
EARLY = 20


def seam(late: int, early: int, limit: int) -> tuple[bool, int]:
    each_window_allows = late <= limit and early <= limit
    return each_window_allows, late + early


print(*seam(LATE, EARLY, LIMIT))
# True 40
```

## Sliding Weight

Twenty seconds of a 60-second window have elapsed. The previous minute recorded 24 asks. This minute has recorded 9. The limit is 20. What is the weighted count, and is it over the limit?

```python
PREV = 24
CURR = 9
ELAPSED = 20
WINDOW = 60
LIMIT = 20
```

**Answer:** The previous minute still overlaps the last 60 seconds by 40 seconds. The estimate keeps 24 * 40 / 60 = 16 of those asks and adds the 9 already in this minute. The weighted count is 25, which is over 20, so the ask is refused. A log of timestamps would be exact and would store every ask. This estimate stores two counts. The division lands on a whole number here.

```python
PREV = 24
CURR = 9
ELAPSED = 20
WINDOW = 60
LIMIT = 20


def weighted(prev: int, curr: int, elapsed: int, window: int) -> int:
    return prev * (window - elapsed) // window + curr


count = weighted(PREV, CURR, ELAPSED, WINDOW)
print(count, count > LIMIT)
# 25 True
```

## Counter Race

One permit remains on the shared seat-ask counter. Alder reads 1 and admits. Beech reads 1 before alder writes, and admits. Each would store 0. How many asks pass, and how many pass when the decrement is one atomic step? Why is a lock or a two-phase commit the wrong repair?

```python
REMAINING = 1
CARS = 2
```

**Answer:** Both cars admit, so 2 asks pass on 1 permit. An atomic decrement admits 1. The second car sees 0 and refuses. One script that reads, decides, and writes before another car runs does the same thing. A distributed lock, two-phase commit, and a consensus round stay in Transactions and Concurrency Control. They coordinate a unit of work across records. This failure is one counter updated in two steps.

```python
REMAINING = 1
CARS = 2


def raced(remaining: int, cars: int) -> int:
    return sum(1 for _ in range(cars) if remaining > 0)


def atomic(remaining: int, cars: int) -> int:
    admitted = 0
    left = remaining
    for _ in range(cars):
        if left > 0:
            left -= 1
            admitted += 1
    return admitted


print(raced(REMAINING, CARS), atomic(REMAINING, CARS))
# 2 1
```

## Retry-After

Rider 14's board received HTTP 429 with Retry-After: 8, and X-RateLimit-Remaining: 0. Four boards at the lower station each received that answer. How many of those four call again during this second if they honor the header, and how many call if they ignore it? What does the second choice do to the desk?

```python
RETRY_AFTER_S = 8
BOARDS = 4
```

**Answer:** A board that honors the header waits 8 seconds and then sends one ask, so this second sees 0 of the four. A board that ignores the header calls again now, so this second sees 4. Those four immediate calls are a retry storm: they spend the capacity the refusal was meant to protect. The growing gap and the spread that keep retries off one second stay on Timeouts and Retries. This exercise is the header.

```python
RETRY_AFTER_S = 8
BOARDS = 4


def retries_this_second(boards: int, honors_header: bool) -> int:
    if honors_header:
        return 0
    return boards


print(retries_this_second(BOARDS, True), retries_this_second(BOARDS, False), RETRY_AFTER_S)
# 0 4 8
```
