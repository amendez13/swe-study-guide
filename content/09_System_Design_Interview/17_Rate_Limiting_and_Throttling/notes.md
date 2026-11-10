# Rate Limiting and Throttling

Copperline Tram sells seats on three cars, alder, beech, and cedar. A budget decides how often one rider may ask, where that check sits, and whether an ask over the budget waits or comes back as 429. The gateway that can host the check, the queue that slows a producer, shedding when the hill is full, a pin to one car, and the wait after Retry-After live in the topics that own them. A shared limiter counter, and the race of two cars reading that counter before either writes, live here. Locks, two-phase commit, and consensus stay in Transactions and Concurrency Control.

## Key Points

- **Rate limiter** — the budget on one rider, checked before a seat is assigned. A phone pause can be skipped. The usual shared place is the API Gateway. A spent personal budget is 429 with Retry-After and the X-RateLimit-* headers. The hill being full is load shedding.
- **Rate limit rules** — an address collapses the cafe's NAT. A rider id or API key counts the person. A path gives the timetable its own key. A burst rate and a day quota of 500 can both apply. A notification send cap stays on the Push Notification System card.
- **Throttle or reject** — a short queue or a slower producer, versus 429 with nothing kept. Slowing a producer is Backpressure.
- **Token bucket** — 8 permits, refilled at 2 a second, never past 8. A burst of 8 passes, then 2 more a second later. One count and a timestamp per rider.
- **Leaky bucket** — a queue of 6 that drains at 1 a second. A burst of 15 leaves 6 waiting and drops 9. Seat asks want the burst. The timetable wants the steady drain.
- **Fixed window counter** — 20 asks in a clock minute, then the count starts over. Twenty at the end of one minute and twenty at the start of the next are 40 asks in six seconds.
- **Sliding window** — a log of timestamps is exact and grows with the asks. Two counts, weighted by the overlap, estimate the same span. At 20 seconds in, 24 in the previous minute and 9 in this one estimate 25, over a limit of 20.
- **Distributed rate limiting** — a shared counter, a local share synced on a timer, or a sticky pin to one car. Two cars that both read 1 remaining permit both admit. An atomic decrement or one script is the fix. A lock and two-phase commit stay in Transactions and Concurrency Control.

## Example

Rider 14's seat-ask bucket holds 8 and refills 2 a second. A fixed window of 20 still shows a legal count on each side of the minute. Twenty seconds into the new minute, the weighted estimate is 25 against a limit of 20. Alder and beech both read one remaining permit.

```python
CAPACITY = 8
REFILL = 2
LATE = 20
EARLY = 20
PREV = 24
CURR = 9
ELAPSED = 20
WINDOW = 60
REMAINING = 1


def after_burst(capacity: int, refill: int) -> tuple[int, int]:
    return capacity, min(capacity, refill)


def seam_total(late: int, early: int) -> int:
    return late + early


def weighted(prev: int, curr: int, elapsed: int, window: int) -> int:
    return prev * (window - elapsed) // window + curr


def raced_admits(remaining: int) -> int:
    return sum(1 for seen in (remaining, remaining) if seen > 0)


print(
    after_burst(CAPACITY, REFILL),
    seam_total(LATE, EARLY),
    weighted(PREV, CURR, ELAPSED, WINDOW),
    raced_admits(REMAINING),
)
# (8, 2) 40 25 2
```

The burst takes 8, and one second later 2 more pass. Five quiet seconds from an empty bucket would add 10, and the cap leaves 8. The seam admits 40. The weighted count is over the limit of 20, so that ask is refused. The raced counter admits 2 asks on 1 permit. One script, or an atomic decrement, admits 1.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — API Gateway. A usual place for one budget over every public path. The bucket stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Backpressure. Slowing a producer stays there. The choice to throttle or reject stays here.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — Circuit Breaker Pattern and Graceful Degradation. Load shedding when the hill is full stays there. A per-rider quota stays here.
- [Load Balancing](../04_Load_Balancing/) — Sticky Sessions (Session Affinity). Pinning a rider to one car stays there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. How a client waits after Retry-After stays there.
- [Observability](../25_Observability/) — the chart of rejects and the page that fires.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — a limiter race is a missing atomic step on a shared counter. Locks, two-phase commit, and consensus stay there.
