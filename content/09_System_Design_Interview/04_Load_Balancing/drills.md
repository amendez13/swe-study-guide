# Load Balancing — Drills

Original practice for the balancer in front of a web tier. Each card is one exercise: commit to an answer, then check it. The numbers are invented for a parcel-locker pickup service. The shared session store, geo routing across sites, and gateway auth stay in their own topics.

## Public Address Stays

The pickup name resolves to `203.0.113.10`. The pool is three private web servers. You add `10.0.4.14`. Which address do clients still use, and how many servers are in the pool?

```python
PUBLIC = "203.0.113.10"
POOL = ["10.0.4.11", "10.0.4.12", "10.0.4.13"]
```

**Answer:** Clients still use `203.0.113.10`. The pool grows from 3 to 4. The new server is not a DNS change. Publishing each web server would turn every add, and every crash, into an address clients cache.

```python
PUBLIC = "203.0.113.10"
POOL = ["10.0.4.11", "10.0.4.12", "10.0.4.13"]


def add_server(pool: list[str], private_ip: str) -> tuple[str, int]:
    return PUBLIC, len(pool) + 1


print(*add_server(POOL, "10.0.4.14"))
# 203.0.113.10 4
```

## DNS Hold After a Failure

DNS is the only spreader, and it is handing out web-server addresses. The TTL is 90 seconds. A resolver cached the answer 20 seconds ago. One of those addresses dies. How many seconds can that resolver keep returning it? Separately, a balancer removes a server after 3 failed probes, 5 seconds apart, measured from the first failed probe. How many seconds is that?

```python
TTL_S = 90
AGE_S = 20
FAILS_REQUIRED = 3
PROBE_S = 5
```

**Answer:** The resolver can keep returning the dead address for 70 seconds. The balancer drops it 10 seconds after the first failed probe. DNS publishes a few stable public addresses. Membership of the web tier is the balancer's job. Which site the name should point at is Multi-DC and Geo Routing.

```python
TTL_S = 90
AGE_S = 20
FAILS_REQUIRED = 3
PROBE_S = 5

dns_hold_s = TTL_S - AGE_S
lb_remove_s = (FAILS_REQUIRED - 1) * PROBE_S
print(dns_hold_s, lb_remove_s)
# 70 10
```

## Path Needs Layer 7

`/pickup` belongs on the door pool. `/labels` belongs on the printer pool. What does a Layer 4 balancer do with `/labels`, and what does a Layer 7 balancer do with each path?

```python
ROUTES = {"/pickup": "doors", "/labels": "printers"}
```

**Answer:** Layer 4 sends `/labels` to the door pool. It can see the connection, not the path. Layer 7 sends `/labels` to the printers and `/pickup` to the doors, which requires the HTTP request in the clear on the balancer. Use Layer 4 to spread identical connections. Use Layer 7 when the path, host, or cookie selects the pool.

```python
ROUTES = {"/pickup": "doors", "/labels": "printers"}


def tier(mode: str, path: str) -> str:
    if mode == "l4":
        return "doors"
    return ROUTES[path]


print(tier("l4", "/labels"), tier("l7", "/labels"), tier("l7", "/pickup"))
# doors printers doors
```

## Worker CPU After Offload

Four web servers. Each has 1,000 ms of CPU each second. The handler costs 8 ms. TLS on the worker costs another 4 ms. The balancer has spare CPU in this exercise. What QPS can the workers finish if they terminate TLS, and what QPS if the balancer terminates and forwards HTTP?

```python
WORKERS = 4
CPU_MS = 1_000
APP_MS = 8
TLS_MS = 4
```

**Answer:** Terminating on the workers caps the tier at 333 QPS. Terminating on the balancer raises the workers to 500 QPS, and the certificate lives in one place, which is also what lets Layer 7 read the path. Re-encrypting to the web server puts the 4 ms back on the worker. Passthrough is that second case: the balancer never sees HTTP.

```python
WORKERS = 4
CPU_MS = 1_000
APP_MS = 8
TLS_MS = 4


def worker_qps(terminate_on_worker: bool) -> int:
    cost = APP_MS + (TLS_MS if terminate_on_worker else 0)
    return WORKERS * CPU_MS // cost


print(worker_qps(True), worker_qps(False))
# 333 500
```

## Round Robin on a Hot Server

