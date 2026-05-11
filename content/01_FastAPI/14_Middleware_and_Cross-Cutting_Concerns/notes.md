# Middleware and Cross-Cutting Concerns

How to attach behavior that wraps every (or nearly every) request without polluting individual route handlers.

## Key Points

- **Middleware** wraps the whole route stack; runs in registration order on the request and reverse order on the response.
- **CORS** is browser-only and opt-in via headers; `CORSMiddleware` configures the policy. `allow_origins=["*"]` and `allow_credentials=True` are mutually exclusive by spec.
- **Built-in middleware** for GZip, trusted-host enforcement, HTTPS redirect, and session cookies.
- **Custom middleware** via `@app.middleware("http")` for quick cases or `BaseHTTPMiddleware` subclass when you need configuration.
- **Middleware vs dependency** — middleware runs for everything (including `/docs`); use a dependency for route-specific cross-cutting logic.

## Example

A small middleware stack covering response timing, request-time gzip, CORS for a separate frontend, and a custom API-key guard:

```python
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import get_settings

settings = get_settings()
app = FastAPI()


# 1. Built-in: compress JSON responses over 1 KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 2. Built-in: allow the SPA at app.example.com to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    allow_credentials=True,
)


# 3. Custom: timing header on every response
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-process-time"] = f"{time.perf_counter() - start:.3f}"
    return response


# 4. Custom class-based: require an API key on non-doc routes
class RequireApiKey(BaseHTTPMiddleware):
    def __init__(self, app, expected_key: str, exempt_paths: set[str]):
        super().__init__(app)
        self.expected_key = expected_key
        self.exempt_paths = exempt_paths

    async def dispatch(self, request, call_next):
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        if request.headers.get("x-api-key") != self.expected_key:
            return JSONResponse({"error": "missing api key"}, status_code=401)
        return await call_next(request)


app.add_middleware(
    RequireApiKey,
    expected_key=settings.jwt_secret,    # placeholder
    exempt_paths={"/docs", "/openapi.json", "/health"},
)


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/books")
async def list_books():
    return [{"id": 1, "title": "Example"}]
```

Order of middleware effect on a request to `/books`:
1. `RequireApiKey` checks the header; rejects with 401 if missing.
2. `add_process_time_header` records the start time.
3. `CORSMiddleware` handles preflight/origin checks.
4. `GZipMiddleware` decides whether to compress the eventual response.
5. The route handler runs and returns the list.
6. The middleware stack unwinds in reverse — gzip applies if response is large enough, CORS headers are added, `x-process-time` is set, the response goes out.

`/health` and `/docs` skip the API-key check via `exempt_paths`, so they remain reachable for load balancers and developers.
