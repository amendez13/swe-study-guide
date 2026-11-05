# Interview Framework and Process — Drills

Original practice for pacing, choosing a deep dive, and capacity math. Each card is one exercise: commit to an answer, then check it. The numbers are invented for study.

## Daily actions to QPS

A museum audio guide has 3 million daily active visitors. Each visitor plays 25 clips. Using 10^5 seconds/day and a weekend peak of 5×, what are average and peak play QPS?

```python
DAU = 3_000_000
PLAYS_PER_VISITOR = 25
PEAK = 5
SECONDS = 100_000
```

**Answer:** Average 750 QPS and peak 3,750 QPS. These are reads of clip metadata or media, and 5× is the top of the usual 2–5× band because the prompt piles traffic onto weekends.

```python
DAU = 3_000_000
PLAYS_PER_VISITOR = 25
PEAK = 5
SECONDS = 100_000

avg = DAU * PLAYS_PER_VISITOR / SECONDS
print(avg, avg * PEAK)  # 750.0 3750.0
```

## A year of sensor rows

80,000 weather stations write one 120-byte row every 10 minutes. Retain 2 years. How much raw storage is that, and what is the average write QPS using 10^5 seconds/day?

```python
STATIONS = 80_000
ROW_BYTES = 120
MINUTES = 10
YEARS = 2
SECONDS = 100_000
```

**Answer:** About 1.0 TB raw over two years, and about 115 write QPS on average. That is one database volume with room to spare, before indexes or replicas. Steady ingest is the write-path number; a storm may burst above it, and you would apply a peak factor only after you say so.

```python
STATIONS = 80_000
ROW_BYTES = 120
ROWS_PER_DAY = 24 * (60 // 10)  # 144
SECONDS = 100_000

rows_per_day = STATIONS * ROWS_PER_DAY
tb_two_years = rows_per_day * 365 * 2 * ROW_BYTES / 1e12
write_qps = rows_per_day / SECONDS
print(round(tb_two_years, 2), round(write_qps, 1))  # 1.01 115.2
```

## Powers of two in RAM

Using 2^10 ≈ 10^3, how many gigabytes is 2^34 bytes? Does a working set of 40 million records × 2 KB fit in a server with 128 GB of RAM?

```python
SHIFT = 34
RECORDS = 40_000_000
RECORD_BYTES = 2 * 1024
RAM_GB = 128
```

**Answer:** 2^34 is exactly 16 GiB, which matches the shortcut (2^34 = 16 × 2^30). The working set is 40e6 × 2 KB = 80 GB by the decimal shortcut, and 76.3 GiB exactly. It fits in 128 GB with roughly 50 GB left for the process and a modest index. A second full in-memory copy of the same rows would push past 128 GB, and the design would move to a larger box or a cache of the hot subset.

```python
RECORDS = 40_000_000
RECORD_BYTES = 2 * 1024

gib = RECORDS * RECORD_BYTES / 2**30
shortcut_gb = RECORDS * 2 / 1e6  # 2 KB → 2e-6 GB each, times 40e6
print(2**34 / 2**30, round(gib, 1), shortcut_gb)  # 16.0 76.3 80.0
```

## Downtime from a nines target

The promise is 99.95% availability over a 365-day year. How many minutes of downtime is that, and where does that budget sit between 99.9% and 99.99%?

```python
TARGET = 0.9995
MINUTES_PER_YEAR = 365 * 24 * 60
```

**Answer:** 99.95% allows about 263 minutes, or 4.4 hours, per year. Allowed downtime at 99.9% is about 8.8 hours and at 99.99% about 53 minutes, so 99.95% is roughly halfway between those two budgets. The hours still matter: this target is an hours-per-year conversation, which usually means automated failover rather than a five-minute error budget.

```python
MINUTES_PER_YEAR = 365 * 24 * 60


def downtime_minutes(availability: float) -> float:
    return (1 - availability) * MINUTES_PER_YEAR


for nines in (0.999, 0.9995, 0.9999):
    minutes = downtime_minutes(nines)
    print(f"{nines:.4%} → {minutes:.0f} min ({minutes / 60:.2f} h)")
# 99.9000% → 526 min (8.76 h)
# 99.9500% → 263 min (4.38 h)
# 99.9900% → 53 min (0.88 h)
```

