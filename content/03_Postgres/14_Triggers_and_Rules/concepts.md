## Triggers

Functions fired automatically before or after INSERT, UPDATE, DELETE, or TRUNCATE on a table. They guarantee side effects happen regardless of which client or application modifies the data.

```sql
-- Audit trigger: log every change to the orders table
CREATE TABLE orders_audit (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   integer NOT NULL,
    action     text NOT NULL,
    old_data   jsonb,
    new_data   jsonb,
    changed_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION orders_audit_trigger() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO orders_audit (order_id, action, old_data, new_data)
    VALUES (
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        to_jsonb(OLD),
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_orders_audit
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION orders_audit_trigger();
```

Trigger functions return type `trigger` and have access to special variables: `NEW` (incoming row), `OLD` (existing row), `TG_OP` (INSERT/UPDATE/DELETE), `TG_TABLE_NAME`, and `TG_WHEN` (BEFORE/AFTER).

## Row-level vs statement-level triggers

Row-level triggers fire once per affected row. Statement-level triggers fire once per SQL statement regardless of how many rows are affected.

```sql
-- Row-level: fires for each updated row
CREATE TRIGGER trg_row
    AFTER UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION log_change();

-- Statement-level: fires once even if 1000 rows are updated
CREATE TRIGGER trg_stmt
    AFTER UPDATE ON orders
    FOR EACH STATEMENT EXECUTE FUNCTION log_bulk_update();
```

Row-level triggers have access to OLD and NEW. Statement-level triggers do not — they know the operation happened but not which specific rows were affected. Use statement-level triggers for notifications or summary actions that don't need per-row data.

## BEFORE vs AFTER triggers

BEFORE triggers can modify or reject the incoming row. AFTER triggers see the final committed row and are used for side effects.

```sql
-- BEFORE: automatically set updated_at
CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;  -- returning NEW allows the operation to proceed
END;
$$;

CREATE TRIGGER trg_set_updated
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- BEFORE: reject invalid state transitions
CREATE FUNCTION validate_status_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.status = 'delivered' AND NEW.status != 'delivered' THEN
        RAISE EXCEPTION 'Cannot change status after delivery';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_status
    BEFORE UPDATE OF status ON orders
    FOR EACH ROW EXECUTE FUNCTION validate_status_change();
```

Returning NULL from a BEFORE trigger silently cancels the operation for that row. Returning NEW allows it to proceed (with modifications). AFTER triggers' return value is ignored.

## INSTEAD OF triggers

Fire on views to make non-updatable views writable. The trigger function handles the actual table modifications.

```sql
CREATE VIEW order_summary AS
SELECT o.id, c.name AS customer, o.total, o.status
FROM orders o JOIN customers c ON c.id = o.customer_id;

CREATE FUNCTION order_summary_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    UPDATE orders SET status = NEW.status, total = NEW.total WHERE id = OLD.id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_order_summary_update
    INSTEAD OF UPDATE ON order_summary
    FOR EACH ROW EXECUTE FUNCTION order_summary_update();

-- Now this works
UPDATE order_summary SET status = 'shipped' WHERE id = 5;
```

INSTEAD OF triggers are the only way to make complex views (multi-table joins, aggregates) updatable. The trigger function defines the semantics of what an "update to the view" means.

## Trigger execution order and conditional firing

When multiple triggers exist on the same event, they fire in alphabetical order by name. Use WHEN clauses and column-specific triggers to reduce unnecessary invocations.

```sql
-- Only fire when status actually changes
CREATE TRIGGER trg_status_change
    AFTER UPDATE OF status ON orders
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION notify_status_change();
```

The WHEN clause is evaluated before the trigger function is called. If it evaluates to false, the function is not invoked at all — saving the overhead of entering PL/pgSQL, creating a subtransaction context, etc.

## Triggers vs application logic

Triggers guarantee consistency regardless of which client modifies the data, but they make debugging harder and create hidden behavior.

| Factor | Triggers | Application logic |
|--------|----------|-------------------|
| Consistency guarantee | Always enforced, any client | Only if all clients implement it |
| Visibility | Hidden in schema, easy to miss | Visible in application code |
| Testing | Harder to unit test in isolation | Standard test tooling |
| Debugging | Stack traces cross SQL/PL boundary | Single-language debugging |
| Performance | Adds overhead to every write | Only runs when the application calls it |

Prefer triggers for cross-cutting concerns (audit logging, updated_at timestamps, derived column maintenance). Prefer application logic for complex business rules where visibility and testability matter more than guaranteed enforcement.
