## Why migrations

`Base.metadata.create_all()` only works on a fresh database. The moment you have production data, schema changes must be applied as versioned, reversible scripts — not by dropping and recreating tables.

Migrations exist to answer three questions every deployable change forces:

1. What's the exact sequence of DDL statements needed to bring an existing database to the new schema?
2. How do we apply them automatically in CI/CD without manual SQL?
3. How do we roll back if the new schema turns out to be wrong?

A migration tool tracks which migrations a database has already applied (typically in a `alembic_version` table) so it knows what to run next.

## Alembic

Alembic is the standard migrations tool for SQLAlchemy. It lives alongside the application code, knows how to read SQLAlchemy models, and produces versioned Python scripts that describe schema changes.

```bash
pip install alembic
alembic init alembic         # one-time scaffold
```

This creates `alembic.ini`, an `alembic/` directory with an `env.py` (configuration), a `versions/` directory (where migrations live), and a script template.

In `alembic/env.py`, point `target_metadata` at your `Base.metadata` so autogeneration can compare models against the live schema:

```python
from app.db import Base
target_metadata = Base.metadata
```

## Revisions

A revision is a single migration file with two functions: `upgrade()` (apply the change) and `downgrade()` (reverse it). Each revision has a unique ID and a `down_revision` pointer to its parent, forming a linear or branching history.

```python
# alembic/versions/abc123_add_isbn_to_books.py
revision = "abc123"
down_revision = "def456"

def upgrade():
    op.add_column("books", sa.Column("isbn", sa.String(13), nullable=True))
    op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)

def downgrade():
    op.drop_index("ix_books_isbn", table_name="books")
    op.drop_column("books", "isbn")
```

`op` is Alembic's DDL helper API; it generates dialect-appropriate SQL. Write `downgrade()` even if you'll rarely run it — it forces you to think about whether the change is reversible.

## Autogenerate

`alembic revision --autogenerate -m "<message>"` compares your SQLAlchemy models against the current live database and drafts a migration file with the diff. Saves a lot of hand-written DDL, but treat the output as a draft.

```bash
alembic revision --autogenerate -m "add isbn to books"
# inspect alembic/versions/<new_file>.py before committing
```

Autogenerate catches most things — added/removed tables and columns, type changes, index changes — but misses some (renames look like drop+add, server-side defaults, CHECK constraints). Always review the generated file, edit it where needed, and commit.

## `alembic upgrade head`

The command that actually applies migrations. `head` means "the most recent revision in the script tree." You can also upgrade to a specific revision (`alembic upgrade abc123`), downgrade with `alembic downgrade -1` (one step back) or to a specific revision.

```bash
# Locally, after pulling new migration files
alembic upgrade head

# In CI/CD, before starting the new app version
alembic upgrade head
```

This is what runs in your deploy pipeline. The convention: migrations run **before** the new application code starts serving traffic, so the running app always sees a schema that matches its code. The exception is destructive migrations (drop column, rename) which need the old code's reads to stop first — those are typically rolled out as two coordinated releases.
