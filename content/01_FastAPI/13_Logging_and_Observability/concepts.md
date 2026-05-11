## Python `logging` module mental model

Python's `logging` module has four parts that compose into a pipeline. Once you understand the pipeline, every other logging trick is a variation on configuring it.

```
Logger ──emits──▶ LogRecord ──filtered by──▶ Filter ──formatted by──▶ Formatter ──sent to──▶ Handler
```

- **`Logger`** — named, hierarchical; you call `.info()`/`.warning()`/`.error()` on it.
- **`Handler`** — where logs go: stderr, a file, a remote service. A logger can have multiple.
- **`Formatter`** — how the record turns into bytes/string (plain text, JSON, etc.).
- **`Filter`** — optional predicates that drop or transform records (e.g. drop debug logs from a noisy library).

```python
import logging

logger = logging.getLogger("app.books")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(handler)

logger.info("created book", extra={"book_id": 42})
```

## Logger hierarchies

Logger names with dots form a hierarchy: `app`, `app.books`, `app.books.queries`. A child logger inherits handlers and levels from its parents unless overridden. Configure once at the root (or near it) and every module gets logging for free.

```python
# Configure once
logging.basicConfig(level=logging.INFO)

# Every module just does this — no per-module setup
logger = logging.getLogger(__name__)
logger.info("ready")
```

`__name__` inside a module is the import path (`app.routers.books`), so logger names match the code structure automatically. To silence a noisy library: `logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)`.

## Structured logging

Plain-text logs are fine for humans tailing a file; **JSON logs** are what log aggregators (Logtail, Datadog, ELK, Grafana Loki) need to index fields and run queries. Same content, different formatter.

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        # Attach anything passed via extra={...}
        if hasattr(record, "context"):
            payload.update(record.context)
        return json.dumps(payload)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)

logger.info("created book", extra={"context": {"book_id": 42, "user_id": 1}})
# {"ts":"...","level":"INFO","name":"app.books","msg":"created book","book_id":42,"user_id":1}
```

Production logs should be JSON; local dev can stay plain text for readability.

## Correlation IDs

In a system with multiple services (or even just one service with concurrent requests), you need a way to find all log lines belonging to a single request. The standard tool is a **correlation ID** (a.k.a. request ID or trace ID) generated per incoming request, attached to every log line, and propagated to downstream HTTP calls in a header (`X-Request-ID` or W3C `traceparent`).

```python
import uuid
from contextvars import ContextVar
from fastapi import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

@app.middleware("http")
async def correlation_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex
    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response
    finally:
        request_id_var.reset(token)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True
```

Now `record.request_id` is available for every log line and can be included in the formatter — making it possible to grep one request's complete history out of a sea of concurrent logs.

## Custom filters

Filters can do more than drop records — they can mutate them. Useful for redacting PII, attaching request context, or down-sampling noisy debug logs.

```python
import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

class EmailRedactor(logging.Filter):
    def filter(self, record):
        record.msg = EMAIL_RE.sub("<email>", str(record.msg))
        return True

handler.addFilter(EmailRedactor())
```

The filter runs before the formatter, so it sees and can rewrite the raw message. Apply filters at the handler that ships to external services (so internal logs keep the data, but the logs leaving the process are scrubbed).

## Cloud log shipping

Production logs need to leave the process so they survive crashes, restarts, and autoscaling. Two common approaches:

1. **stdout/stderr + sidecar** — the app writes JSON to stdout; the platform (Kubernetes, Render, Heroku) collects it and forwards to the log aggregator. Simple, twelve-factor, and works with anything.
2. **Direct handler** — the app writes through a handler that ships logs over HTTP (Logtail, Datadog, CloudWatch). More control, but the handler must be reliable, async, and not block the app.

```python
# Only enable cloud shipping in production
if settings.env == "production":
    from logtail import LogtailHandler
    handler = LogtailHandler(source_token=settings.logtail_token)
    logging.getLogger().addHandler(handler)
```

Always gate the cloud handler on environment — you don't want local dev logs flooding a paid log service.

## Sentry for error tracking

Logs answer "what happened?"; **error tracking** answers "what blew up and where, with full context?". Sentry (or Rollbar/Honeybadger) captures every uncaught exception with a stack trace, the request that triggered it, the user it affected, and any breadcrumbs you've left.

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.05,    # 5% APM sampling
    environment=settings.env,
)
```

The FastAPI integration auto-captures exceptions and request context. You'll still want logs for everything that isn't an exception — slow queries, business events, audit trails — but for "something broke at 3am," Sentry beats grepping logs.
