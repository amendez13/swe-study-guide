# Accessing PostgreSQL from Applications

The bridge between your application code and the database: client libraries, connection pooling, query patterns (ORM vs raw SQL), architectural boundaries (repository pattern), and testing strategies that exercise real SQL against a real database.

## Key Points

- **Client libraries** — psycopg3 (Python), pg (Node), pgx (Go), JDBC (Java). Always use native parameterization.
- **Connection pool per application** — each process gets its own pool. Size to match database capacity, not request volume.
- **ORM vs raw SQL** — ORM for CRUD and portability; raw SQL for complex queries, Postgres-specific features, and performance. Most teams use both.
- **Repository pattern** — encapsulates database access behind domain operations. Keeps SQL out of route handlers.
- **Testing with schemas** — isolated schema per test worker enables parallel testing with real SQL, real constraints, and real types.

## Example

```python
# Complete application data layer: pool, repository, parameterized queries

from dataclasses import dataclass
from decimal import Decimal
from psycopg_pool import ConnectionPool

pool = ConnectionPool("dbname=mydb", min_size=5, max_size=15)

@dataclass
class Order:
    id: int
    customer_id: int
    total: Decimal
    status: str

class OrderRepo:
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def find_recent(self, customer_id: int, limit: int = 10) -> list[Order]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                """SELECT id, customer_id, total, status
                   FROM orders WHERE customer_id = %s
                   ORDER BY created_at DESC LIMIT %s""",
                (customer_id, limit),
            ).fetchall()
            return [Order(*r) for r in rows]

    def create(self, customer_id: int, total: Decimal) -> Order:
        with self._pool.connection() as conn:
            row = conn.execute(
                """INSERT INTO orders (customer_id, total)
                   VALUES (%s, %s)
                   RETURNING id, customer_id, total, status""",
                (customer_id, total),
            ).fetchone()
            return Order(*row)

# Usage in a route handler
repo = OrderRepo(pool)
orders = repo.find_recent(customer_id=42, limit=5)
new_order = repo.create(customer_id=42, total=Decimal("149.99"))
```

This shows a production-ready data layer: connection pool with bounded size, repository class exposing domain operations, parameterized queries for safety, RETURNING to avoid extra queries, and dataclass for typed results.
