## OVER clause

Defines a window — a partition and ordering — over which a function computes. Unlike GROUP BY, window functions do not collapse rows; every input row appears in the output with the computed value alongside.

```sql
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER () AS company_avg
FROM employees;
-- Every row shows the company-wide average alongside individual salary
```

`OVER ()` with no arguments makes the window span the entire result set. Adding `PARTITION BY` and `ORDER BY` inside the parentheses scopes and orders the computation.

## PARTITION BY

Divides the result set into independent groups (partitions). The window function resets for each partition — think of it as GROUP BY without collapsing rows.

```sql
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department) AS diff_from_dept
FROM employees;
```

Each row shows its own salary alongside the department average. Multiple window functions can use different partitions in the same query.

## ROW_NUMBER, RANK, DENSE_RANK

Numbering functions that assign sequential positions within a partition. They differ only in how they handle ties.

```sql
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rnk,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rnk
FROM employees;
```

| Salary | ROW_NUMBER | RANK | DENSE_RANK |
|--------|-----------|------|------------|
| 120k | 1 | 1 | 1 |
| 110k | 2 | 2 | 2 |
| 110k | 3 | 2 | 2 |
| 100k | 4 | 4 | 3 |

- `ROW_NUMBER` — always unique, arbitrary tiebreaker
- `RANK` — ties share a rank, next rank skips (1, 2, 2, 4)
- `DENSE_RANK` — ties share a rank, next rank does not skip (1, 2, 2, 3)

Common pattern: use ROW_NUMBER to pick the top-N per group:

```sql
-- Latest order per customer
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
    FROM orders
) sub WHERE rn = 1;
```

## LAG and LEAD

Access a row before (LAG) or after (LEAD) the current row within the window. Essential for computing deltas: day-over-day change, month-over-month growth, gap detection.

```sql
SELECT
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) AS prev_day,
    revenue - LAG(revenue) OVER (ORDER BY date) AS daily_change,
    LEAD(revenue) OVER (ORDER BY date) AS next_day
FROM daily_sales;
```

Both accept an optional offset (default 1) and default value (returned when there's no previous/next row):

```sql
-- Compare to 7 days ago, default to 0 if no data
LAG(revenue, 7, 0) OVER (ORDER BY date)
```

## Frame clauses (ROWS BETWEEN)

Control exactly which rows relative to the current row are included in the window computation. The default frame depends on whether ORDER BY is present.

```sql
-- Running total (default frame with ORDER BY)
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM transactions;
-- Frame: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- 7-day moving average (explicit frame)
SELECT date, amount,
    AVG(amount) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily_metrics;

-- Centered window (3 rows before and after)
SELECT date, temp,
    AVG(temp) OVER (
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) AS smoothed
FROM weather;
```

`ROWS` counts physical row positions. `RANGE` groups rows with the same ORDER BY value together. `GROUPS` (Postgres 11+) counts groups of tied values. For most moving-window use cases, `ROWS` is what you want.

## Aggregate functions as window functions

SUM, AVG, COUNT, MIN, MAX, and other aggregates can be used with OVER to compute running totals, cumulative counts, or moving averages — without collapsing rows.

```sql
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total,
    COUNT(*) OVER (ORDER BY date) AS cumulative_count,
    SUM(amount) OVER () AS grand_total,
    ROUND(amount / SUM(amount) OVER () * 100, 2) AS pct_of_total
FROM transactions;
```

This is powerful because a single query can show both individual row values and aggregate computations at multiple levels (row-level, partition-level, total-level) without self-joins or subqueries.
