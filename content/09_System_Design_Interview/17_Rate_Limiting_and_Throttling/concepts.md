## Rate Limiter

**What it is.** A rate limiter decides whether this caller may make another request right now. It answers before the handler does the expensive work.

**Why it exists.** One script that pages through every record, or one client that retries in a tight loop, can occupy the API and slow everyone else. A per-caller budget stops that client from taking the whole service. A different problem is the service itself running out of capacity for every caller. That decision is load shedding, covered with the Circuit Breaker Pattern and Graceful Degradation in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

**How it works.** The request hits the limiter, which loads that caller's counter from a store the servers share, often Redis. The rule allows the call, or it refuses. The usual refusal is HTTP 429 Too Many Requests. `Retry-After: 8` means wait 8 seconds. The header may instead be an HTTP date. `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` report the budget on the response, including responses that still succeed, so a careful client slows down before it is refused. These `X-RateLimit-*` names are a common convention. HTTP 429 is valid without them.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 8
X-RateLimit-Limit: 8
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 8
```

That sample is a teaching budget of 8, and it prints the reset as a delay of 8 so it lines up with `Retry-After`. GitHub publishes a larger real budget: 5,000 requests per hour for a personal access token, and 60 requests per hour for an unauthenticated caller, counted by IP address. Some GitHub App and Enterprise installations are higher, and routes such as search have a separate, tighter budget. GitHub may answer an exhausted primary budget with 403 or 429, with the remaining count at 0. Its `x-ratelimit-reset` header is a UTC epoch second, so the wait is that value minus now. When GitHub sends `Retry-After`, wait that many seconds. Stripe's live API publishes 100 requests per second per account, 25 per second in the sandbox, and 25 per second on many individual endpoints as well. Stripe's 429 carries `Stripe-Rate-Limited-Reason`. A Stripe 429 without that header can be an object lock timeout, which is a different failure.

A pause inside the client is still worth doing. Stripe's own guidance is a client-side token bucket, so a well-behaved integration stays under the published budget. A modified client skips the pause. The server still enforces the limit.

Put a budget that covers every public route on the API gateway, which already sees those calls. The gateway's other jobs stay on the API Gateway card in [Networking and Communication](../10_Networking_and_Communication/). Put a budget for one expensive route, such as search, inside that service, so ordinary reads never spend it. How long a client waits, and how a fleet of retries stays off the same second, is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). The chart of 429s stays in [Observability](../25_Observability/). Naming the caller, the limit, and the failure mode before picking an algorithm is the scoping step on The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/).

**Trade-offs.** A client-side delay is cheap and saves a polite caller from burning its own budget. It leaves the API open to a caller that ignores it. A gateway check is one place to change, and it puts a shared counter on every public route. A check inside one service sees that route's real cost and leaves other routes alone. The next route someone adds can ship without it.

**In an interview.** Say what you are protecting, who the caller is, and where the check runs. Name 429, `Retry-After`, and the remaining-budget headers. Keep a per-caller budget separate from load shedding, which refuses work because the whole service is full.

**Recap.**

- A rate limiter counts one caller's recent requests and answers before the handler does the work.
- The usual refusal is HTTP 429, with `Retry-After` and the `X-RateLimit-*` headers.
- A client-side pause can be skipped, so the server enforces the budget.
- A budget over every public route belongs on the API gateway. A budget for one expensive route belongs in that service.
- A service that is full for every caller is load shedding, which is a different decision.

![Rate Limiter](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-1-rate-limiter.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 1.*

## Rate Limit Rules

**What it is.** A rate limit rule names the caller, the route, and the allowance. The counter key is that tuple. Two rules can apply to the same call, and the call has to pass both.

**Why it exists.** A limit on the wrong key punishes the wrong people, and one shared counter lets a cheap route and an expensive route spend the same budget. GitHub's unauthenticated limit of 60 requests per hour is keyed by IP address, so everyone behind that address shares it. An authenticated GitHub call counts against the user, and it stays on that hourly budget when the client changes IP address. Stripe counts each named operation as its own endpoint on top of the account-wide budget, so a flood of one operation can be capped while the rest of the account still has room.

**How it works.** An IP address is easy to read and a weak key. Twenty people on one cafe Wi-Fi share one public address through NAT. One busy client spends that address, and the other nineteen are refused with it. A phone that leaves the Wi-Fi and continues on cellular presents a new address and starts a fresh budget. A user id, or the API key you issued, counts the holder of the credential. A route counts the work. Creating an issue and running search are different costs, so each route keeps its own key.

A short rate and a longer quota can both apply to the same user. In the teaching budget, the write bucket holds 8 permits and refills 2 permits a second, and a quota of 500 writes a day sits beside it. A client that never bursts and simply sends with the refill reaches 500 in 250 seconds, because 2 per second times 250 seconds is 500. The daily quota is what stops that steady sender. The expensive route has its own key, capped at 4 requests a minute. A cap on how many notifications one person may be sent is a product rule. The numbers for that rule live on the Push Notification System card in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/). The counters that enforce a rule are the cards that follow.

**Trade-offs.** An IP key needs no login, which is why it fits an unauthenticated public route, and it collapses everyone behind a NAT. A user or API-key key survives a network change and misses anonymous traffic, so anonymous calls still need an IP key or they are unlimited. One counter for every route is simple, and the expensive route then runs as often as the cheap one. Separate keys match cost, and you have more counters to store and explain. A daily quota stops a slow scrape that never trips the per-second bucket, at the cost of a second check on the same request.

**In an interview.** Start with the key. Say "per API key and per route" for an authenticated API, and say why an IP key fails for users who share a NAT or who change networks. Then name the second window, such as a daily quota next to a burst rate, when a steady caller is part of the threat.

**Recap.**

| Key | What it counts | Where it fails |
| --- | --- | --- |
| IP address | The public address | Many people share one NAT. A new network starts a new budget. |
| User id or API key | The credential holder | Anonymous calls have no credential, so they need another key. |
| Route, plus the caller | The cost of that operation | A new route ships uncapped until someone adds its rule. |
| Burst rate and daily quota | The same caller, two windows | The request pays for two checks. The quota catches the steady sender. |

![Rate Limit Rules](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-2-rate-limit-rules.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 2.*

## Throttle or Reject

**What it is.** Past the budget, the server either slows the work down or refuses it. A throttle keeps the request waiting, or tells a producer to send more slowly. A reject returns 429 and keeps no copy of the request.

**Why it exists.** Accepting every extra request fills the process with work it cannot finish. The queue grows, memory grows, and requests that arrived on time wait behind requests that should have been turned away. Refusing once the queue is full leaves room for the work already accepted.

**How it works.** A throttle holds a short queue and lets the request wait its turn. For a producer you can reach, such as your own worker, the throttle is a signal to send more slowly. That signal is Backpressure in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). The queue, its depth, and when to add consumers stay on that card. A reject answers 429 and drops the request. The client decides whether to try again after `Retry-After`.

Hold an expensive job, such as a report rebuild, when the caller can wait and the queue still has room. Reject a browser call, which can try again after the header. Reject the next request once the queue is full. Stripe publishes this same split under two names: a rate limit counts how many requests start per second, and a concurrency limit counts how many are still in flight. The published live-mode default for ordinary traffic is 50 in-flight requests. A concurrency refusal is still a 429. It means "too much is already running," which is the full-queue case.

**Trade-offs.** A short queue smooths a burst and adds latency up to the depth of the queue. An unbounded queue turns that latency into an outage. An immediate 429 keeps the server's memory flat and pushes the retry decision to the client, which may retry badly. Slowing a producer you control wastes less work than refusing a message you will only requeue. You can slow a producer only when you have a channel back to it.

**In an interview.** Pick throttle when you control the producer or the caller can wait, and name a maximum queue depth. Pick reject for a public HTTP API, and say that a full queue refuses the next request. Point at Backpressure for the producer signal, and keep the queue design on that card.

**Recap.**

- A throttle holds a short queue, or asks a producer you can reach to slow down.
- A reject returns 429 and stores nothing.
- Queue the job when the caller can wait and the queue has room.
- Reject a browser call, and reject again once the queue is full.
- A concurrency cap counts in-flight work. A rate limit counts how fast new work starts.

![Throttle or Reject](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-3-throttle-or-reject.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 3.*

## Token Bucket

**What it is.** A token bucket is a count of permits plus a refill rate. Each request takes one permit. The count never rises past a fixed capacity, so a quiet period saves at most one burst.

**Why it exists.** People and well-written clients send in bursts: a page load fires several calls, then goes quiet. A limiter that allows only a perfectly even rate refuses that normal burst. The bucket allows the burst, then falls back to the refill rate. Idle time cannot raise the burst above the capacity.

**How it works.** The teaching bucket holds 8 permits and gains 2 permits a second. It starts full. Ten requests arrive together: 8 take a permit and pass, and 2 are refused with 429 because the bucket is empty. A refused request does not take a permit. One second later the refill has put 2 permits back, so 2 more requests pass and a third is refused. The state you store is the current count and the time it was last updated. On the next request you add `rate × elapsed`, then cap at the capacity. The process stores the timestamp and updates the count on that request. Five quiet seconds from an empty bucket would add 10, and the cap leaves 8, so the next burst is 8 again.

```python
def refill(tokens: int, elapsed_s: int, capacity: int = 8, rate: int = 2) -> int:
    return min(capacity, tokens + elapsed_s * rate)


