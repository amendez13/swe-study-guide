## Rate Limiter

A rate limiter decides whether this caller may make another request right now, and it answers before the handler does the expensive work. One script paging through every record, or one client retrying in a tight loop, can occupy the API and slow everyone else. A per-caller budget stops one client from taking the whole service. A service that is out of capacity for every caller is a different decision, load shedding, covered with the Circuit Breaker Pattern and Graceful Degradation in [High Availability and Reliability](../03_High_Availability_and_Reliability/).

The limiter loads the caller's counter from a store the servers share, often Redis, and either allows the call or refuses it. The usual refusal is HTTP 429 Too Many Requests, and `Retry-After: 8` means wait 8 seconds. That header may instead be an HTTP date. `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` report the budget on every response, so a careful client slows down before it is refused. These names are a convention, and a 429 is valid without them. Real budgets differ. GitHub allows 5,000 requests an hour per personal access token and 60 an hour per IP for unauthenticated callers. It may refuse with 403 or 429, and its `x-ratelimit-reset` is a UTC epoch second. Stripe's live API allows 100 requests a second per account, and 25 a second in the sandbox and on many single endpoints. Its 429 carries `Stripe-Rate-Limited-Reason`. A 429 without that header can be an object lock timeout.

A client-side token bucket keeps a polite integration under budget, and Stripe recommends one, but a modified client skips it, so the server still enforces the limit. A budget over every public route belongs on the API Gateway in [Networking and Communication](../10_Networking_and_Communication/). A budget for one expensive route, such as search, belongs inside that service, so ordinary reads never spend it. Client waits and retry spread are Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). Scoping the caller and limit first is The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/), and the 429 chart is in [Observability](../25_Observability/).

```text
refusal       429, Retry-After, X-RateLimit-* headers
client pause  polite but skippable, the server enforces
gateway       a budget over every public route
service       a budget for one expensive route
full service  load shedding, a different decision
```

![Rate Limiter](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-1-rate-limiter.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 1.*

## Rate Limit Rules

A rate limit rule names the caller, the route, and the allowance, and that tuple is the counter key. Two rules can apply to one call, and the call has to pass both. A limit on the wrong key punishes the wrong people, and one shared counter lets a cheap route and an expensive route spend the same budget. GitHub's unauthenticated limit is keyed by IP, so everyone behind that address shares it, while an authenticated call counts against the user even after an IP change. Stripe caps each named operation on top of the account budget, so a flood of one operation leaves room for the rest.

An IP address is easy to read and a weak key. Twenty people on one cafe Wi-Fi share one public address through NAT, so one busy client gets the other nineteen refused. A phone that moves to cellular gets a new address and a fresh budget. A user id or API key counts the credential holder. It survives network changes but misses anonymous traffic, which still needs an IP key or it is unlimited. The route counts the work, and creating an issue costs differently from running search, so each route gets its own key. A new route ships uncapped until someone adds its rule.

A short rate and a longer quota can both apply. In the teaching budget, the write bucket holds 8 permits and refills 2 a second, with a quota of 500 writes a day beside it. A client that never bursts and sends at the refill rate reaches 500 in 250 seconds, and only the daily quota stops that steady scrape, at the cost of a second check per request. The expensive route has its own key, capped at 4 a minute. A cap on notifications sent to one person is a product rule, on Push Notification System in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).

```text
IP          no login needed, collapses a NAT, resets on new networks
user / key  follows the credential, misses anonymous calls
route       matches cost, new routes ship uncapped
rate+quota  8 burst at 2/s, plus 500 a day for the steady sender
```

