# Content Distribution and Media — Drills

Original practice for placing a CDN, setting a TTL, purging, and estimating media cost. Each card is one exercise: commit to an answer, then check it. The numbers are invented.

## Shared photo or private JSON

For each object, say whether it belongs on a CDN, in the application cache, or only at the origin.

```python
items = [
    {"name": "product photo", "shared": True, "regions": 6, "reusable": True},
    {"name": "profile json", "shared": False, "regions": 6, "reusable": True},
    {"name": "checkout total", "shared": False, "regions": 6, "reusable": False},
    {"name": "local brochure", "shared": True, "regions": 1, "reusable": True},
]
```

**Answer:** The product photo is shared across six regions, so it goes on the CDN. Profile JSON is reused but private, so it stays in the application cache from Caching. The checkout total is not reusable. The brochure is shared, but every reader is already in the origin's region, so an application cache is enough until a second region shows up.

```python
def home(item: dict) -> str:
    if not item["reusable"]:
        return "origin only"
    if item["shared"] and item["regions"] > 1:
        return "cdn"
    return "app cache"


items = [
    {"name": "product photo", "shared": True, "regions": 6, "reusable": True},
    {"name": "profile json", "shared": False, "regions": 6, "reusable": True},
    {"name": "checkout total", "shared": False, "regions": 6, "reusable": False},
    {"name": "local brochure", "shared": True, "regions": 1, "reusable": True},
]
print([home(item) for item in items])
# ['cdn', 'app cache', 'origin only', 'app cache']
```

## TTL, edges, and a shield

100,000 hot objects sit on 40 edges. Each edge refreshes an object once per TTL. What is the origin fetch rate at a 1-hour TTL, at a 1-minute TTL, and at a 1-hour TTL with an origin shield? If the edges together see 80,000 requests/s, what is the hit ratio at the 1-hour TTL without a shield?

```python
OBJECTS = 100_000
EDGES = 40
REQUESTS_PER_SEC = 80_000
```

**Answer:** Without a shield the origin sees one fetch per edge per TTL: about 1,111/s at one hour, and about 66,667/s at one minute. The shield collapses 40 copies into one, so the hour-long TTL falls to about 28 origin fetches/s. At 80,000 requests/s the unshielded hour-long misses are a 0.986 hit ratio. Shortening the TTL by 60 multiplies origin load by 60. The shield is the other lever, and it does not change the TTL the user observes.

```python
def origin_fetches_per_sec(objects: int, edges: int, ttl_seconds: float, shield: bool) -> float:
    copies = 1 if shield else edges
    return objects * copies / ttl_seconds


def hit_ratio(requests_per_sec: float, misses_per_sec: float) -> float:
    if requests_per_sec <= 0:
        return 0.0
    return max(0.0, 1.0 - misses_per_sec / requests_per_sec)


OBJECTS = 100_000
EDGES = 40
hour = origin_fetches_per_sec(OBJECTS, EDGES, 3600, False)
minute = origin_fetches_per_sec(OBJECTS, EDGES, 60, False)
shielded = origin_fetches_per_sec(OBJECTS, EDGES, 3600, True)
print(round(hour, 1), round(minute, 1), round(shielded, 1))
print(round(hit_ratio(80_000, hour), 4))
# 1111.1 66666.7 27.8
# 0.9861
```

## Public response or a private one

Which of these responses may be stored at the edge?

```python
samples = [
    {"cache_control": "public, s-maxage=86400"},
    {"cache_control": "private, max-age=60", "cookie_session": True},
    {"cache_control": "no-store", "authorization": "Bearer x"},
    {"cache_control": "max-age=30"},
]
```

**Answer:** Only the public object with `s-maxage` is an edge candidate. A session cookie means the next caller is a different user, so `private` stays off the edge even though the browser may keep it for 60 seconds. `no-store` plus `Authorization` is never stored. `max-age` alone tells a browser a lifetime and does not grant the shared cache permission, so the edge bypasses it until the response says `public` or `s-maxage`.

