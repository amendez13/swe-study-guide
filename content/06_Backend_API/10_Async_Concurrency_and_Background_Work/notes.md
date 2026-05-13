# Async, Concurrency, and Background Work

Backend performance is shaped by how the server handles waiting, contention, and slow side effects. This topic covers the mental model behind asynchronous APIs and when work should move off the main request path entirely.

## Key Points

- **Async is about waiting efficiently** - It helps most with I/O-bound work, not CPU-heavy computation.
- **Concurrency has a model** - Event loops, threads, and processes each impose different tradeoffs.
- **Dependencies can defeat async** - One blocking library can erase the benefit of non-blocking handlers.
- **Background jobs protect request latency** - Slow side effects often belong off the main response path.
- **Lifespan matters** - Shared clients and pools need startup and shutdown discipline.
- **Tune for the workload you actually have** - Throughput and latency depend on request shape, not on buzzwords alone.

## Example

```python
import asyncio


async def fetch_order(order_id: int) -> str:
    await asyncio.sleep(0.1)  # pretend this is network I/O
    return f"order:{order_id}"


async def main() -> None:
    results = await asyncio.gather(fetch_order(1), fetch_order(2))
    print(results)


asyncio.run(main())
```

The example is tiny, but it shows the core async value: while one request is waiting on I/O, the process can make progress on another instead of blocking entirely.
