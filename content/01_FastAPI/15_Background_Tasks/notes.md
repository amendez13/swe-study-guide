# Background Tasks

How to do work *after* sending the response without making the user wait — and how to know when FastAPI's built-in tool is enough versus when you need a real queue.

## Key Points

- **`BackgroundTasks`** — schedule a function (sync or async) to run after the response is sent; lives in the same worker.
- **Three-part fit test** — short, loss-tolerant, no retries → `BackgroundTasks`. Otherwise use a queue.
- **Real queues** — Celery, Dramatiq, arq, or platform-managed; require a broker (Redis/RabbitMQ/SQS) and a separate worker process.
- **What queues add** — durability, retries with backoff, scheduling, fan-out, isolation, observability.
- **Third-party integrations** — short ones (email confirmation, analytics events) fit `BackgroundTasks`; long ones (image generation, exports) belong in a queue.

## Example

A signup endpoint using `BackgroundTasks` for a quick email + analytics event, alongside an image-upload endpoint that defers the heavy work to a durable queue:

```python
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()


class SignupIn(BaseModel):
    email: str
    name: str


# --- Short, loss-tolerant: BackgroundTasks ---
def send_welcome_email(to: str, name: str):
    # Synchronous SMTP call; fine — it runs after the response
    smtp.send(to=to, subject="Welcome", body=f"Hi {name}!")


async def track_event(event: str, **props):
    # Async HTTP POST to analytics
    async with httpx.AsyncClient() as client:
        await client.post("https://analytics.example.com/events",
                          json={"event": event, **props})


@app.post("/signup")
async def signup(payload: SignupIn, tasks: BackgroundTasks):
    user = create_user(payload.email, payload.name)
    tasks.add_task(send_welcome_email, payload.email, payload.name)
    tasks.add_task(track_event, "signup_completed", user_id=user.id)
    return {"id": user.id}    # client sees this immediately


# --- Long, durable: real queue ---
# Imagine a separate worker process running arq with the same Redis
from arq.connections import RedisSettings, create_pool

job_queue = None

@app.on_event("startup")
async def startup():
    global job_queue
    job_queue = await create_pool(RedisSettings.from_dsn("redis://localhost"))


@app.post("/images/{image_id}/thumbnail")
async def request_thumbnail(image_id: int, size: int = 256):
    job = await job_queue.enqueue_job("generate_thumbnail", image_id, size)
    return {"job_id": job.job_id, "status": "queued"}


# In worker.py (separate process, run with `arq worker:WorkerSettings`):
#
# async def generate_thumbnail(ctx, image_id: int, size: int) -> str:
#     img = await download_image(image_id)
#     thumb = resize(img, size)
#     return await upload_to_s3(thumb)
#
# class WorkerSettings:
#     functions = [generate_thumbnail]
#     redis_settings = RedisSettings.from_dsn("redis://localhost")
```

**Why this split:** the welcome email and analytics event are short, fail-tolerant nice-to-haves. If they don't fire, no support ticket. Thumbnail generation can take 5–30 seconds, can fail (download error, S3 timeout), and absolutely needs a retry — that's why it goes to arq, not `BackgroundTasks`.
