# Async Programming

Why FastAPI is fast and how to keep it that way. Async is what lets one worker hold thousands of in-flight requests — but only if you don't accidentally block the event loop.

## Key Points

- **`async def` for awaitable work** — use it when the handler awaits async I/O (async DB driver, `httpx`, message brokers).
- **`def` for blocking work** — FastAPI runs sync handlers in a threadpool so they don't stall other requests.
- **Cooperative concurrency** — `await` is where the event loop switches between requests; no `await`, no concurrency.
- **Not parallelism** — one worker = one CPU thread; add worker processes for parallelism.
- **Async footgun** — calling a blocking function inside `async def` stalls every concurrent request. Use the async equivalent, `asyncio.to_thread`, or make the route sync `def`.
- **End-to-end async pays the bill** — async only helps if the driver and ORM are also async (`asyncpg`, async SQLAlchemy). Sync drivers in async handlers are worse than going fully sync.

## Example

A side-by-side demo showing the right and wrong ways to handle a slow operation, plus a properly async DB query:

```python
import asyncio
import time

import httpx
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

app = FastAPI()

# ✅ Async I/O — yields to the loop on every await
@app.get("/weather/{city}")
async def weather(city: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.weather/{city}")
    return r.json()


# ❌ Blocking inside async — freezes other requests for 5s
@app.get("/wait-wrong")
async def wait_wrong():
    time.sleep(5)
    return {"ok": True}


# ✅ Blocking offloaded to the threadpool
@app.get("/wait-right")
async def wait_right():
    await asyncio.to_thread(time.sleep, 5)
    return {"ok": True}


# ✅ Blocking in a sync handler — FastAPI moves it to the threadpool automatically
@app.get("/wait-sync")
def wait_sync():
    time.sleep(5)
    return {"ok": True}


# ✅ Async database query end-to-end
engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@app.get("/books/{id}")
async def get_book(id: int, session: AsyncSession = Depends(get_session)):
    return await session.get(Book, id)  # truly non-blocking
```

If you only remember one rule: **never call a blocking function from inside `async def`**. When in doubt, make the handler `def` and let FastAPI move it to the threadpool.