Open door sessions are `[300, 40, 50]`. The round-robin cursor is on server 0. Where does the next connection go under round robin, and where under least connections?

```python
COUNTS = [300, 40, 50]
```

**Answer:** Round robin chooses server 0, which already holds 300 sessions. Least connections chooses server 1, which holds 40. Round robin evens out arrivals. It does not even out open work, so a server that accumulated long sessions stays hot. Use round robin when requests are short and similar, and weights when the machines differ in size.

```python
COUNTS = [300, 40, 50]


def round_robin(cursor: int) -> int:
    return cursor % len(COUNTS)


def least_connections() -> int:
    return min(range(len(COUNTS)), key=lambda i: COUNTS[i])


print(round_robin(0), least_connections())
# 0 1
```

## Failure Streak

`web-c` starts in the pool. Probes arrive as fail, fail, ok, fail, fail, fail. Three failures in a row remove a server. Which probe index removes it?

```python
PROBES = ["fail", "fail", "ok", "fail", "fail", "fail"]
REMOVE = 3
```

**Answer:** The ok at index 2 clears a streak of two, so those early failures leave `web-c` in the pool. Indexes 3, 4, and 5 are fail, fail, fail. Index 5 is the one that reaches three in a row and removes it. One blip must not eject a live server. A deep probe that fails whenever the shared database blips ejects every web server together. Membership stays on a shallow check the process can answer by itself.

```python
PROBES = ["fail", "fail", "ok", "fail", "fail", "fail"]
REMOVE = 3


def removed_at(probes: list[str]) -> int | None:
    streak = 0
    for index, probe in enumerate(probes):
        streak = streak + 1 if probe == "fail" else 0
        if streak >= REMOVE:
            return index
    return None


print(removed_at(PROBES))
# 5
```

## Sticky Cookie and a Dead Target

The cookie says `web-b`. Open sessions are web-a 5, web-b 40, web-c 8. Where does the next request go while `web-b` is healthy, and where once `web-b` is out? Three clients share the NAT address `10.9.9.2`, and one client uses `10.1.4.8`. Which IP-hash buckets do they land in, out of 3?

```python
POOL = {"web-a": 5, "web-b": 40, "web-c": 8}
COOKIE = "web-b"
```

**Answer:** While `web-b` is healthy the cookie wins, so the request stays on the server that holds 40 sessions. Once `web-b` is out, the cookie is ignored and least connections chooses `web-a`. The in-memory session on `web-b` does not come with it. Keeping the login is the shared session store on Scalability Fundamentals. All three NAT clients hash to bucket 0. The other client hashes to bucket 2. An IP pin piles a whole office onto one server, and a phone that changes address changes servers.

```python
POOL = {"web-a": 5, "web-b": 40, "web-c": 8}
COOKIE = "web-b"


def assign(down: set[str]) -> str:
    live = {name: count for name, count in POOL.items() if name not in down}
    if COOKIE in live:
        return COOKIE
    return min(live, key=lambda name: live[name])


def ip_bucket(ip: str, servers: int) -> int:
    return sum(int(part) for part in ip.split(".")) % servers


nat = ["10.9.9.2", "10.9.9.2", "10.9.9.2"]
print(assign(set()), assign({"web-b"}), [ip_bucket(ip, 3) for ip in nat], ip_bucket("10.1.4.8", 3))
# web-b web-a [0, 0, 0] 2
```

## Standby Takes the Address

Four web servers are healthy. The active balancer dies holding 50 requests. A passive standby takes the same public address. How many web servers are still up, how many of those 50 requests complete, and what happens to new requests if there is no standby?

```python
WEB_UP = 4
IN_FLIGHT = 50
```

**Answer:** All 4 web servers are still up. None of the 50 in-flight requests complete, because the process that had accepted them is gone. With a standby, new requests use the address once it moves. With one balancer, the web pool is healthy and has no public address. A second data center is a different failure domain. Say the pair out loud when the diagram shows one box.

```python
WEB_UP = 4
IN_FLIGHT = 50


def inflight_completed(in_flight: int, balancer_died: bool) -> int:
    if balancer_died:
        return 0
    return in_flight


def new_route(have_standby: bool) -> str:
    if have_standby:
        return "vip-moved"
    return "no-address"


print(WEB_UP, inflight_completed(IN_FLIGHT, True), new_route(True), new_route(False))
# 4 0 vip-moved no-address
```
