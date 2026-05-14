# High Availability and Reliability

How to design systems that stay up when things break — and things always break. Availability is measured in nines, improved through redundancy and fast recovery, and formalized through SLAs. The core insight is that reducing recovery time (MTTR) is almost always more practical than preventing all failures (MTBF).

## Key Points

- **Availability and the nines** — 99.9% (three nines) allows ~8.7 hours downtime/year. Composite availability for serial components multiplies; parallel components (redundancy) push availability higher.
- **MTBF and MTTR** — Availability = MTBF / (MTBF + MTTR). Reducing MTTR through automated failover, health checks, and fast rollbacks is usually more effective than trying to eliminate failures.
- **Redundancy and replication** — run multiple copies at every layer: app servers, databases, network paths, regions. Cost scales linearly with replica count.
- **Failover strategies** — cold (slow, cheap), warm (moderate, common), hot (fast, expensive). Most interview designs use warm standby with automated failover.
- **Active-active vs. active-passive** — active-passive is simpler (one writes, one waits); active-active uses resources better but requires conflict resolution. Stateless services default to active-active; databases default to active-passive.
- **SLA, SLO, SLI** — SLI is the metric, SLO is the internal target, SLA is the customer contract. Tie architecture decisions to the SLO.
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

This kind of reasoning — connecting the availability target to concrete redundancy decisions — is exactly what interviewers look for.
