# Observability

How you see and change a fleet after it no longer fits on one machine. Logs say what one request did. Metrics say whether a tier or the business is drifting. Automation makes the build you tested the build that runs in every data center. A handful of servers can skip all three. A large fleet cannot.

## Key Points

- **Per-server logs** — the line lives on the host that handled the request. Enough while you can name that host.
- **Centralized logs** — ship a structured line to one searchable store. Sample successes, keep errors, and leave secrets out of the line.
- **Error logs** — the failure path records the request, the host, and the cause. A 500 with no line is a missing log.
- **Host metrics** — CPU, memory, disk, and network on one box. A hot singleton is a page. A hot member of a large pool is a replacement.
- **Tier metrics** — rate, errors, and latency rolled up by service. Page the tier against the SLO, not the busiest host's CPU.
- **Business metrics** — completed work the product promised. A flat HTTP 200 chart can hide a product that stopped doing the thing.
- **Continuous integration** — build and test on check-in. Only a green artifact may be deployed.
- **Repeatable deploys** — one artifact to every host and every data center. A small group ships by promoting that artifact. Rollback points the pipeline at the previous artifact id.
- **Fleet growth** — the same three practices are optional on a few servers and required once inspection by hand is slower than the user. Tracing, error-budget policy, and alert routing stay neighbors of this topic.

## Example

A bike-share unlock tier: three docks, one quiet minute, and a 99.9% window that has already recorded some failures. The helpers use integer arithmetic. They stand in for a collector, not for one.

```python
def tier_error_rate(hosts: list[dict[str, int]]) -> float:
    requests = sum(host["requests"] for host in hosts)
    errors = sum(host["errors"] for host in hosts)
    if requests == 0:
        return 0.0
    return errors / requests


def remaining_error_budget(requests: int, failures: int) -> int:
    """99.9% SLO: 1 failed request allowed per 1,000."""
    allowed = requests // 1_000
    return allowed - failures


docks = [
    {"requests": 4_000, "errors": 12},
    {"requests": 4_100, "errors": 9},
    {"requests": 3_900, "errors": 11},
]
print(round(tier_error_rate(docks), 5))
print(remaining_error_budget(50_000_000, 18_400))
# 0.00267
# 31600
```

32 errors out of 12,000 requests is about 0.27%. That minute is hotter than a 0.1% budget rate even though no dock is down. Against 50 million requests, 18,400 failures already spent leave 31,600 failures inside a 99.9% window. The page is the tier error rate and completed unlocks, not one dock's CPU.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — the wrap-up is where you name the metric you would alert on.
- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — the stage that introduces logs, metrics, and automation. That stage stays a pointer. The design is here.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — nines, MTTR, and SLO, SLI, and SLA. This topic reads the SLI. It does not pick a new target.
