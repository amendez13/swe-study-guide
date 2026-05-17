## Client libraries

Every language has a mature Postgres client that wraps the wire protocol (or libpq). The library handles connection setup, query execution, parameter binding, type conversion, and result parsing.

| Language | Library | Notes |
|----------|---------|-------|
| Python | `psycopg3` (or `psycopg2`) | Async support, pipeline mode, COPY streaming |
| Node.js | `pg` (node-postgres) | Callback and promise APIs, connection pooling |
| Go | `pgx` | High-performance, batch queries, binary format |
| Java | JDBC (`org.postgresql`) | Standard JDBC interface, HikariCP for pooling |
| Rust | `tokio-postgres` / `sqlx` | Async, compile-time query checking (sqlx) |

```python
# psycopg3 basic usage
import psycopg

with psycopg.connect("dbname=mydb") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM users WHERE active = %s", (True,))
        for row in cur:
            print(row)
```

Use the library's native parameterization (not string formatting) for all queries. Every library supports it; there's no performance or convenience reason to concatenate.

## Connection pool per application

Each application process should use its own connection pool. Don't open a new connection per request — and don't share a single connection across concurrent requests.

```python
# psycopg3 with a connection pool
from psycopg_pool import ConnectionPool

pool = ConnectionPool("dbname=mydb", min_size=5, max_size=20)

async def handle_request(user_id: int):
    async with pool.connection() as conn:
        row = await conn.execute(
            "SELECT name FROM users WHERE id = %s", (user_id,)
        ).fetchone()
        return row
```

```javascript
// node-postgres pool
const { Pool } = require('pg');
const pool = new Pool({ max: 20 });

async function getUser(id) {
    const { rows } = await pool.query('SELECT name FROM users WHERE id = $1', [id]);
    return rows[0];
}
```

Pool sizing: match the database server capacity (see Connection Management topic). A common mistake is each microservice opening its own pool of 50 — ten services × 50 = 500 connections, far exceeding what Postgres handles efficiently.

## ORM vs raw SQL

ORMs (SQLAlchemy, Django ORM, TypeORM, GORM) add convenience and portability at the cost of control. Raw SQL gives full access to Postgres features but requires more manual work.

```python
# ORM: declarative, portable, less control
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    total = Column(Numeric)
    customer_id = Column(Integer, ForeignKey('customers.id'))

orders = session.query(Order).filter(Order.total > 100).all()

# Raw SQL: full control, Postgres-specific features
result = conn.execute(text("""
    SELECT o.id, o.total, c.name
    FROM orders o
    JOIN customers c ON c.id = o.customer_id
    WHERE o.total > :min_total
    AND o.metadata @> :filter
"""), {"min_total": 100, "filter": '{"priority": "high"}'})
```

Many teams use both: ORM for standard CRUD and simple queries; raw SQL for complex joins, window functions, CTEs, JSONB operations, and performance-critical paths. The ORM handles the boring stuff; raw SQL handles the interesting stuff.

## Repository pattern

Encapsulates database access behind a domain-specific interface. Keeps SQL out of route handlers and business logic, making the code testable and the data layer swappable.

```python
class OrderRepository:
    def __init__(self, pool):
        self._pool = pool

    async def get_by_customer(self, customer_id: int) -> list[Order]:
        async with self._pool.connection() as conn:
            rows = await conn.execute(
                "SELECT id, total, status FROM orders WHERE customer_id = %s",
                (customer_id,),
            ).fetchall()
            return [Order(*row) for row in rows]

    async def create(self, customer_id: int, total: Decimal) -> int:
        async with self._pool.connection() as conn:
            row = await conn.execute(
                "INSERT INTO orders (customer_id, total) VALUES (%s, %s) RETURNING id",
                (customer_id, total),
            ).fetchone()
            return row[0]
```

The repository exposes domain operations (get_by_customer, create) not database primitives (SELECT, INSERT). Route handlers call repository methods without knowing whether the implementation uses an ORM, raw SQL, or a microservice call.

## Testing with schemas

Create an isolated schema per test worker, run migrations, execute tests, and drop the schema. Enables parallel test execution without database conflicts and without the overhead of creating/destroying entire databases.

```python
import pytest

@pytest.fixture
def db(connection):
    schema = f"test_{os.getpid()}_{uuid4().hex[:8]}"
    connection.execute(f"CREATE SCHEMA {schema}")
    connection.execute(f"SET search_path TO {schema}")
    run_migrations(connection)
    yield connection
    connection.execute(f"DROP SCHEMA {schema} CASCADE")

def test_create_order(db):
    db.execute("INSERT INTO orders (customer_id, total) VALUES (1, 99.99)")
    count = db.execute("SELECT count(*) FROM orders").fetchone()[0]
    assert count == 1
```

Advantages over mocking: tests exercise real SQL, real constraints, and real data types. Issues that mocks hide (type mismatches, constraint violations, query syntax errors) are caught during testing.

Alternative approach: use a transaction per test that rolls back at the end. Faster (no DDL per test) but doesn't support testing code that commits internally.