print(8, refill(0, 1), refill(0, 5))  # full, one second later, five quiet seconds
# 8 2 8
```

The worked example uses whole seconds, which matches the diagram. The same formula allows a fraction: half a second at 2 permits per second adds 1 permit.

**Trade-offs.** The burst is the feature, and it is also the risk. A full bucket dumps `capacity` requests onto the handler at once. Raise the capacity when the product needs a sharper burst, and lower it when the handler cannot absorb one. A leaky bucket, on the next card, turns the same burst into a steady departure. A fixed window is cheaper to explain and allows a larger spike at the window boundary.

**In an interview.** This is the usual default for an HTTP API that should tolerate a short burst, cap how much idleness is saved, and remember one bucket per caller. Say the two numbers out loud, capacity and refill rate, and say that the stored state is one count and a timestamp.

**Recap.**

- Capacity 8 is the largest burst. The refill is 2 permits each second.
- A full bucket lets 8 requests through. Two more pass one second later.
- Five quiet seconds from empty would add 10. The cap leaves the bucket at 8.
- Each caller stores one count and the time of the last refill.
- A refused request leaves the count unchanged.

![Token Bucket](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-4-token-bucket.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 4.*

## Leaky Bucket

**What it is.** A leaky bucket is a queue that drains at a fixed rate. Requests enter the queue, and a worker takes them out at a steady pace. The queue has a maximum depth. Arrivals past that depth are dropped at once.

**Why it exists.** Some work must arrive smoothly. A report planner, a webhook sender, or a payment capture worker that finishes 1 job a second falls behind when 15 jobs arrive in the same instant. The queue turns the burst into a departure of 1 per second, and the depth cap keeps the queue from growing without a bound.

**How it works.** The teaching queue drains at 1 request a second and holds 6. A burst of 15 arrives. Six wait in the queue. Nine are dropped immediately, because the queue is already full. The worker then takes one job each second, so the depth runs 6, 5, 4, 3, 2, 1, and the queue is empty 6 seconds after the burst. The last job waited the full 6 seconds.

A token bucket lets the burst through and refuses once the permits are gone. This queue holds the excess and releases it steadily, for as long as the queue has room. User-facing writes want the burst to succeed, so they stay on the token bucket. A planner that must see a smooth arrival uses this queue. The choice between waiting and refusing is Throttle or Reject.

Some write-ups use the name "leaky bucket" for a meter that only counts and refuses, with no queue. That meter behaves like a token bucket. This card means the finite queue that drains at a fixed rate. Say which one you mean.

**Trade-offs.** Callers see a smooth downstream rate, and they also see extra latency: the last accepted job waits `depth / drain rate`. A token bucket answers immediately with success or 429, and the handler then sees the whole burst. The queue costs memory for every waiting request. The token bucket costs one integer and a timestamp. Dropping the overflow is the same reject decision as a full throttle queue.

**In an interview.** Use the token bucket when a short burst should succeed, as with a user clicking through a page. Use this queue when the next stage has a fixed processing rate and can accept a short wait. Give the drain rate and the depth, and say what happens to the seventh request when the depth is 6.

**Recap.**

| | Token bucket | Leaky bucket (this card) |
| --- | --- | --- |
| Burst | Passes, up to the capacity, then 429 | Sits in a queue and leaves at a fixed rate |
| Overflow | Refused immediately | Dropped once the queue is full |
| Stored state | One count and a timestamp | The queued requests |
| Teaching numbers | 8 pass from a full bucket | 6 wait, 9 of 15 are dropped, empty after 6 seconds |
| Use it when | The caller needs the burst to succeed | The next stage needs a steady arrival |

![Leaky Bucket](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-5-leaky-bucket.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 5.*

## Fixed Window Counter

**What it is.** A fixed window counts requests inside a clock-aligned interval, then starts the next interval at zero. The usual interval in this example is one minute, and the limit is 20.

**Why it exists.** It is the smallest counter that enforces "N requests per minute." The key is the caller plus the minute. An increment whose new value is above 20 is refused, and the key expires when the minute is over. One integer per caller is easy to keep in Redis with `INCR` and an expiry.

**How it works.** Minute 12 and minute 13 are separate keys. Twenty requests that land in the last three seconds of minute 12 are allowed, because that window's count is 20. Twenty more that land in the first three seconds of minute 13 are allowed, because the new window starts at zero and its count is also 20. Across the edge the caller sent 40 requests in six seconds. Each window, read alone, stayed inside the rule. The boundary can carry two windows of traffic, so the spike is up to twice the limit.

With the Redis shape the diagram shows, you `INCR` the key and refuse when the result is greater than 20. The refused call has already incremented the counter. Remaining stays at 0 for the rest of the minute, which is what you want to display. Set the key to expire at the end of the minute so a quiet caller does not leave old keys behind. The next minute is a new key and starts at 0.

**Trade-offs.** The implementation is one integer, an increment, and an expiry. The cost is the seam: a client that watches the clock can send the full limit twice in a few seconds. That is acceptable when the handler can absorb a 2× spike and the product copy says "per minute" in clock minutes. Leave the fixed window when those few seconds matter. The next card closes the seam with either an exact log or a weighted estimate.

**In an interview.** Draw the two minutes and put 20 requests on each side of the line. Say that both windows allow their own count, and that the caller sent 40 in six seconds. Keep the fixed window when you say that spike is acceptable. Use a sliding window when the limit has to hold for any 60-second span, including the seconds that cross a clock minute.

**Recap.**

- The window is one clock minute. The next minute starts at 0. The limit is 20.
- Twenty at the end of minute 12 are allowed. Twenty at the start of minute 13 are allowed.
- The six seconds around the edge carry 40 requests, which is two windows of traffic.
- The key is the caller plus the minute. Increment it, refuse when the value passes 20, and expire it at the end of the minute.
- Keep this counter when a 2× spike at the boundary is acceptable.

![Fixed Window Counter](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-6-fixed-window-counter.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 6.*

## Sliding Window

**What it is.** A sliding window counts requests in the last 60 seconds, whichever clock minute they fell in. That closes the boundary seam of the fixed window. Two implementations live on this card: a log of timestamps, and a weighted pair of counts.

**Why it exists.** The fixed window can admit twice the limit in a few seconds that straddle the minute. A sliding measure counts the requests that are still inside the last minute, including the ones from the previous clock minute that have not aged out.

**How it works.** A sliding log stores the time of each request and counts the times still inside the last 60 seconds. The count matches the requests that arrived. The seam is gone. The cost is one timestamp per request per caller, and that list is the memory to avoid when the minute is busy.

A sliding counter keeps two numbers, the previous minute and the current minute, and weights the previous minute by the part that still falls inside the last 60 seconds. Twenty seconds into the new minute, the previous minute holds 24 and the current minute holds 9. The previous minute overlaps the last 60 seconds by 40 seconds, so the estimate keeps `24 × 40 / 60 = 16` of those requests and adds the 9 already counted. The weighted count is 25. A limit of 20 refuses the request.

```python
def weighted(prev: int, curr: int, elapsed: int, window: int) -> int:
    return prev * (window - elapsed) // window + curr


