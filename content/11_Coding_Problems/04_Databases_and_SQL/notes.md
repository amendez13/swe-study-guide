# Databases and SQL

This topic is an outline of the relational ideas that come up when an interview turns to tables and queries: keys, joins, the order of filter and group, indexes, transactions, and when a duplicated column is a choice rather than an accident. The cards are a skeleton. Query practice and storage-engine detail belong in a later pass, and the system-design treatment of databases lives in that section of the guide.

## Key Points

- **Rows, keys, and relationships** — a primary key identifies a row; a foreign key is a promise that the referenced row exists.
- **Joins match rows** — inner join drops unmatched rows; left join keeps them. Joining a one-to-many relationship multiplies rows.
- **Filter, then group** — `WHERE` sees rows, `HAVING` sees groups, and `COUNT(column)` skips nulls.
- **Indexes serve a query shape** — propose an index for a filter or join you can name, and remember that writes maintain it.
- **Transactions group writes** — name the pair of writes that must commit together.
- **Normalize, then denormalize on purpose** — one fact in one place, unless a specific read justifies a copy and a plan to keep it fresh.
- **Say the query before you write it** — a spoken sentence with the tables, the match, and the filter is the spec for the SQL.

## Example

```sql
-- Patrons with at least one overdue loan.
SELECT patrons.id, patrons.name, COUNT(*) AS overdue
FROM patrons
JOIN loans ON loans.patron_id = patrons.id
WHERE loans.due_on < CURRENT_DATE
  AND loans.returned_on IS NULL
GROUP BY patrons.id, patrons.name
HAVING COUNT(*) >= 1;
```

The sketch uses an inner join because patrons with no overdue loan are not part of the answer, a `WHERE` for row-level overdue rules, and `GROUP BY` so the count is per patron. An index on `loans (patron_id, due_on)` is the one to discuss if this query is the hot path.
