# Connection Management

Every Postgres connection costs memory and a backend process. Without connection pooling, a busy application can exhaust server resources in seconds. Proper connection management — pooling, sizing, and cursor strategy — determines whether your database handles 10 or 10,000 concurrent users.

## Key Points

- **Connection pooling** — reuses connections across requests. Each Postgres connection costs ~5-10 MB. Pool instead of opening per-request.
- **PgBouncer** — external pooler. Transaction mode is standard; session features (prepared statements, temp tables) don't work across pooled connections.
- **Pool sizing** — (cores × 2) + spindles. More connections past optimal makes performance worse, not better. Monitor idle-in-transaction.
- **Server-side cursors** — stream large result sets without loading everything into memory. Hold a transaction open while active.

## Example

```python
# Python application with connection pooling (psycopg3 + pool)
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    conninfo="host=localhost dbname=mydb",
    min_size=5,
    max_size=20,
    max_idle=300,  # close idle connections after 5 min
)

# Each request borrows and returns a connection
def get_orders(customer_id: int):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, total FROM orders WHERE customer_id = %s",
                (customer_id,),
            )
            return cur.fetchall()
    # connection returned to pool automatically

# Large export using a server-side cursor
def export_all_events():
    with pool.connection() as conn:
        with conn.cursor(name="export") as cur:
            cur.execute("SELECT * FROM events")
            while batch := cur.fetchmany(5000):
                write_to_csv(batch)
```

This demonstrates application-level pooling with psycopg3's built-in pool: bounded connection count, automatic checkout/return via context manager, and a named (server-side) cursor for streaming a large export.