print(weighted(24, 9, 20, 60))
# 25
```

The figure is an estimate. It assumes the previous minute's requests were spread evenly. If all 24 arrived in the first 20 seconds of that minute, none of them are still inside the last 60 seconds, and the true count is 9. If all 24 arrived in the last 40 seconds, the true count is 33. The estimate says 25 either way. It stores two counts. The log stores every timestamp. Keep the previous minute's counter until the overlap ends, which is longer than the fixed window's expiry at the end of its own minute.

**Trade-offs.** The log is exact and grows with traffic. The weighted counter is small and can refuse a request the exact count would allow, or allow one the exact count would refuse. Integer division lands on a whole number in this example. At other elapsed times it truncates. A token bucket answers a different question, burst versus refill, and does not look back over a minute of history.

**In an interview.** Prefer the weighted counter unless the problem asks for an exact count. Walk the arithmetic: overlap fraction, times the previous count, plus the current count, compared with the limit. Mention that the result is an estimate so you are not claiming the log's accuracy at the counter's cost.

**Recap.**

| | Sliding log | Sliding counter |
| --- | --- | --- |
| Stores | Every timestamp in the last 60 seconds | The previous minute and the current minute |
| Accuracy | Exact | An estimate that assumes an even spread |
| At 20 seconds of a 60-second window | The timestamps still inside the window | `24 × 40 / 60 + 9 = 25`, which is over a limit of 20 |
| Pick it when | The problem requires an exact count | You want the usual interview answer |

![Sliding Window](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-7-sliding-window.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 7.*

## Distributed Rate Limiting

**What it is.** Distributed rate limiting is the same budget enforced by more than one server. A counter that lives in one server's memory is wrong for a caller whose next request lands on a different server.

**Why it exists.** An API gateway or a service tier has several instances behind a load balancer. Each instance can allow the full budget from its own memory, and together they allow a multiple of the limit. The counter has to be shared, or each server has to hold a share you are willing to see drift.

**How it works.** Three options cover the interview.

A shared counter, usually in Redis, is what every server updates. The total matches the requests that were admitted. Every request pays a network hop, and the store sits on the path. If Redis is down, you choose a failure mode: fail open and admit, or fail closed and refuse.

A local counter plus a periodic sync gives each server a share of the budget. The read stays on the server, which is fast. Until the next sync, the shares can add up past the limit. That overshoot is the drift you accept when a local decision is enough and the hop can wait.

Sticky routing sends one caller to the same server every time, so that server's counter is the caller's counter. The pin itself is Sticky Sessions (Session Affinity) in [Load Balancing](../04_Load_Balancing/). Callers who arrived first pile onto one server. A restart of that server drops the count it held, so the caller looks unused and receives a fresh budget.

The race is two servers updating the shared count in separate steps. One permit remains. Both servers read 1, both admit, and each then writes 0, the value it computed from the 1 it read. Two requests passed on one permit. Redis runs one command at a time, so a single `DECR`, or one script that reads, decides, and writes before another server runs, closes the gap. The script lets the first server take the permit and leaves the second looking at 0. A bare `DECR` from 1 returns 0 for the first server and `-1` for the second. Admit only a result that is still at least 0. A distributed lock, two-phase commit, and a consensus round stay in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). They coordinate a unit of work across records. This failure is one counter written in two steps. The timestamp list and its memory stay on Sliding Window.

GitHub documents a real version of a split count: because requests are handled in more than one region, `x-ratelimit-remaining` on a later response can be higher than on an earlier one inside the same window. Use the headers to slow down, and treat 403 and 429 as the decision. A client that assumes the remaining count ticks down by exactly one will mis-count across regions.

**Trade-offs.** The shared store is accurate and adds a dependency and a hop to every request. Local shares are fast and can overshoot until the next sync. Sticky routing needs no extra store and pins load to whichever server the caller hit first, and a restart forgets the usage. A lock around the counter would also stop the race, and it is a large mechanism for one integer. The atomic command is the repair that matches the size of the bug.

**In an interview.** Put the counter in Redis and update it with one atomic command or one script. Say the race in one sentence: two servers read 1 and both admit. Mention local shares or sticky routing as the options you would pick when a little overshoot is acceptable or when one server can own the caller. Leave locks, two-phase commit, and consensus on the transactions card.

**Recap.**

| Approach | What you gain | What it costs |
| --- | --- | --- |
| Shared store | The admitted total matches the requests | A hop on every request, and the store is on the path |
| Local count, synced on a timer | The read stays on the server | Shares can add up past the limit until the next sync |
| Sticky routing | One server owns the caller, so its counter is the budget | Load piles up, and a restart drops the count |
| Atomic decrement or one script | One permit admits one request | The counter store has to support that atomic step |

![Distributed Rate Limiting](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-8-distributed-rate-limiting.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 8.*
