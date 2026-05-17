# Triggers and Rules

Triggers let you attach automatic behavior to table modifications — audit logging, timestamp maintenance, validation, and derived data updates that fire regardless of which application or script changes the data.

## Key Points

- **Triggers** — functions fired automatically on INSERT, UPDATE, DELETE, or TRUNCATE. Access OLD (existing row) and NEW (incoming row).
- **Row-level vs statement-level** — row triggers fire per row and have OLD/NEW; statement triggers fire once per statement.
- **BEFORE vs AFTER** — BEFORE can modify/reject the row (return NEW or NULL); AFTER is for side effects (audit, notification).
- **INSTEAD OF** — makes non-updatable views writable by defining what an update means.
- **Execution order** — alphabetical by name when multiple triggers on the same event. WHEN clauses skip unnecessary invocations.
- **Triggers vs app logic** — triggers guarantee enforcement at any access path; app logic is more visible and testable.

## Example

```sql
-- Automatic updated_at and audit log for a table

CREATE TABLE products (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text NOT NULL,
    price      numeric(10, 2) NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE products_audit (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id integer NOT NULL,
    action     text NOT NULL,
    old_price  numeric(10, 2),
    new_price  numeric(10, 2),
    changed_at timestamptz NOT NULL DEFAULT now()
);

-- BEFORE trigger: maintain updated_at
CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_products_updated
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- AFTER trigger: audit price changes only
CREATE FUNCTION audit_price_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO products_audit (product_id, action, old_price, new_price)
    VALUES (NEW.id, TG_OP, OLD.price, NEW.price);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_products_price_audit
    AFTER UPDATE OF price ON products
    FOR EACH ROW
    WHEN (OLD.price IS DISTINCT FROM NEW.price)
    EXECUTE FUNCTION audit_price_change();

-- Test: only the price change triggers the audit
UPDATE products SET price = 29.99 WHERE id = 1;
```

This demonstrates a BEFORE trigger for timestamp maintenance and a conditional AFTER trigger that only fires when the price column actually changes value.
