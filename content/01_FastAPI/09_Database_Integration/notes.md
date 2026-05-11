# Database Integration

How FastAPI talks to a SQL database without leaking lifecycle bugs (leaked sessions, connection pool starvation) or coupling concerns (DB models on the API surface).

## Key Points

- **SQLAlchemy ORM** — the default stack; sync `Session` works with sync handlers, `AsyncSession` works with async ones.
- **SQLModel** — Pydantic + SQLAlchemy fused; faster to start, harder to scale when shapes diverge.
- **Session per request** — open via `Depends(get_db)` with `yield`/`finally` cleanup; never share sessions across requests.
- **Lifespan events** — `@asynccontextmanager async def lifespan(app)` runs setup before `yield` and teardown after; replaces the deprecated `on_event` decorators.
- **Models vs schemas** — DB-shaped SQLAlchemy models stay internal; Pydantic schemas shape what the API accepts and returns.
- **Relationships** — `relationship()` + `ForeignKey`; loading strategy (`joined`, `select`, `raise`) determines N+1 vs over-fetching tradeoff.
- **Reusable queries** — move non-trivial query logic into functions/repository classes for testability.
- **Database choice** — SQLite for dev/test, Postgres for production by default, MySQL if the org already runs on it.

## Example

A two-route app with separate ORM model and Pydantic schemas, session-per-request dependency, lifespan for the engine pool, and a reusable query helper:

```python
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

# --- DB layer ---
engine = create_engine("sqlite:///./library.db", future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")


# --- API schemas ---
class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    author_name: str


# --- Reusable query ---
def list_books_with_authors(db: Session) -> list[Book]:
    return db.query(Book).join(Book.author).order_by(Book.title).all()


# --- Lifespan + DB dependency ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield
    engine.dispose()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(lifespan=lifespan)


@app.get("/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)):
    return [
        BookOut(id=b.id, title=b.title, author_name=b.author.name)
        for b in list_books_with_authors(db)
    ]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return BookOut(id=book.id, title=book.title, author_name=book.author.name)
```

The DB engine is created once at startup, sessions open per request, the query helper is testable on its own, and the API schema (`BookOut`) is decoupled from the table — adding a `soft_deleted` column to `Book` won't change a thing on the API surface.
