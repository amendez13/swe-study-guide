# Interview Framework and Process

How to structure and drive a system design interview from the first question to the wrap-up. Interviewers grade the process along with the design: a simpler architecture that is scoped, estimated, and wrapped up beats a larger drawing that never agreed the problem.

## Key Points

- **Four-step framework** — understand & establish scope (3–5 min), propose high-level design & get buy-in (10–15 min), design deep dive (15–20 min), wrap up (3–5 min). Drive the transitions yourself.
- **Time allocation** — protect the deep dive. When the clock slips, shorten the high-level tour, keep a single deep dive, and still leave 3–5 minutes to talk about failure.
- **Functional vs. non-functional requirements** — functional is what the system does; non-functional is how well (latency, availability, durability, cost). Gather both before drawing.
- **Scope management** — state the cut list. Depth on one or two hard problems is the goal; deferred boxes should be named, not forgotten silently.
- **Back-of-the-envelope estimation** — round, keep units, and separate reads, writes, and bytes. Peak for human traffic is about 2–5× average. 2^10 through 2^50 are the KB-to-PB milestones. A year at 99% / 99.9% / 99.99% / 99.999% allows about 3.65 days, 8.76 hours, 52.6 minutes, and 5.26 minutes of downtime.
- **Latency ladder** — L1 ~1 ns, RAM ~100 ns, SSD random read ~100 μs, same-datacenter RTT ~0.5 ms, HDD seek ~10 ms, cross-continent RTT ~150 ms. Design the hop that dominates the budget.
- **Estimation habits** — users are not QPS; write actions per user per day. Recompute at 10× and stop when the architecture stops changing.
- **QPS and storage estimate** — DAU × actions / 10^5 seconds → QPS; DAU × writes × 365 × bytes → storage. Label every multiplier (peak, indexes, replicas).
- **Working backwards** — user needs → API contract → services → data model → technology, then get buy-in before the deep dive.
- **API contract** — a few endpoints make pagination, ids, and sync-vs-async visible while the diagram is still cheap to change.
- **Deep-dive focus** — pick the data model, the hot path, consistency, or the algorithm that would miss the agreed requirement if it stayed naive. Say what you are leaving on the sketch.
- **Trade-off articulation** — name the cost of the choice (consistency vs. availability, read latency vs. write latency, cost vs. durability) on the specific decision, not as a slogan.
- **Wrap-up checklist** — single points of failure, the first bottleneck at 10×, metrics you would alert on, security, cost, and one extension.

## Example

A tool-lending co-op: 5 million daily active members, 2 loan records written and 12 records read per member per day, 400 bytes per record, 3 years of retention, peak at 4×. The helper uses the interview shortcut of 10^5 seconds/day.

```python
SECONDS_PER_DAY = 100_000  # shortcut; a true day is 86_400 s (~15% higher QPS)


def estimate_load(
    dau: int,
    writes_per_user: float,
    reads_per_user: float,
    record_bytes: int,
    years: float,
    peak_factor: float,
) -> dict[str, float]:
    write_qps = dau * writes_per_user / SECONDS_PER_DAY
    read_qps = dau * reads_per_user / SECONDS_PER_DAY
    bytes_per_year = dau * writes_per_user * 365 * record_bytes
    return {
        "write_qps_avg": write_qps,
        "write_qps_peak": write_qps * peak_factor,
        "read_qps_avg": read_qps,
        "read_qps_peak": read_qps * peak_factor,
        "tb_per_year": bytes_per_year / 1e12,
        "tb_retained_raw": bytes_per_year * years / 1e12,
    }


coop = estimate_load(5_000_000, 2, 12, 400, 3, 4)
indexed_tb = coop["tb_retained_raw"] * 2  # assumption: indexes about double raw bytes
print(coop)
print(f"indexed_tb={indexed_tb:.1f}")
```

That prints 100 average write QPS (400 peak), 600 average read QPS (2,400 peak), 1.46 TB/year, 4.38 TB raw over 3 years, and 8.8 TB once indexes are budgeted at 2×. Say the conclusion before you draw: one primary, a replica, and a cache. A full replica copies the disk again; name that multiplier if the interviewer asks about durability. Then ask anything you still need (custom loan names, expiry, search) and sketch only the path this estimate justified.

## See also

- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — describing load once the estimate exists: QPS, read/write mix, and what you do when one machine is no longer enough.
- [High Availability and Reliability](../03_High_Availability_and_Reliability/) — downtime per month, and how components in series or parallel change the nines.