```python
def edge_decision(headers: dict) -> str:
    if headers.get("authorization") or headers.get("cookie_session"):
        return "bypass"
    cache_control = headers.get("cache_control", "")
    if "private" in cache_control or "no-store" in cache_control:
        return "bypass"
    if "public" in cache_control or "s-maxage" in cache_control:
        return "edge"
    return "bypass"


samples = [
    {"cache_control": "public, s-maxage=86400"},
    {"cache_control": "private, max-age=60", "cookie_session": True},
    {"cache_control": "no-store", "authorization": "Bearer x"},
    {"cache_control": "max-age=30"},
]
print([edge_decision(headers) for headers in samples])
# ['edge', 'bypass', 'bypass', 'bypass']
```

## Hashed name or a purge

You are publishing three kinds of object. What do you do to the URL and the TTL?

```python
kinds = ["hashed-asset", "stable-url", "cart"]
```

**Answer:** A content-hashed asset gets a new URL and a TTL of days, and you do not purge. A stable URL such as `/terms` keeps its name, you purge that one URL, and a short TTL covers a PoP that missed the purge. A cart is not an edge object at all.

```python
def publish(kind: str) -> str:
    if kind == "hashed-asset":
        return "new URL, TTL days, no purge"
    if kind == "stable-url":
        return "same URL, purge that URL, short TTL"
    return "do not cache"


kinds = ["hashed-asset", "stable-url", "cart"]
print([publish(kind) for kind in kinds])
# ['new URL, TTL days, no purge', 'same URL, purge that URL, short TTL', 'do not cache']
```

## A day of image egress

200 million image requests in a day, 80 KB average, 92% served from the edge. Edge egress is $0.01/GB and origin egress is $0.05/GB. What is the day's bill, and what would it be if every byte came from the origin?

```python
REQUESTS = 200_000_000
BYTES = 80_000
HIT = 0.92
EDGE_PER_GB = 0.01
ORIGIN_PER_GB = 0.05
```

**Answer:** The catalog moves 16,000 GB. The edge share costs $147.20 and the 8% origin share costs $64.00, so the day is $211.20. All-origin egress would be $800. The 92% hit ratio is doing the saving. Raising the hit ratio further is a TTL and a hot-set choice, not a second copy of the cold images on every PoP.

```python
REQUESTS = 200_000_000
BYTES = 80_000
HIT = 0.92
EDGE_PER_GB = 0.01
ORIGIN_PER_GB = 0.05

total_gb = REQUESTS * BYTES / 1e9
edge_cost = total_gb * HIT * EDGE_PER_GB
origin_cost = total_gb * (1 - HIT) * ORIGIN_PER_GB
all_origin = total_gb * ORIGIN_PER_GB
print(round(total_gb), round(edge_cost, 2), round(origin_cost, 2), round(edge_cost + origin_cost, 2), round(all_origin, 2))
# 16000 147.2 64.0 211.2 800.0
```

## A smaller rendition

One million viewers each watch 10 minutes. Compare bytes and edge cost at $0.02/GB for a 5 Mbps rendition and a 1 Mbps rendition.

```python
VIEWS = 1_000_000
SECONDS = 600
EDGE_PER_GB = 0.02
```

**Answer:** 5 Mbps is 375,000 GB and $7,500. 1 Mbps is 75,000 GB and $1,500. Adaptive bitrate exists so a viewer who cannot sustain 5 Mbps takes the smaller rendition instead of stalling, and the bill follows the bytes. The CDN price does not change. The codec and the ladder do.

```python
def watched_gb(mbps: float, seconds: int, views: int) -> float:
    return mbps * 1_000_000 / 8 * seconds * views / 1e9


VIEWS = 1_000_000
SECONDS = 600
EDGE_PER_GB = 0.02
hi = watched_gb(5, SECONDS, VIEWS)
lo = watched_gb(1, SECONDS, VIEWS)
print(round(hi), round(lo), round(hi * EDGE_PER_GB, 2), round(lo * EDGE_PER_GB, 2))
# 375000 75000 7500.0 1500.0
```
