## SQLAlchemy ORM (sync)

The most common database stack with FastAPI. Declare models, get a `Session` per request, query through it. Sync SQLAlchemy works fine with sync `def` handlers; for async handlers see the next concept.

```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://user:pass@host/db")
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
```

SQLAlchemy 2.x supports a typed `Mapped[T]` API alongside the legacy `Column` style; new code should prefer the typed form.

## SQLAlchemy async (2.x)

For end-to-end async I/O, use `AsyncSession` and `create_async_engine` with an async driver like `asyncpg`. The query API is mostly identical, but every database call is awaitable.

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

@app.get("/books/{id}")
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    return await session.get(Book, id)
```

Mixing sync and async sessions in one app is fine, but a single request should pick one — don't open an async session and then call sync methods on it.

## SQLModel

`SQLModel` is Tiangolo's library that fuses Pydantic and SQLAlchemy into one model class. The same class serves as the database table and the API schema, which removes a lot of boilerplate at the cost of mixing two concerns.

```python
from sqlmodel import Field, SQLModel

class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
```

Good for small/medium projects and rapid prototypes. Larger projects often outgrow it and split back into separate ORM models and Pydantic schemas because the API and DB shapes diverge over time.

## Database session per request

The canonical pattern: a `Depends(get_session)` dependency opens a session at the start of the request and closes it at the end via `yield`/`finally`. Every dependency and route handler in that request shares the same session, so they see a consistent snapshot.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/books")
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).all()
```

Never share a session across requests — sessions are not thread-safe, and a leaked session leaks connections from the pool. The dependency pattern enforces correct lifecycle automatically.

## Lifespan events

Resources that should be initialized once at app startup (connection pools, ML models, message broker clients) live in the `lifespan` async context manager. Code before `yield` runs on startup; code after runs on shutdown.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)
```

`lifespan=` replaces the older `@app.on_event("startup")` / `@app.on_event("shutdown")` decorators, which are now deprecated.

## Models, schemas, and tables

Keep ORM models (shaped by the database) separate from Pydantic schemas (shaped by the API). One class with `from_attributes=True` is fine when they line up, but when they diverge — and they will — having separate types saves you from leaking internal columns through the API or accepting bad fields from clients.

```python
# Database shape
class BookRow(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    soft_deleted = Column(Boolean, default=False)  # internal

# API input
class BookIn(BaseModel):
    title: str

# API output
class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    # soft_deleted never leaves the API
```

## Relationships

SQLAlchemy expresses table relationships via `relationship()` and foreign keys. The three patterns:

- **One-to-many** — `Author.books` is a list of `Book`; each `Book` has an `author_id` foreign key.
- **Many-to-many** — link table; declare with `secondary="link_table"`.
- **One-to-one** — one-to-many with a `uselist=False` on the parent side.

```python
class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")
```

Loading strategy matters: `lazy="joined"` always joins (good for small, frequently accessed children); `lazy="select"` issues a follow-up query (good when you don't always need the related rows but cheap to load); `lazy="raise"` makes lazy loads an error, forcing explicit eager loading and catching N+1 problems in tests.

## Reusable queries

Move non-trivial query logic out of route handlers into functions or repository-style classes. Keeps routes readable, makes the logic testable in isolation, and avoids duplicating the same filter in five places.

```python
def get_visible_books_for(user: User, db: Session) -> list[Book]:
    return (
        db.query(Book)
        .filter(Book.deleted_at.is_(None))
        .filter(or_(Book.public, Book.owner_id == user.id))
        .order_by(Book.created_at.desc())
        .all()
    )

@app.get("/books")
def list_books(user = Depends(current_user), db = Depends(get_db)):
    return get_visible_books_for(user, db)
```

## Database choice

The standard FastAPI lineup:

- **SQLite** — perfect for dev, tests, and small single-node apps. Zero setup, single file. Limited concurrency (one writer at a time).
- **PostgreSQL** — the default production choice. Mature, predictable, rich type system, robust async driver (`asyncpg`).
- **MySQL / MariaDB** — fine choice when the rest of the org runs on it. Less feature-rich than Postgres but well supported.

Because SQLAlchemy abstracts the dialect, switching DBs is mostly a connection-string change — until you hit dialect-specific features (Postgres JSONB, full-text search, partial indexes), at which point you've committed.
