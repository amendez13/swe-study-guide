# Load Balancing

The box that makes a horizontal web tier reachable. It publishes one address, chooses a healthy server, and can terminate TLS so the web tier sees HTTP. A single balancer is a failure domain, so the production drawing is a pair or a managed service that is already a pair.

## Key Points

- **What it does** — spreads requests across a pool, stops sending new work to a dead server, and lets you add a server without changing the client.
- **In front of the web tier** — clients use the balancer's public address. Web servers stay on private addresses.
- **DNS-level balancing** — several addresses for one name, cached for the TTL, with no per-request health check. Publish the balancers. Let the balancer pick the web server.
- **Layer 4 vs. Layer 7** — L4 routes on address and port and keeps a connection on one server. L7 routes on path, host, and cookie, and needs the HTTP bytes in the clear.
- **TLS termination** — the certificate lives on the balancer, the web tier spends CPU on the handler, and Layer 7 can read the request. Passthrough and re-encrypt keep TLS on the web server.
- **Algorithms** — round robin for similar short requests, weights for different machine sizes, least connections for long-lived work, IP hash and consistent hashing when the same key should stick.
- **Health checks** — active probes, passive error counts, a shallow check for membership. Drain a server before a deploy.
- **Sticky sessions** — cookie, client IP, or header. The pin keeps an in-memory session on one process. The shared session store is the durable fix.
- **One balancer** — active-passive with a floating address, active-active with headroom, or a managed balancer. In-flight work on the dead balancer is lost.

## Example

A parcel-locker pickup tier. Three web servers, open door sessions, and a cookie that names `web-b`. Unpinned, least connections chooses the quietest live server. If that cookie's server has failed its health check, the pin is ignored.

```python
def pick_door(pool: dict[str, int], failed: set[str], cookie: str | None) -> str:
    """Least connections, honoring a sticky cookie only while that server is live."""
    live = [name for name in pool if name not in failed]
    if cookie in live:
        return cookie
    return min(live, key=lambda name: pool[name])


doors = {"web-a": 420, "web-b": 90, "web-c": 110}
print(pick_door(doors, set(), None), pick_door(doors, {"web-b"}, "web-b"))
# web-b web-c
```

`web-b` holds 90 sessions and wins the unpinned pick. After it leaves the pool, the cookie no longer saves it, and `web-c` (110) wins over `web-a` (420). Round robin would have kept offering whatever was next in line, including a server already holding hundreds of long-lived door sessions. The session document that should survive `web-b` restarting lives in the shared session store.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — the horizontal web tier, and the shared session store. How the pin is implemented stays here.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — a second site and geo routing, after a site has been chosen. The balancer pair inside one site stays here.
- [Networking and Communication](../10_Networking_and_Communication/) — reverse proxy and API gateway. Those terminate TLS too, and the gateway also authenticates and fans out.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — the hash ring, when an algorithm card needs keys to move in a small slice.
