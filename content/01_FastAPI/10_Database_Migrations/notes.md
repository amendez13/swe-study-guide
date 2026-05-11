# Database Migrations

The schema changes; the data doesn't disappear. Migrations are how you evolve a live database without `DROP TABLE; CREATE TABLE`.

## Key Points

- **Why migrations** — `create_all()` only works on a fresh DB; production data needs versioned, reversible scripts.
- **Alembic** — the standard SQLAlchemy migrations tool; `alembic init` scaffolds the config and versions directory.
- **Target metadata** — point `alembic/env.py`'s `target_metadata` at `Base.metadata` so autogeneration can compare.
- **Revisions** — each migration is a Python file with `upgrade()` and `downgrade()` and a `down_revision` pointer to its parent.
- **Autogenerate** — `alembic revision --autogenerate` drafts a migration from the model/schema diff; review the draft, fix what autogen missed (renames, server-side defaults, CHECK constraints).
- **`alembic upgrade head`** — applies pending migrations; runs in CI/CD **before** the new app version starts serving requests.
- **Destructive changes** — drops/renames need a two-release coordinated rollout (stop reads first, then drop) — autogenerate won't protect you from this.

## Example

A complete workflow for adding an `isbn` column to a `books` table.

**1. Scaffold Alembic (one time):**

```bash
pip install alembic
alembic init alembic
```

**2. Wire `alembic/env.py` to your models:**

```python
# alembic/env.py (excerpt)
from app.db import Base
target_metadata = Base.metadata
```

**3. Add the column to the SQLAlchemy model:**

```python
# app/models.py
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    isbn = Column(String(13), unique=True, index=True, nullable=True)  # NEW
```

**4. Generate the migration:**

```bash
alembic revision --autogenerate -m "add isbn to books"
```

This produces `alembic/versions/<hash>_add_isbn_to_books.py`. Review it:

```python
revision = "abc123def456"
down_revision = "0001_initial"

def upgrade():
    op.add_column(
        "books",
        sa.Column("isbn", sa.String(length=13), nullable=True),
    )
    op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)

def downgrade():
    op.drop_index("ix_books_isbn", table_name="books")
    op.drop_column("books", "isbn")
```

**5. Apply locally and in CI/CD:**

```bash
alembic upgrade head
```

In a deploy pipeline this runs before the new app version boots:

```yaml
# .github/workflows/deploy.yml (sketch)
- run: alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.PROD_DB_URL }}
- run: ./scripts/deploy-app.sh
```

**6. If the column turns out to be wrong, roll back:**

```bash
alembic downgrade -1   # back one revision
```

The autogenerate diff caught the column and the unique index, but it wouldn't have detected a `title` → `name` rename — that would have shown up as `drop_column("title")` + `add_column("name")`, which loses data. Always read the diff before committing.
