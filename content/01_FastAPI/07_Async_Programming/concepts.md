## `async def` path operations

Declare a path operation with `async def` when it needs to `await` async work — async database drivers, `httpx` clients, message brokers, anything I/O-bound that exposes a coroutine. FastAPI runs the coroutine on the event loop, so multiple in-flight `async` requests share a single worker cooperatively.

```python
import httpx

@app.get("/weather/{city}")
async def weather(city: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.weather/{city}")
    return r.json()
```

Inside `async def`, every `await` yields control to the event loop so other requests can make progress.

## Sync `def` path operations

Path operations declared with plain `def` still work — FastAPI runs them in a threadpool so blocking calls (synchronous DB drivers, `requests`, file I/O) don't stall the event loop.

```python
@app.get("/legacy")
def legacy_route():
    return blocking_db_query()   # safe — runs in threadpool
```

The threadpool is bounded (default ~40 threads). Mixing sync and async is fine, but if every route is `def` you're paying threadpool overhead on every request and gaining nothing from ASGI.

## Concurrency model

FastAPI's concurrency win is **cooperative multitasking**: when an `async` handler awaits I/O, the event loop runs other handlers in the gap. A single worker can hold thousands of in-flight requests as long as they spend most of their time waiting.

This is not parallelism — there's still only one Python thread per worker doing CPU work at any moment. To use multiple CPU cores, run multiple worker processes (`uvicorn --workers 4` or gunicorn with the `UvicornWorker` class).

| Workload | Best with |
|----------|-----------|
| I/O-bound (DB, HTTP, files) | `async def` everywhere, one worker |
| CPU-bound (parsing, ML inference) | sync `def` or async-offloaded, multiple workers |
| Mixed | `async` routes, offload CPU work to threadpool or worker queue |

## When async hurts

The single biggest async footgun: **calling a blocking function from inside `async def` stalls the entire event loop**. Every concurrent request stops until the blocking call returns.

```python
# WRONG — time.sleep blocks the loop
@app.get("/wait")
async def wait():
    time.sleep(5)        # all other requests are frozen for 5 seconds
    return {"ok": True}

# Right options:
# 1. Use the async version
await asyncio.sleep(5)
# 2. Offload to the threadpool
await asyncio.to_thread(time.sleep, 5)
# 3. Make the route sync def — FastAPI runs it in the threadpool
def wait():
    time.sleep(5)
```

Common culprits: `requests` (use `httpx` async), synchronous DB drivers in `async` handlers, heavy CPU work, `time.sleep`, and unbuffered file I/O.

## Async database drivers

For async to actually buy you concurrency on database-bound APIs, the whole stack must be async — driver, ORM, and session management.

```python
# requirements:  asyncpg, sqlalchemy[asyncio]>=2.0

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

@app.get("/books/{id}")
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    book = await session.get(Book, id)
    return book
```

Async-capable drivers: `asyncpg` (Postgres), `aiomysql` (MySQL), `aiosqlite` (SQLite), `motor` (MongoDB). Putting a sync driver behind an `async def` handler is worse than going fully sync because you pay coroutine overhead without getting concurrency.
