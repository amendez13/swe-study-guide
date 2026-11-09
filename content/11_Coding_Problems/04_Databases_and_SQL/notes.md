# Databases and SQL

This topic is about writing the query and drawing the schema in an interview. The studio below is small on purpose: four potters, their pieces, the sales to cafes, and the payouts. You join it, group it, and keep the facts in one place. How a primary grows into replicas and shards is a different topic, in the system-design section.

## Key Points

- **Explicit and implicit joins** — put the match in `ON`. A comma join with no `WHERE` is a cross join.
- **Inner, left, and full joins** — inner drops unmatched rows, left keeps the left side, full keeps both. Dee survives only the outer forms.
- **Self joins and anti-joins** — alias a table to itself, and use `id <` so a pair appears once. `NOT EXISTS` is "no partner." A left join plus `IS NULL` lies when some of a parent's rows match and some do not.
- **SELECT, INSERT, UPDATE, DELETE** — name the rows a write will touch. An update or delete without `WHERE` hits the whole table.
- **WHERE, GROUP BY, and HAVING** — filter rows, then collapse, then filter groups. Aggregates do not go in `WHERE`.
- **NULL** — unknown fails ordinary comparisons. Use `IS NULL`. `COUNT(col)` skips nulls. `COUNT(*)` does not.
- **Subqueries and CTEs** — a subquery builds a set or a derived table. A CTE names that result so you can aggregate it twice, as with an average of potter totals.
- **Window functions** — a value across related rows without collapsing them. `ROW_NUMBER` has no ties. `RANK` ties and then skips. A running `SUM` needs an `ORDER BY` inside `OVER`.
- **First through third normal form** — one value per column, columns depend on the whole key, and non-key columns do not depend on each other.
- **Keys and constraints** — a primary key identifies a row. A foreign key rejects a piece with no potter. Unique and check constraints are the other promises worth saying.
- **Indexes** — equality columns, then the range column. A covering index holds the columns the query returns. An unused index still costs writes.
- **Transactions, ACID, and isolation** — statements that must agree commit together. Add to a balance in one `UPDATE`, or two readers will each write a stale total back.
- **When to denormalize** — copy a fact only with the query it speeds up and a way to refresh the copy. A closed-month summary qualifies. A name retyped on every live sale does not.
- **Handle ambiguity** — decide what a sale is, whether a cafe is a table, and what this pass will not store. Then draw.
- **Core tables, relationships, and actions** — potter, piece, sale, payout. Say the cardinality and which statement performs each verb.
- **Large database design** — keep recent sales hot, archive or partition older months by `sold_on`, and leave replicas and shards to the system-design topic.

## The studio

```text
potters (id, name, bench)
  1 Ada  A
  2 Bo   A
  3 Cy   B
  4 Dee  B

pieces (id, potter_id, form, price_cents)
  10 Ada bowl  1200
  11 Ada mug    800
  12 Ada vase   900     -- never sold
  20 Bo  bowl  1500
  30 Cy  plate 2000

sales (id, piece_id, cafe, sold_on, qty)
  100 bowl  North 2024-05-01  2
  101 mug   North 2024-05-02  1
  102 Bo    South 2024-05-02  4
  103 bowl  South 2024-05-03  1
  104 plate North 2024-05-03  3

payouts (id, potter_id, amount_cents, paid_on)
  1 Ada 4400  2024-05-04
  2 Bo  6000  NULL
```

Ada's sold work is `2 * 1200 + 1 * 800 + 1 * 1200 = 4400` cents. Bo is `4 * 1500 = 6000`. Cy is `3 * 2000 = 6000`. Dee sold nothing. The average of those four totals is 4100, so Ada, Bo, and Cy sit above it.

## Example

```sql
-- Potters paid more than the average potter, using one grouped result twice.
WITH rev AS (
  SELECT p.id AS potter_id,
         p.name AS name,
         COALESCE(SUM(s.qty * pi.price_cents), 0) AS cents
  FROM potters AS p
  LEFT JOIN pieces AS pi ON pi.potter_id = p.id
  LEFT JOIN sales AS s ON s.piece_id = pi.id
  GROUP BY p.id, p.name
)
SELECT name, cents
FROM rev
WHERE cents > (SELECT AVG(cents) FROM rev)
ORDER BY cents DESC, name;
-- Bo 6000, Cy 6000, Ada 4400. Dee is 0 and drops out.
```

The CTE is the whole idea of this topic in one statement: join on keys, treat a missing sale as no cents, group per potter, then filter the groups. The vase does not change Ada's total, because the unsold piece contributes no sale rows to the sum.

## More practice

Work the original exercises on the **Drills** tab. They use this studio. Each answer is a query or a short schema judgment. Replication and sharding are not in these drills.
