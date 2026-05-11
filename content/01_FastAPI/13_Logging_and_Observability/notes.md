# Logging and Observability

What gets logged, how it gets out of the process, and how you find one request's history in a million-line log stream.

## Key Points

- **Pipeline mental model** — `Logger` → `Filter` → `Formatter` → `Handler`; configure each piece independently.
- **Hierarchies** — `logging.getLogger(__name__)` inherits config from parents; configure once at the root.
- **Structured (JSON) logs** — required for log aggregators to index fields; plain text is for local dev.
- **Correlation IDs** — one ID per request, attached via middleware + `ContextVar` + a logging `Filter`; makes per-request tracing possible.
- **Custom filters** — drop, sample, or redact records (e.g. mask email addresses before logs leave the process).
- **Cloud shipping** — prefer stdout + platform log collector (twelve-factor); direct handlers when you need finer control.
- **Sentry for errors** — captures uncaught exceptions with stack trace, request context, and user; complements logs but doesn't replace them.

## Example

A complete logging setup with JSON output, a correlation-ID filter, an email-redaction filter, and a Sentry hookup gated on environment:

```python
import json
import logging
import re
import uuid
from contextvars import ContextVar

import sentry_sdk
from fastapi import FastAPI, Request
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import get_settings

settings = get_settings()

# --- Correlation ID context ---
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


# --- Filters ---
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class EmailRedactor(logging.Filter):
    def filter(self, record):
        record.msg = EMAIL_RE.sub("<email>", str(record.msg))
        return True


# --- JSON formatter ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "ts": self.formatTime(record),
                "level": record.levelname,
                "name": record.name,
                "msg": record.getMessage(),
                "request_id": getattr(record, "request_id", "-"),
            }
        )


def configure_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    handler.addFilter(EmailRedactor())
    root.handlers = [handler]

    # Quiet noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


configure_logging()

# --- Sentry (production only) ---
if settings.env == "production":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.05,
        environment=settings.env,
    )

# --- FastAPI app with correlation middleware ---
app = FastAPI()
logger = logging.getLogger("app")


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


@app.get("/users/{id}")
async def get_user(id: int):
    logger.info("looking up user", extra={"user_id": id})
    # If something raises, Sentry captures it with the request_id attached
    return {"id": id}
```

Log output:

```json
{"ts":"2026-05-12 10:00:00","level":"INFO","name":"app","msg":"looking up user","request_id":"abc123"}
```

Grep the log stream by `request_id=abc123` and you get the complete story of one request, even with hundreds of concurrent ones. If `/users/0` raises, Sentry gets the stack trace with `request_id: abc123` so you can correlate the exception back to the logs.
