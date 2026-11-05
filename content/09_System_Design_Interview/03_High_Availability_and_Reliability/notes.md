# High Availability and Reliability

How to design systems that stay up when things break — and things always break. Availability is measured in nines, improved through redundancy and fast recovery, and formalized through SLOs. A second data center is the same idea at site scale: latency, disaster, or residency, with a routing choice and a replication cost attached. Reducing recovery time (MTTR) is almost always more practical than preventing every failure (MTBF).

## Key Points

- **Availability and the nines** — 99.9% (three nines) allows ~8.7 hours downtime/year. Components in series multiply; copies in parallel raise availability.
- **MTBF and MTTR** — Availability = MTBF / (MTBF + MTTR). Automated failover, health checks, and fast rollbacks cut MTTR.
- **Redundancy and replication** — extra copies inside one site: app servers, databases, network paths. Cost scales with the copy count.
- **Failover strategies** — cold (slow, cheap), warm (moderate, common), hot (fast, expensive). Warm standby with automated failover is the usual single-site answer.
- **Active-active vs. active-passive** — one writer and a spare, or every instance serving. Stateless services default to active-active; databases default to active-passive.
- **Multi-DC and geo routing** — a second site for latency, disaster, or residency. Geo DNS and a traffic manager choose the site. A sync write waits out the cross-site round trip; an async write can lose the lag window. A charge fails closed; a catalog can answer from the local copy.
- **SLA, SLO, SLI** — SLI is the metric, SLO is the internal target, SLA is the customer contract. The SLO decides whether a second site is required.
- **Graceful degradation** — serve reduced functionality rather than failing completely. Show trending content when the recommendation engine is down.
- **Circuit breaker pattern** — stop calling a failing service after a threshold; short-circuit to a fallback. Prevents cascading failures across the call chain.

## Example

Calculating required redundancy from an availability target:

```text
Requirement: 99.99% availability (4 nines)
Single server availability: 99.9% (measured from historical data)

Single server:
  99.9% = 8.77 hours downtime/year → does not meet 99.99%

Two servers (active-passive, automated failover):
  Unavailable only when BOTH are down simultaneously.
  P(both down) = 0.001 × 0.001 = 0.000001
  Availability = 1 - 0.000001 = 99.9999% → exceeds 99.99% ✓

  But failover takes ~30 seconds. Assume 10 failovers/year.
  Actual downtime = 10 × 30s = 5 min/year.
  Availability ≈ 99.999% → still meets 99.99% ✓

Cost: 2× infrastructure for the redundant pair.
Decision: worth it for a 99.99% SLO.
```

That pair still shares one site. A region-level failure needs a second site, and the write has to say whether it waits:

```python
LOCAL_COMMIT_MS = 5
CROSS_SITE_RTT_MS = 80

CLOSED = {"charge", "reserve", "transfer"}


def commit_ms(wait_for_other_site: bool) -> int:
    if wait_for_other_site:
        return LOCAL_COMMIT_MS + CROSS_SITE_RTT_MS
    return LOCAL_COMMIT_MS


def answer(op: str, other_site_reachable: bool) -> str:
    if op in CLOSED and not other_site_reachable:
        return "503"
    if op in CLOSED:
        return f"ok {commit_ms(True)}ms"
    return "local-copy"


print(commit_ms(True), answer("charge", False), answer("catalog", False))
# 85 503 local-copy
```

The charge pays 85 ms when both sites are up, and it fails closed when they are split. The catalog keeps serving the local copy. Feature fallbacks inside one site stay on the graceful-degradation card. Connecting the availability target to a concrete redundancy decision, including whether that redundancy is a spare process or a second site, is the interview move.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — the zero-to-millions stage that names multiple data centers. The card is here.
- [Observability](../25_Observability/) — one artifact in every data center, and the tier metrics you compare to the SLO.
- [Content Distribution and Media](../22_Content_Distribution_and_Media/) — edges for shared bytes. A CDN is a different box from a second site that accepts writes.
- [Consistency and Replication](../09_Consistency_and_Replication/) — lag, quorums, and conflicting writes once two sites both accept them.
- [Load Balancing](../04_Load_Balancing/) — per-request balancing after a site has been chosen.
