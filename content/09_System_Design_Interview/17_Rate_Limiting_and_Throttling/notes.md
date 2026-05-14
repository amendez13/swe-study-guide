# Rate Limiting and Throttling

How to control the rate of requests to protect a system from abuse, overload, and cascading failures. Rate limiting is a common system design interview question on its own ("Design a rate limiter") and a building block in almost every other design ("How do you prevent abuse?").

## Key Points

- **Rate limiter** — controls request rate per client, endpoint, or service. Returns HTTP 429 with Retry-After header. Place at the API gateway for centralized enforcement.
- **Token bucket** — tokens accumulate at a fixed rate, requests consume tokens. Allows bursts up to bucket capacity. Most commonly used algorithm (AWS, Stripe).
- **Leaky bucket** — requests enter a fixed-rate drain queue. Smooths traffic but queues requests. Better for network shaping than APIs.
- **Fixed window counter** — counts per time window. Simple but allows double the limit at window boundaries.
- **Sliding window** — log (exact, memory-heavy) or counter (approximate, efficient). Sliding window counter is the best default for interviews.
- **Distributed rate limiting** — shared Redis counters for globally accurate limits across multiple servers. Lua scripts for atomic operations.

## Example

Designing a rate limiter for a public API:

```text
Requirements:
  100 requests/minute per API key
  1,000 requests/minute per IP (for unauthenticated requests)
  Different limits per endpoint: /search = 20/min, /upload = 5/min

Algorithm: Sliding window counter (accurate, low memory)

Architecture:
  Client → API Gateway → Rate Limiter Middleware → Service

  Rate limiter checks Redis:
    Key: "rate:{api_key}:{endpoint}:{window}"
    Example: "rate:key_abc:search:202403151030"

  Lua script (atomic):
    prev_count = GET("rate:key_abc:search:202403151029") or 0
    curr_count = INCR("rate:key_abc:search:202403151030")
    EXPIRE("rate:key_abc:search:202403151030", 120)
    elapsed = current_second / 60  -- fraction of current window
    weighted = prev_count * (1 - elapsed) + curr_count
    if weighted > 20 then REJECT end

Response headers on every request:
  X-RateLimit-Limit: 20
  X-RateLimit-Remaining: 14
  X-RateLimit-Reset: 1710001260

On rejection:
  HTTP 429 Too Many Requests
  Retry-After: 35
  Body: { "error": "Rate limit exceeded. Try again in 35 seconds." }
```

The design handles per-key, per-IP, and per-endpoint limits using the same sliding window counter mechanism with different Redis key patterns.
