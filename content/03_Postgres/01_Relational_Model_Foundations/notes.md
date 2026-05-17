# Relational Model Foundations

The building blocks every other PostgreSQL topic rests on: how data is organized into tables, how tables reference each other through keys, and how normalization guides schema design. Getting these right means fewer migrations later.

## Key Points

- **Tables, rows, and columns** — a table is a typed collection of rows. Postgres enforces column types on every write and stores rows in an unordered heap.
- **Primary keys** — uniquely identify each row. Postgres auto-creates a B-tree index on the PK. Prefer `GENERATED ALWAYS AS IDENTITY` over the legacy `serial` type.
- **Foreign keys** — enforce referential integrity across tables. Know the three ON DELETE behaviors: RESTRICT (block), CASCADE (delete child), SET NULL (orphan gracefully).
- **Normalization (1NF → 3NF)** — eliminate redundancy by ensuring every non-key column depends on the key, the whole key, and nothing but the key. Denormalize deliberately for performance, not by accident.
- **Relationship types** — one-to-many (FK on the many side), many-to-many (junction table with two FKs), one-to-one (FK + UNIQUE). The relationship type determines where the foreign key lives.
- **Schemas** — namespaces within a database. Use them for tenant isolation, module separation, or parallel test runners. The `search_path` setting controls unqualified name resolution.

## Example

```sql
-- A small normalized schema: authors, books, tags (many-to-many)

CREATE TABLE authors (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE books (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title     text NOT NULL,
    author_id integer REFERENCES authors (id) ON DELETE CASCADE
);

CREATE TABLE tags (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text UNIQUE NOT NULL
);

CREATE TABLE book_tags (
    book_id integer REFERENCES books (id) ON DELETE CASCADE,
    tag_id  integer REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, tag_id)
);

-- Insert some data
INSERT INTO authors (name) VALUES ('Kleppmann');
INSERT INTO books (title, author_id) VALUES ('Designing Data-Intensive Applications', 1);
INSERT INTO tags (name) VALUES ('distributed-systems'), ('databases');
INSERT INTO book_tags (book_id, tag_id) VALUES (1, 1), (1, 2);

-- Query across the relationships
SELECT b.title, a.name AS author, t.name AS tag
FROM books b
JOIN authors a ON a.id = b.author_id
JOIN book_tags bt ON bt.book_id = b.id
JOIN tags t ON t.id = bt.tag_id;
```

This schema exercises every concept in the topic: identity-generated primary keys, foreign keys with cascade deletes, a junction table for the many-to-many relationship between books and tags, and normalization (author name stored once, not repeated per book).