![Rate Limit Rules](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-2-rate-limit-rules.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 2.*

## Throttle or Reject

Past the budget, the server either slows the work or refuses it. A throttle keeps the request waiting in a short queue, or tells a producer to send more slowly. A reject returns 429 and keeps no copy. Accepting every extra request fills the process with work it cannot finish, so the queue and memory grow, and requests that arrived on time wait behind ones that should have been turned away.

Hold an expensive job, such as a report rebuild, when the caller can wait and the queue has room. For a producer you can reach, such as your own worker, the throttle is a signal to slow down, which is Backpressure in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Queue depth and consumer scaling stay on that card. Reject a browser call, which can retry after `Retry-After`, and reject the next request once the queue is full. Stripe publishes the same split under two names. A rate limit counts how many requests start per second, and a concurrency limit counts how many are still in flight, 50 by default in live mode. A concurrency refusal is still a 429 and means too much is already running.

A short queue smooths a burst and adds latency up to its depth. An unbounded queue turns that latency into an outage. An immediate 429 keeps memory flat and pushes the retry decision to the client, which may retry badly. Slowing a producer you control wastes less than refusing a message you will only requeue, but that needs a channel back to the producer.

```text
throttle      short queue, or slow a producer you can reach
reject        429, nothing stored
caller waits  queue it, with a maximum depth
queue full    reject the next one
concurrency   counts in-flight work, rate counts new starts
```

![Throttle or Reject](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-3-throttle-or-reject.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 3.*

## Token Bucket

A token bucket is a count of permits plus a refill rate. Each request takes one permit, and the count never rises past a fixed capacity, so a quiet period saves at most one burst. People and well-written clients send in bursts, because a page load fires several calls and then goes quiet. A limiter that allows only a perfectly even rate refuses that normal burst. The bucket allows it, then falls back to the refill rate.

The teaching bucket holds 8 permits and gains 2 a second. It starts full. Ten requests arrive together: 8 take a permit, and 2 get 429 because the bucket is empty. A refused request takes nothing. One second later the refill has added 2, so 2 more pass and a third is refused. The stored state is the count and the time it was last updated. On each request, add `rate × elapsed`, cap at the capacity, then take a permit. Five quiet seconds from empty would add 10, the cap leaves 8, and the next burst is 8 again. Fractions work too, so half a second at 2 per second adds 1.

The burst is the feature and the risk, because a full bucket dumps `capacity` requests on the handler at once. Raise the capacity when the product needs a sharper burst, and lower it when the handler cannot absorb one. A leaky bucket turns the same burst into a steady departure. A fixed window is simpler and allows a bigger spike at its boundary. This is the usual default for an HTTP API. Say both numbers, capacity and refill, and that each caller stores one count and a timestamp.

```text
capacity 8    the largest burst
refill 2/s    two more pass one second later
5 s idle      would add 10, capped at 8
state         one count and a timestamp per caller
```

![Token Bucket](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-4-token-bucket.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 4.*

## Leaky Bucket

A leaky bucket is a queue that drains at a fixed rate. Requests enter the queue, a worker takes them out at a steady pace, and arrivals past the maximum depth are dropped at once. Some work must arrive smoothly. A report planner, webhook sender, or payment capture worker that finishes 1 job a second falls behind when 15 jobs arrive together. The queue turns the burst into 1 per second, and the depth cap keeps it bounded.

The teaching queue drains 1 request a second and holds 6. A burst of 15 arrives, 6 wait, and 9 are dropped because the queue is full. The worker takes one a second, so the depth runs 6, 5, 4, 3, 2, 1, and the queue is empty 6 seconds later. The last job waited the full 6 seconds, which is `depth / drain rate`. A token bucket lets the burst through and refuses once the permits are gone. This queue holds the excess and releases it steadily. User-facing writes want the burst to succeed, so they use the token bucket, and a planner that needs a smooth arrival uses this queue.

The smooth downstream rate costs latency and memory for every waiting request, while a token bucket costs one integer and a timestamp. Dropping the overflow is the same reject decision as a full throttle queue. Some write-ups use "leaky bucket" for a meter that only counts and refuses, with no queue. That behaves like a token bucket, so say which one you mean.

```text
drain 1/s, depth 6   15 arrive, 6 wait, 9 dropped
drained              empty after 6 seconds
token bucket         the burst passes, overflow gets 429
leaky bucket         the burst queues, leaves at a fixed rate
```

![Leaky Bucket](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-5-leaky-bucket.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 5.*

## Fixed Window Counter

A fixed window counts requests inside a clock-aligned interval, then starts the next interval at zero. Here the interval is one minute and the limit is 20. It is the smallest counter that enforces "N requests per minute." The key is the caller plus the minute, so one integer per caller fits in Redis with `INCR` and an expiry.

`INCR` the key and refuse when the result is above 20. The refused call has already incremented the counter, so remaining stays at 0 for the rest of the minute, which is what you want to display. Set the key to expire at the end of the minute so a quiet caller leaves no old keys. The next minute is a new key at 0.

The cost is the seam. Minute 12 and minute 13 are separate keys. Twenty requests in the last three seconds of minute 12 are allowed, and twenty more in the first three seconds of minute 13 are allowed too, because the new window starts at zero. The caller sent 40 in six seconds while each window stayed inside the rule. The boundary can carry up to twice the limit. Keep the fixed window when the handler can absorb a 2× spike and "per minute" means clock minutes. When the limit has to hold for any 60-second span, use a sliding window.

```text
key           caller + minute, INCR, refuse above 20, expire at minute end
minute 12     20 in the last 3 s, allowed
minute 13     20 in the first 3 s, allowed
the seam      40 in 6 s, up to 2x the limit
```

![Fixed Window Counter](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-6-fixed-window-counter.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 6.*

## Sliding Window

A sliding window counts requests in the last 60 seconds, whichever clock minute they fell in. That closes the fixed window's seam, where twice the limit can pass in the seconds around a minute boundary. There are two ways to build it. A sliding log stores the time of every request and counts the ones still inside the last 60 seconds. It is exact, and it costs one timestamp per request per caller, which is the memory to avoid when the minute is busy.

A sliding counter keeps two numbers, the previous minute and the current one, and weights the previous minute by how much of it still falls in the window. Twenty seconds into the new minute, the previous minute holds 24 and the current holds 9. The previous minute overlaps the last 60 seconds by 40 seconds, so the estimate is `24 × 40 / 60 + 9 = 16 + 9 = 25`, and a limit of 20 refuses the request. Keep the previous minute's counter until its overlap ends, which is longer than a fixed window's expiry.

The figure is an estimate that assumes the previous minute's requests were spread evenly. If all 24 came in its first 20 seconds, the true count is 9. If they all came in its last 40 seconds, it is 33. The estimate says 25 either way, so it can refuse a request the exact count would allow, or allow one it would refuse. Integer division truncates at other elapsed times. The weighted counter is the usual interview answer unless the problem demands an exact count, and you should say it is an estimate. A token bucket answers a different question, burst versus refill.

```text
sliding log      every timestamp, exact, memory grows
sliding counter  previous x overlap + current
at 20 s          24 x 40/60 + 9 = 25, over a limit of 20
caveat           assumes an even spread, true count 9 to 33
```

![Sliding Window](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-7-sliding-window.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 7.*

## Distributed Rate Limiting

Distributed rate limiting is the same budget enforced by more than one server. A gateway or service tier runs several instances behind a load balancer. If each one counts in its own memory, each allows the full budget, and together they allow a multiple of the limit. The counter has to be shared, or each server holds a share you accept will drift.

A shared counter, usually in Redis, keeps the admitted total accurate, and it costs a network hop on every request with the store on the path. If Redis is down, choose to fail open and admit, or fail closed and refuse. A local counter with a periodic sync gives each server a share, so reads stay local and fast, and the shares can add up past the limit until the next sync. Sticky routing sends a caller to the same server every time, so that server's counter is the budget. It needs no store, but load piles onto whichever server callers hit first, and a restart forgets the count and hands out a fresh budget. The pin is Sticky Sessions (Session Affinity) in [Load Balancing](../04_Load_Balancing/).

The race comes from updating the shared count in two steps. One permit remains, both servers read 1, both admit, and each writes 0, so two requests passed on one permit. Redis runs one command at a time, so a single `DECR` or one read-decide-write script closes the gap. With a bare `DECR` from 1, the first server gets 0 and the second gets `-1`, so admit only results of at least 0. A lock would work too, but it is a large mechanism for one integer, and locks, two-phase commit, and consensus stay in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). GitHub handles requests in more than one region, so `x-ratelimit-remaining` can go up between responses in the same window. Clients should treat the headers as a hint and 403 or 429 as the decision.

```text
shared store   accurate, a hop per request, fail open or closed
local + sync   fast, can overshoot until the next sync
sticky         one server owns the caller, a restart forgets
the race       two servers read 1, both admit
the fix        one atomic DECR or script, admit only >= 0
```

![Distributed Rate Limiting](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting-8-distributed-rate-limiting.png)

*Source: [`diagrams/rate-limiting.drawio`](/content/09_System_Design_Interview/17_Rate_Limiting_and_Throttling/diagrams/rate-limiting.drawio), page 8.*
