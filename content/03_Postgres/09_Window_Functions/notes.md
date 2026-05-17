# Window Functions

Window functions compute a value across a set of rows related to the current row — without collapsing those rows into groups. They're the tool for rankings, running totals, moving averages, and row-to-row comparisons that would otherwise require self-joins or correlated subqueries.

## Key Points

- **OVER clause** — defines the window. Without arguments, spans all rows. Add PARTITION BY and ORDER BY to scope.
- **PARTITION BY** — splits into groups like GROUP BY but keeps all rows. The function resets per partition.
- **ROW_NUMBER / RANK / DENSE_RANK** — numbering functions. ROW_NUMBER is unique; RANK skips on ties; DENSE_RANK doesn't.
- **LAG / LEAD** — access previous/next rows. Essential for deltas (day-over-day, period-over-period).
- **Frame clauses** — ROWS BETWEEN controls exactly which rows are included. Use for moving averages and sliding windows.
- **Aggregates as window functions** — SUM, AVG, COUNT with OVER gives running totals and cumulative computations without collapsing rows.

## Example

```sql
-- Sales dashboard: per-rep row with running total, rank, and day-over-day change

SELECT
    sale_date,
    rep_name,
    amount,
    SUM(amount) OVER (PARTITION BY rep_name ORDER BY sale_date) AS running_total,
    RANK() OVER (PARTITION BY rep_name ORDER BY amount DESC) AS best_sale_rank,
    amount - LAG(amount) OVER (PARTITION BY rep_name ORDER BY sale_date) AS vs_previous,
    AVG(amount) OVER (
        PARTITION BY rep_name ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7
FROM sales
ORDER BY rep_name, sale_date;
```

Each row preserves individual sale data while adding four window computations: cumulative revenue per rep, rank of each sale by amount, change vs the previous sale, and a 7-day moving average. No GROUP BY, no self-join, no subquery.
