## Rows, keys, and relationships

A relational table is a set of rows with a fixed collection of columns. A primary key identifies a row. A foreign key says a value in this table must match a key in another table, which is how "this loan belongs to this patron" is enforced by the database rather than only by application code. Say the keys out loud before you write a query; most wrong joins are a confusion about which column identifies what.

## Joins match rows

An inner join keeps pairs of rows that satisfy the match. A left join keeps every row from the left table and fills the right side with nulls when nothing matches. Choose the join from the question "do I want unmatched rows?" and not from habit. Joining on a non-key column can multiply rows: one patron with three loans joined to those loans produces three result rows, and a later count will lie if you forget that.

```sql
SELECT patrons.name, loans.due_on
FROM patrons
LEFT JOIN loans ON loans.patron_id = patrons.id;
```

## Filter, then group

`WHERE` drops rows before aggregation. `GROUP BY` collapses the surviving rows into one row per group. `HAVING` filters those groups. `COUNT(*)` counts rows in the group; `COUNT(column)` skips nulls in that column. A common mix-up is putting a group condition in `WHERE`, which cannot see the aggregate, or filtering individual rows in `HAVING`, which runs too late.

## Indexes serve a query shape

An index is a side structure, usually a B-tree, that finds rows by a column without reading the whole table. It helps equality and range lookups on the leading columns of the index, and it costs writes because every insert and update must maintain it. Name the query you are speeding up before you propose an index. An index on a column the query never filters or joins is pure overhead.

## Transactions group writes

A transaction makes a group of writes succeed or fail together. The properties to be able to say are atomicity (all or nothing), consistency (constraints still hold), isolation (concurrent transactions do not see each other's half-finished work at the level you asked for), and durability (committed data survives a crash). In an interview, point at the specific pair of writes that would be wrong if one of them landed alone.

## Normalize, then denormalize on purpose

Normalization stores each fact once so an update cannot disagree with itself. Third normal form is the usual interview target: every non-key column depends on the key, the whole key, and nothing but the key. Denormalize only after you can name the read that the extra copy speeds up, and say how you will keep the copies from drifting. "It's faster" without that story is not a design.

## Say the query before you write it

Translate the question into a sentence with the tables, the match, the filter, and the aggregation. Then write the SQL as that sentence. For "how many overdue loans does each patron have, counting only patrons with at least one," the sentence already contains the join, the `WHERE due_on < today` filter, the `GROUP BY`, and the `HAVING COUNT(*) >= 1`. Reading it back catches a missing join condition faster than staring at the result grid.
