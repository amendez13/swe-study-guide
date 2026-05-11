## FastAPI `BackgroundTasks`

`BackgroundTasks` lets a route schedule work to run **after the response is sent**. The client gets a fast 200/201 right away; the slow work (sending email, writing audit logs, generating a thumbnail) happens in the background of the same worker process.

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_email(to: str, subject: str, body: str):
    # blocking SMTP call; doesn't matter, response is already out
    smtp.send(to=to, subject=subject, body=body)

@app.post("/signup")
async def signup(email: str, tasks: BackgroundTasks):
    user = create_user(email)
    tasks.add_task(send_email, email, "Welcome", "Hello!")
    return {"id": user.id}      # client gets this immediately
```

Inject `BackgroundTasks` as a parameter; `add_task(fn, *args, **kwargs)` schedules a function (sync or async) to run after the response. Multiple tasks run in order on the same worker.

## When `BackgroundTasks` is enough

`BackgroundTasks` is the right tool when **all three** are true:

1. The work is **short** (seconds, not minutes) and won't pile up under load.
2. It's OK if the work is **lost** when the worker crashes, redeploys, or scales down — there's no durability guarantee.
3. It doesn't need **retries**, **scheduling**, or **cross-process coordination**.

Examples that fit: sending a "welcome" email, writing an audit log row, invalidating a cache, posting a Slack notification. Examples that don't: monthly billing runs, video transcoding, anything a user might call support about if it silently fails.

## When you need a real queue

For durable, retryable, schedulable background work, use a real task queue: **Celery**, **Dramatiq**, **arq** (async-native), or platform-managed (AWS SQS+Lambda, GCP Cloud Tasks). The architecture changes: tasks are serialized and pushed to a broker (Redis, RabbitMQ, SQS), and a separate worker process picks them up.

```python
# arq example — an async-native task queue
from arq import create_pool
from arq.connections import RedisSettings

async def generate_thumbnail(ctx, image_url: str, size: int) -> str:
    img = await download(image_url)
    thumb = resize(img, size)
    return await upload(thumb)

# In a route handler
@app.post("/images")
async def upload_image(...):
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job("generate_thumbnail", image_url, 256)
    return {"status": "queued"}
```

What the queue gives you that `BackgroundTasks` doesn't: persistence across crashes, retries with backoff, scheduled/delayed execution, fan-out to multiple workers, observability (job IDs, status), and isolation (web workers don't share CPU with task workers).

## Third-party integrations triggered by background tasks

Most third-party integrations (email, SMS, push notifications, AI APIs, analytics events) are the canonical use case for background work. They're slow, occasionally fail, and the user shouldn't wait for them — but they need to eventually happen.

```python
# Quick path: short, fire-and-forget — use BackgroundTasks
@app.post("/orders")
async def create_order(payload: OrderIn, tasks: BackgroundTasks):
    order = repo.create(payload)
    tasks.add_task(send_order_confirmation, order)  # Mailgun, 1-2s
    tasks.add_task(track_event, "order_created", order.id)  # Segment, 50ms
    return order

# Durable path: long-running, needs retries — use a queue
@app.post("/images/{id}/generate")
async def generate_image(id: int):
    await job_queue.enqueue("generate_with_deepai", id)
    return {"status": "queued"}
```

Rule of thumb: short integrations (under ~2 seconds, OK to lose) → `BackgroundTasks`. Anything else → durable queue.
