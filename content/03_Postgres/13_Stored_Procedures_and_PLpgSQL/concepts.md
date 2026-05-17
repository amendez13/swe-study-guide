## Functions vs procedures

Functions return a value and can be used in SELECT, WHERE, or as part of an expression. Procedures (Postgres 11+) can manage transactions internally (COMMIT/ROLLBACK within the body) and are invoked with CALL.

```sql
-- Function: returns a value, usable in queries
CREATE FUNCTION total_revenue(customer integer) RETURNS numeric AS $$
    SELECT COALESCE(SUM(total), 0) FROM orders WHERE customer_id = customer;
$$ LANGUAGE sql;

SELECT name, total_revenue(id) FROM customers;

-- Procedure: can commit/rollback, invoked with CALL
CREATE PROCEDURE archive_old_orders(cutoff_date date) LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO orders_archive SELECT * FROM orders WHERE created_at < cutoff_date;
    DELETE FROM orders WHERE created_at < cutoff_date;
    COMMIT;  -- procedures can commit mid-execution
END;
$$;

CALL archive_old_orders('2023-01-01');
```

Use functions for computations you embed in queries. Use procedures for multi-step operations that need transaction control (batch processing, data migrations, maintenance tasks).

## PL/pgSQL basics

Postgres's default procedural language. Adds variables, control flow, exception handling, and dynamic SQL to SQL's declarative foundation.

```sql
CREATE FUNCTION apply_discount(order_id integer, pct numeric)
RETURNS numeric LANGUAGE plpgsql AS $$
DECLARE
    current_total numeric;
    new_total numeric;
BEGIN
    SELECT total INTO current_total FROM orders WHERE id = order_id;

    IF current_total IS NULL THEN
        RAISE EXCEPTION 'Order % not found', order_id;
    END IF;

    new_total := current_total * (1 - pct / 100);

    UPDATE orders SET total = new_total WHERE id = order_id;
    RETURN new_total;
END;
$$;
```

Key PL/pgSQL constructs: `DECLARE` for variables, `:=` for assignment, `IF/ELSIF/ELSE/END IF`, `LOOP/EXIT WHEN/END LOOP`, `FOR var IN query LOOP`, `WHILE ... LOOP`, `RETURN` and `RETURN NEXT`.

## RETURNS TABLE / RETURNS SETOF

Functions that return multiple rows, usable as a FROM source. This is how you create reusable parameterized queries.

```sql
CREATE FUNCTION recent_orders(cust_id integer, n integer DEFAULT 10)
RETURNS TABLE (id integer, total numeric, created_at timestamptz)
LANGUAGE sql AS $$
    SELECT id, total, created_at FROM orders
    WHERE customer_id = cust_id
    ORDER BY created_at DESC
    LIMIT n;
$$;

-- Use like a table
SELECT * FROM recent_orders(42, 5);
SELECT * FROM recent_orders(42) WHERE total > 100;
```

For PL/pgSQL, use `RETURN NEXT` to emit rows one at a time, or `RETURN QUERY` to emit an entire query result:

```sql
CREATE FUNCTION active_customers()
RETURNS SETOF customers LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY SELECT * FROM customers WHERE active = true;
END;
$$;
```

## RAISE NOTICE / RAISE EXCEPTION

Logging and error signaling inside PL/pgSQL. NOTICE is informational (printed to the client but does not abort). EXCEPTION aborts the current transaction.

```sql
CREATE FUNCTION transfer(from_id int, to_id int, amount numeric)
RETURNS void LANGUAGE plpgsql AS $$
DECLARE
    from_balance numeric;
BEGIN
    SELECT balance INTO from_balance FROM accounts WHERE id = from_id;

    RAISE NOTICE 'Current balance for account %: %', from_id, from_balance;

    IF from_balance < amount THEN
        RAISE EXCEPTION 'Insufficient funds: have %, need %', from_balance, amount;
    END IF;

    UPDATE accounts SET balance = balance - amount WHERE id = from_id;
    UPDATE accounts SET balance = balance + amount WHERE id = to_id;
END;
$$;
```

Exception levels: DEBUG, LOG, INFO, NOTICE, WARNING, EXCEPTION. Only EXCEPTION aborts. Use RAISE NOTICE during development for tracing; use RAISE EXCEPTION for business rule violations.

## Exception handling

PL/pgSQL supports structured exception handling with BEGIN/EXCEPTION blocks. Catch specific error codes or broad categories.

```sql
CREATE FUNCTION safe_insert(p_email text) RETURNS text LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO users (email) VALUES (p_email);
    RETURN 'created';
EXCEPTION
    WHEN unique_violation THEN
        RETURN 'already exists';
    WHEN check_violation THEN
        RETURN 'invalid email format';
    WHEN OTHERS THEN
        RAISE NOTICE 'Unexpected error: %', SQLERRM;
        RETURN 'error: ' || SQLERRM;
END;
$$;
```

Each BEGIN/EXCEPTION block creates a subtransaction (like a savepoint). If the exception fires, work inside that block is rolled back. This has overhead — don't wrap every statement in an exception block.

## SQL vs PL/pgSQL language choice

Not every function needs PL/pgSQL. Pure-SQL functions (`LANGUAGE sql`) are simpler, inlinable by the planner, and sufficient when you don't need variables or control flow.

```sql
-- LANGUAGE sql: simple, inlinable, no procedural overhead
CREATE FUNCTION order_count(cust_id integer) RETURNS bigint
LANGUAGE sql STABLE AS $$
    SELECT count(*) FROM orders WHERE customer_id = cust_id;
$$;

-- LANGUAGE plpgsql: when you need variables, branching, loops, or exceptions
CREATE FUNCTION process_batch() RETURNS integer LANGUAGE plpgsql AS $$
DECLARE
    processed integer := 0;
    rec record;
BEGIN
    FOR rec IN SELECT id FROM jobs WHERE status = 'pending' LIMIT 100 LOOP
        UPDATE jobs SET status = 'processing' WHERE id = rec.id;
        processed := processed + 1;
    END LOOP;
    RETURN processed;
END;
$$;
```

Use `LANGUAGE sql` when the function body is a single query (or a few queries) with no branching. The planner can inline SQL functions into the calling query, potentially optimizing the whole thing together.
