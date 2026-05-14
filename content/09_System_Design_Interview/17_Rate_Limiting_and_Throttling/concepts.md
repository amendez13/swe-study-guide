## Rate Limiter

Controls the rate of requests a client or service can make. Protects against abuse, prevents cascading overload, and enforces fair usage across tenants.

```text
Where to place it:
  Client-side:     cooperative throttling (unreliable — client can ignore it)
  API Gateway:     centralized, applies to all services behind the gateway
  Per-service:     each service enforces its own limits
  Middleware:       rate limiter as a library in the request pipeline

What to limit by:
  IP address        — simple, but shared IPs (NAT, VPN) cause false positives
  User ID / API key — accurate per-user throttling
  Endpoint           — different limits for /search (expensive) vs /health (cheap)
```

```text
Response when rate-limited:
  HTTP 429 Too Many Requests
  Retry-After: 30       ← tells client when to retry
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1710001200
```

## Token Bucket

Tokens accumulate in a bucket at a fixed rate. Each request consumes one token. If the bucket is empty, the request is rejected. Allows short bursts up to the bucket's capacity.

```text
Parameters:
  Rate:     10 tokens/second (refill rate)
  Capacity: 50 tokens (max burst size)

Timeline:
  t=0:  Bucket has 50 tokens. Burst of 50 requests → all pass.
  t=1:  10 tokens added. 10 requests pass.
  t=5:  50 tokens accumulated (capped at capacity).
        Another burst of 50 → all pass.

Characteristics:
  ✓ Allows bursts (good for bursty traffic patterns)
  ✓ Simple to implement (one counter + timestamp)
  ✓ Memory efficient (one bucket per client)
```

Token bucket is the most commonly used algorithm. AWS API Gateway, Stripe, and most cloud providers use it.

## Leaky Bucket

Requests enter a queue (bucket) that is processed at a fixed rate. If the queue is full, new requests are dropped. Smooths traffic to a constant rate.

```text
Parameters:
  Rate:     10 requests/second (drain rate)
  Capacity: 100 requests (queue size)

Behavior:
  Burst of 200 requests arrives.
  100 are queued (bucket is full).
  100 are dropped immediately.
  Queued requests drain at 10/sec → 10 seconds to clear.

Compared to token bucket:
  Token bucket: allows bursts, rejects when tokens exhausted.
  Leaky bucket: smooths bursts into steady flow, queues excess.

  Token bucket is better for APIs (users expect burst tolerance).
  Leaky bucket is better for network traffic shaping.
```

## Fixed Window Counter

Counts requests in fixed time windows (e.g., per minute). Simple to implement but allows burst at window boundaries.

```text
Example: limit 100 requests/minute

  Window [10:00 – 10:01]: 90 requests → OK
  Window [10:01 – 10:02]: starts at 0

Boundary problem:
  90 requests at 10:00:55 (end of window 1)
  90 requests at 10:01:05 (start of window 2)
  → 180 requests in 10 seconds, but both windows show < 100.
  The limit is effectively doubled at boundaries.

Implementation:
  Key: "rate:user42:202403151030" (minute-granularity)
  INCR key → if count > limit → reject
  EXPIRE key 60
```

Fixed window is fine for approximate rate limiting where the boundary burst is acceptable.

## Sliding Window

Two variants that solve the fixed window boundary problem at the cost of more complexity.

```text
Sliding Window Log:
  Store the timestamp of every request.
  On new request, count timestamps in the last N seconds.
  If count > limit → reject.
  + Exact, no boundary problem.
  - Memory heavy (stores every timestamp per user).

Sliding Window Counter (hybrid):
  Combine the current window count and the previous window count
  using a weighted average based on time elapsed in the current window.

  Example: limit 100/minute, current window is 40% elapsed.
    Previous window: 80 requests.
    Current window:  30 requests so far.
    Weighted count = 80 × 0.6 + 30 = 78 → under limit → allow.

  + Low memory (two counters per window per user).
  + Smooth, no boundary burst.
  - Approximate (but close enough for rate limiting).
```

Sliding window counter is the best balance of accuracy and efficiency. Use it as the default in interviews unless the problem specifically calls for exact counting.

## Distributed Rate Limiting

When rate limits must be enforced across multiple servers, each server needs access to shared counters. A single-server rate limiter doesn't work behind a load balancer.

```text
Approach 1 — Centralized counter (Redis):
  All servers INCR a shared Redis key per client.
  + Globally accurate counts.
  - Redis becomes a dependency and potential bottleneck.
  - Network latency for every request.

Approach 2 — Local counters with sync:
  Each server maintains local counters.
  Periodically sync to a central store.
  + Lower latency (local reads).
  - Temporarily over-limit (each server allows its share).

Approach 3 — Sticky routing:
  Route all requests from the same client to the same server.
  Local rate limiter is accurate for that client.
  + Simple, no shared state.
  - Uneven load distribution.
```

```text
Redis implementation (token bucket):
  local tokens = redis.call('GET', key)
  -- Calculate tokens to add based on elapsed time
  -- If tokens > 0: DECR and allow
  -- If tokens <= 0: reject
  -- Use Lua script for atomicity
```

In interviews, say "Redis-based distributed rate limiter" and move on — it's the standard answer and lets you focus on more interesting design decisions.
