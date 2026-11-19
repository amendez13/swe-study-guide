# Rate Limiting and Throttling

A rate limiter is a per-caller budget checked before the handler does the work. The usual refusal is HTTP 429 Too Many Requests, with `Retry-After` and the remaining-budget headers. Public APIs such as GitHub and Stripe publish budgets like this: GitHub counts an authenticated caller by the user, and Stripe counts by the account and by the endpoint. The gateway that can host the check, the queue that slows a producer, shedding when the whole service is full, a pin to one server, and the wait after `Retry-After` live in the topics that own them. A shared counter, and the race of two servers reading that counter before either writes, live here.

## Key Points

- **Rate limiter** — a check on one caller, answered before the handler runs. A client-side pause can be skipped. The usual shared place is the API gateway. A spent budget is 429 with `Retry-After` and the `X-RateLimit-*` headers. A service that is full for every caller is load shedding.
- **Rate limit rules** — an IP address collapses everyone behind one NAT. A user id or API key counts the credential. A route gives an expensive call, such as search, its own key. A burst rate and a day quota of 500 can both apply. A notification send cap stays on the Push Notification System card.
- **Throttle or reject** — a short queue or a slower producer, versus 429 with nothing kept. Slowing a producer is Backpressure. A full queue refuses the next request.
- **Token bucket** — 8 permits, refilled at 2 a second, never past 8. A burst of 8 passes, then 2 more a second later. One count and a timestamp per caller. A refused request does not take a permit.
- **Leaky bucket** — a queue of 6 that drains at 1 a second. A burst of 15 leaves 6 waiting and drops 9. User-facing writes want the burst. A planner that needs a steady arrival wants this queue.
- **Fixed window counter** — 20 requests in a clock minute, then the count starts over. Twenty at the end of one minute and twenty at the start of the next are 40 requests in six seconds.
- **Sliding window** — a log of timestamps is exact and grows with the requests. Two counts, weighted by the overlap, estimate the same span. At 20 seconds in, 24 in the previous minute and 9 in this one estimate 25, over a limit of 20.
- **Distributed rate limiting** — a shared counter, a local share synced on a timer, or a sticky pin to one server. Two servers that both read 1 remaining permit both admit. An atomic decrement or one script is the fix. A lock and two-phase commit stay in Transactions and Concurrency Control.

## Example

The teaching write bucket holds 8 permits and refills 2 a second. These are the numbers from the cards, smaller than GitHub's published hourly budget and Stripe's published per-second budget, so the arithmetic stays visible. A fixed window of 20 still shows a legal count on each side of the minute. Twenty seconds into the new minute, the weighted estimate is 25 against a limit of 20. Two servers both read one remaining permit.

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

The burst takes 8, and one second later 2 more pass. Five quiet seconds from an empty bucket would add 10, and the cap leaves 8. The seam admits 40. The weighted count is over the limit of 20, so that request is refused. The raced counter admits 2 requests on 1 permit. One script, or an atomic decrement that admits only a non-negative result, admits 1.

## Which counter

| What you need | Counter | Watch for |
| --- | --- | --- |
| A short burst, then a steady rate | Token bucket | The full bucket arrives at once |
| A smooth departure into the next stage | Leaky bucket queue | The last job waits up to the queue depth |
| One integer per clock minute | Fixed window | Up to twice the limit at the boundary |
| A bound on any recent minute, in two integers | Sliding window counter | The weight is an estimate |
| An exact count of the last minute | Sliding log | One timestamp per request |
| The same budget on every server | Shared atomic counter | Two read-then-write steps admit twice |

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — API Gateway. A usual place for one budget over every public route. The bucket stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Backpressure. Slowing a producer stays there. The choice to throttle or reject stays here.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — Circuit Breaker Pattern and Graceful Degradation. Load shedding, when the whole service is full, stays there. A per-caller quota stays here.
- [Load Balancing](../04_Load_Balancing/) — Sticky Sessions (Session Affinity). Pinning a caller to one server stays there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. How a client waits after `Retry-After` stays there.
- [Observability](../25_Observability/) — the chart of 429s, and the page that fires when that rate climbs.
- [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/) — a limiter race is a missing atomic step on a shared counter. Locks, two-phase commit, and consensus stay there.
- [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/) — a cap on notifications sent to one person. The product numbers stay there. The counter shape stays here.
- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — The Four-Step Framework. Name the caller, the limit, and the failure mode before picking the counter.
