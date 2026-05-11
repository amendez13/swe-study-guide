## Middleware

Middleware is code that runs before and after **every** request, wrapping the entire route stack. Use it for cross-cutting concerns that apply to all (or most) routes: logging request times, attaching correlation IDs, compressing responses, enforcing TLS.

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-process-time"] = f"{time.perf_counter() - start:.3f}"
    return response
```

Middleware runs in registration order on the request and reverse order on the response. If you need cross-cutting logic on **some** routes only, prefer a dependency injected via `dependencies=[...]`.

## CORS middleware

Browsers block JavaScript from one origin (`https://app.example.com`) from making requests to another (`https://api.example.com`) unless the server opts in via CORS headers. `CORSMiddleware` configures the opt-in.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,    # only with explicit origins, not "*"
)
```

`allow_origins=["*"]` is convenient for public APIs but is **incompatible** with `allow_credentials=True` — the spec forbids that combination. For credentialed (cookie/auth-header) APIs, enumerate origins explicitly.

CORS only affects browsers; `curl`, server-to-server calls, and mobile apps don't care. A misconfigured CORS policy is a frontend bug, not a security control.

## Built-in middleware

Starlette ships several middleware classes that FastAPI exposes directly. Add them with `app.add_middleware(...)`:

- **`GZipMiddleware`** — gzip responses larger than a threshold; trivial wins for JSON-heavy APIs.
- **`TrustedHostMiddleware`** — rejects requests whose `Host` header doesn't match an allowlist; mitigates host-header attacks behind misconfigured proxies.
- **`HTTPSRedirectMiddleware`** — 308-redirects HTTP requests to HTTPS; usually unnecessary behind a reverse proxy that already enforces TLS.
- **`SessionMiddleware`** — adds a signed cookie-based `request.session` dict; for server-rendered apps that don't want JWTs.

```python
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.example.com"])
```

## Custom middleware

Two ways to write custom middleware:

1. **`@app.middleware("http")` decorator** — quickest for simple cases; the function takes `(request, call_next)` and returns the response.
2. **Subclass `BaseHTTPMiddleware`** — required when you need an `__init__` for config, or when you want to share middleware across multiple apps.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class RequireApiKey(BaseHTTPMiddleware):
    def __init__(self, app, expected_key: str):
        super().__init__(app)
        self.expected_key = expected_key

    async def dispatch(self, request, call_next):
        if request.headers.get("x-api-key") != self.expected_key:
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "missing api key"}, status_code=401)
        return await call_next(request)

app.add_middleware(RequireApiKey, expected_key=settings.api_key)
```

When middleware logic is route-specific or per-user, use a dependency instead — middleware fires for every request including `/docs` and `/openapi.json`, which is rarely what you want for auth.