## Users are not QPS

A teammate says "10 million users, so 10,000 QPS." Each user actually performs 20 actions a day, and peak is 3×. What average and peak QPS follow from those assumptions, and what actions-per-user figure is hiding inside the 10,000 QPS claim?

```python
DAU = 10_000_000
ACTIONS = 20
PEAK = 3
CLAIMED_QPS = 10_000
SECONDS = 100_000
```

**Answer:** Average is 2,000 QPS and peak is 6,000 QPS. The 10,000 QPS claim implies about 100 actions per user per day if it was meant as an average (10,000 × 10^5 / 10^7). Write the actions-per-user assumption before dividing; a user count alone does not determine QPS.

```python
DAU = 10_000_000
ACTIONS = 20
PEAK = 3
CLAIMED_QPS = 10_000
SECONDS = 100_000

avg = DAU * ACTIONS / SECONDS
implied_actions = CLAIMED_QPS * SECONDS / DAU
print(avg, avg * PEAK, implied_actions)  # 2000.0 6000.0 100.0
```

## Where the deep dive goes

A ticket window serves about 200 QPS through the week and about 80,000 QPS for three minutes when a single show goes on sale. The burst all lands on one show id. What is the burst multiple, and which part of the system earns the deep dive?

```python
STEADY_QPS = 200
ONSALE_QPS = 80_000
```

**Answer:** The on-sale window is 400× steady traffic, on one key. Deep-dive that path: a waiting room or queue, how the hot show id is cached, and what happens when the node that owns it dies. Account settings and profile images stay near the steady rate, so leave them on the ordinary request path and say so.

```python
STEADY_QPS = 200
ONSALE_QPS = 80_000

print(ONSALE_QPS / STEADY_QPS)  # 400.0
```

## A blown 45-minute clock

One mock spent 9 minutes on scope, 16 on the high-level design, 14 on the deep dive, and 1 on wrap-up. Scope and the high-level pass have ceilings of 5 and 15 minutes. The deep dive and wrap-up have floors of 15 and 3 minutes. Which phases missed, and what gets shortened next time?

```python
spent = {"scope": 9, "high_level": 16, "deep_dive": 14, "wrap_up": 1}
```

**Answer:** Scope ran 4 minutes over its ceiling and the high-level pass ran 1 minute over. The deep dive missed its 15-minute floor, and wrap-up never really started. Next time, lock scope at the 5-minute mark with the assumptions written down, and stop adding boxes once the high-level picture has buy-in, so the deep dive and a real wrap-up still fit.

```python
spent = {"scope": 9, "high_level": 16, "deep_dive": 14, "wrap_up": 1}
ceiling = {"scope": 5, "high_level": 15}
floor = {"deep_dive": 15, "wrap_up": 3}

over = {name: spent[name] - limit for name, limit in ceiling.items() if spent[name] > limit}
under = {name: limit - spent[name] for name, limit in floor.items() if spent[name] < limit}
print(sum(spent.values()), over, under)  # 40 {'scope': 4, 'high_level': 1} {'deep_dive': 1, 'wrap_up': 2}
```

## The slow hop in a latency budget

Checkout should answer in 200 ms at p99. The pieces you have are a cache hit at 0.2 ms, application work at 3 ms, a same-datacenter database read at 1 ms, and a cross-continent fraud check at 150 ms. Does the path meet the target, and which hop is worth redesigning?

```python
parts_ms = {"cache": 0.2, "app": 3.0, "db": 1.0, "fraud_rtt": 150.0}
TARGET_MS = 200
```

**Answer:** The sum is 154.2 ms, which meets a 200 ms budget with about 46 ms to spare. The fraud round trip is about 97% of that sum, so that hop is the one to redesign: run it in parallel, move it into the same region, or take it off the synchronous path. The 3 ms of application work is lost inside the 150 ms round trip.

```python
parts_ms = {"cache": 0.2, "app": 3.0, "db": 1.0, "fraud_rtt": 150.0}
TARGET_MS = 200

total = sum(parts_ms.values())
dominant = max(parts_ms, key=parts_ms.get)
print(round(total, 1), round(TARGET_MS - total, 1), dominant, round(parts_ms[dominant] / total, 2))
# 154.2 45.8 fraud_rtt 0.97
```
