# Stored Procedures and PL/pgSQL

PL/pgSQL brings procedural programming to Postgres — variables, control flow, exception handling, and dynamic SQL. Functions embed computation inside queries; procedures manage multi-step operations with transaction control.

## Key Points

- **Functions vs procedures** — functions return values and work in SELECT; procedures use CALL and can COMMIT/ROLLBACK internally.
- **PL/pgSQL** — variables (DECLARE), assignment (:=), IF/ELSIF/ELSE, LOOP, FOR IN query, WHILE, RETURN.
- **RETURNS TABLE / SETOF** — functions returning multiple rows. Use as FROM source for parameterized reusable queries.
- **RAISE NOTICE / EXCEPTION** — NOTICE for logging; EXCEPTION aborts the transaction. Use for business rule enforcement.
- **Exception handling** — BEGIN/EXCEPTION blocks catch specific errors. Each block is a subtransaction (has overhead).
- **SQL vs PL/pgSQL** — prefer LANGUAGE sql for simple functions (inlinable). Use PL/pgSQL only when you need control flow or error handling.

## Example

```sql
-- A function that safely transfers money between accounts with validation and logging

CREATE FUNCTION transfer_funds(
    from_account integer,
    to_account integer,
    amount numeric
) RETURNS text LANGUAGE plpgsql AS $$
DECLARE
    sender_balance numeric;
BEGIN
    -- Lock both accounts in consistent order
    SELECT balance INTO sender_balance
    FROM accounts WHERE id = from_account FOR UPDATE;

    IF sender_balance IS NULL THEN
        RAISE EXCEPTION 'Account % does not exist', from_account;
    END IF;

    IF sender_balance < amount THEN
        RETURN format('Insufficient funds: have %s, need %s', sender_balance, amount);
    END IF;

    UPDATE accounts SET balance = balance - amount WHERE id = from_account;
    UPDATE accounts SET balance = balance + amount WHERE id = to_account;

    RAISE NOTICE 'Transferred % from account % to %', amount, from_account, to_account;
    RETURN 'success';
EXCEPTION
    WHEN foreign_key_violation THEN
        RETURN format('Account %s does not exist', to_account);
END;
$$;

-- Usage
SELECT transfer_funds(1, 2, 50.00);
```

This function demonstrates variable declaration, SELECT INTO, IF branching, RAISE NOTICE for logging, RAISE EXCEPTION for hard errors, exception handling for graceful failure, and row-level locking within a function.
