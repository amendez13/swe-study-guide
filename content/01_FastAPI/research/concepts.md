# FastAPI Concepts

A distilled concept reference for a student of FastAPI, synthesized from the five course outlines in [course_outlines.md](course_outlines.md). Each item names a concept worth being able to explain, recognize in code, and apply in practice. Setup logistics (installing Python, choosing an IDE, generic Git usage) are excluded — the focus is on durable FastAPI, REST, and web-framework knowledge.

---

## 1. Framework Foundations

- **ASGI vs WSGI** — FastAPI is built on the Asynchronous Server Gateway Interface, which is what makes async path operations and concurrent I/O possible.
- **The `FastAPI` application instance** — the root object that holds the route table, middleware stack, and OpenAPI metadata.
- **Uvicorn (and Hypercorn)** — the ASGI server that actually runs the FastAPI app; `--reload` for dev, multiple workers for production.
- **Starlette under the hood** — FastAPI extends Starlette for the HTTP machinery (requests, responses, middleware, websockets).
- **Pydantic under the hood** — FastAPI uses Pydantic models for request/response schemas and validation; understand this is not optional infrastructure but the core data contract.
- **Auto-generated OpenAPI schema** — every route, parameter, model, and response is reflected into an OpenAPI 3 document served at `/openapi.json`.
- **Swagger UI at `/docs` and ReDoc at `/redoc`** — interactive docs generated for free from the OpenAPI schema.
- **Type hints as the API contract** — Python type hints drive validation, serialization, and documentation simultaneously.

## 2. HTTP and REST

- **REST as resource-oriented design** — URLs name resources (nouns), HTTP methods name actions (verbs), state is not held on the server.
- **CRUD ↔ HTTP method mapping** — Create/POST, Read/GET, Update/PUT, Delete/DELETE; PATCH for partial updates.
- **Idempotency** — GET, PUT, DELETE are idempotent; POST is not. Matters for retries and caching.
- **Status code classes** — 1xx informational, 2xx success, 3xx redirection, 4xx client error, 5xx server error.
- **Commonly used codes** — 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 500 Internal Server Error.
- **Request/response anatomy** — method, path, query string, headers, body on the request side; status, headers, body on the response side.
- **Content negotiation** — `Content-Type` and `Accept` headers; FastAPI defaults to JSON.
- **Less common methods** — OPTIONS (preflight, capability discovery), HEAD, TRACE, CONNECT.

## 3. Path Operations and Routing

- **Path operation decorators** — `@app.get`, `@app.post`, `@app.put`, `@app.delete`, `@app.patch`, etc., bind a function to a method/path pair.
- **Path operation function signature** — parameter types in the function signature determine what FastAPI parses from path, query, body, headers, and dependencies.
- **Route declaration order matters** — static routes (`/books/mybook`) must be declared before dynamic routes (`/books/{title}`), otherwise the dynamic route swallows the static one.
- **`APIRouter` for modular routing** — split routes across files by domain (users, posts, comments) and mount them on the main app with `app.include_router()`.
- **Router prefixes and tags** — group related endpoints with a shared URL prefix and Swagger tag for organization.
- **Multiple apps and sub-applications** — mounting one FastAPI app inside another for versioning or feature isolation.

## 4. Request Parameters

- **Path parameters** — values embedded in the URL (`/books/{id}`); typed via function signature, automatically converted and validated.
- **Query parameters** — `name=value` pairs after `?`; declared as function arguments with defaults to mark them optional.
- **Required vs optional parameters** — absence of a default means required; `Optional[T]` or `T | None = None` marks optional.
- **Request body** — declared by typing a parameter as a Pydantic model; FastAPI parses JSON and validates against the schema.
- **Form data** — `Form(...)` for `application/x-www-form-urlencoded` and `multipart/form-data` bodies (used with HTML forms).
- **File uploads** — `UploadFile` and `File()` for multipart file uploads; stream large files instead of loading into memory.
- **Headers and cookies** — `Header()` and `Cookie()` to declare them as typed parameters.
- **`Path()`, `Query()`, `Body()`** — explicit parameter markers used to attach metadata, validators, examples, and titles.

## 5. Pydantic Data Modeling

- **`BaseModel`** — declarative class for typed, validated data; subclass to define schemas.
- **`Field()` validators** — declarative constraints: `min_length`, `max_length`, `gt`/`ge`/`lt`/`le`, `regex`/`pattern`, `default`, `description`, `examples`.
- **Type coercion** — Pydantic converts compatible inputs (e.g. `"3"` → `3`) and rejects incompatible ones.
- **Optional and default values** — `Optional[T]` for nullable, defaults make a field non-required.
- **Nested models** — models containing other models, serialized recursively.
- **Pydantic v1 vs v2** — v2 is a Rust-backed rewrite with breaking changes (`model_dump`, `model_validate`, new validator API); know that migrations exist.
- **Separate request and response models** — input model accepts what the client may set; output model controls what the API returns (and hides internals like password hashes).
- **`model_config` / Config class** — class-level options like `from_attributes` (`orm_mode`), `populate_by_name`, JSON schema extras.
- **Custom validators** — `@field_validator` / `@model_validator` for cross-field rules and computed checks.
- **Automatic 422 on validation failure** — FastAPI returns a structured validation error response by default.
- **Pydantic Settings (`BaseSettings`)** — same modeling power for application configuration loaded from environment variables.

## 6. Responses and Error Handling

- **`response_model`** — declares the output schema; filters and validates what the endpoint returns.
- **Explicit status codes** — `status_code=201` on the decorator or `status.HTTP_201_CREATED` constants from `fastapi.status`.
- **`HTTPException`** — the canonical way to abort a request with a specific status code and detail message.
- **Custom exception handlers** — `@app.exception_handler(SomeException)` to translate domain exceptions into HTTP responses uniformly.
- **`JSONResponse` and other response classes** — `HTMLResponse`, `PlainTextResponse`, `StreamingResponse`, `FileResponse`, `RedirectResponse` for non-JSON outputs.
- **Response headers and cookies** — set via the `Response` parameter or by returning a `Response` directly.

## 7. Async Programming

- **`async def` path operations** — required for awaiting async work (DB, HTTP clients) inside the handler.
- **Sync `def` path operations** — FastAPI runs them in a threadpool so blocking calls don't stall the event loop.
- **Concurrency model** — async lets a single worker handle many in-flight requests when work is I/O-bound.
- **When async hurts** — CPU-bound work in `async def` blocks the loop; offload to a threadpool or worker.
- **Async database drivers** — `asyncpg`, `aiomysql`, async SQLAlchemy 2.x; the whole stack must be async for async I/O to pay off.

## 8. Dependency Injection

- **`Depends()`** — declares that a parameter is computed by calling another function; FastAPI resolves the graph per request.
- **Reusable dependencies** — extract common logic (auth, pagination, DB session, settings) once and inject everywhere.
- **Sub-dependencies** — dependencies can themselves declare dependencies; FastAPI walks the tree.
- **Yielding dependencies** — `yield` lets a dependency run setup/teardown (open a DB session, ensure it closes).
- **Dependency overrides in tests** — `app.dependency_overrides[real_dep] = fake_dep` to swap real services for fakes.
- **Class-based dependencies** — any callable works, including class instances with `__call__`.

## 9. Database Integration

- **SQLAlchemy ORM (sync)** — declarative models, `Session`, `engine`, query API; the most common FastAPI database stack.
- **SQLAlchemy async (2.x)** — `AsyncSession`, `async_engine`; needed with `asyncpg` for async I/O.
- **SQLModel** — Pydantic + SQLAlchemy unified into a single model class (Tiangolo's library).
- **Database session per request** — open a session in a `Depends()` dependency, commit/rollback, close.
- **Lifespan events** — `lifespan` context manager on the app to initialize connection pools, ML models, etc., at startup.
- **Models, schemas, and tables** — keep ORM models (DB-shaped) separate from Pydantic schemas (API-shaped).
- **Relationships** — one-to-one, one-to-many, many-to-many; foreign keys; eager vs lazy loading.
- **Reusable queries** — encapsulate complex query logic in functions or repository classes, not in route handlers.
- **Database choice** — SQLite for dev/test, PostgreSQL/MySQL for production; identical API via SQLAlchemy.

## 10. Database Migrations

- **Why migrations** — schema evolves alongside code; running `Base.metadata.create_all()` only works on a fresh DB.
- **Alembic** — the standard migrations tool for SQLAlchemy.
- **Revisions** — each schema change is a versioned, reversible script with `upgrade()` and `downgrade()`.
- **Autogenerate** — `alembic revision --autogenerate` diffs models against the live DB to draft a migration.
- **`alembic upgrade head`** — applies pending migrations; runs in CI/CD before code that depends on the new schema.

## 11. Authentication and Authorization

- **Password hashing with bcrypt** — never store plaintext; use `passlib` or `bcrypt` to hash on registration, verify on login.
- **JWT (JSON Web Tokens)** — signed, base64url-encoded claims (header.payload.signature); stateless auth.
- **Token expiration (`exp`)** — short-lived access tokens limit blast radius if leaked; refresh tokens extend sessions.
- **OAuth2 Password Bearer flow** — username/password → access token; FastAPI ships first-class helpers for it.
- **`OAuth2PasswordBearer` and `OAuth2PasswordRequestForm`** — built-in dependencies for extracting and parsing credentials.
- **Current user dependency** — a `Depends(get_current_user)` that decodes the token, fetches the user, and is reused on every protected route.
- **Protected routes** — declare the current-user dependency; FastAPI rejects unauthenticated requests automatically.
- **Authorization vs authentication** — authentication answers "who are you?"; authorization answers "what may you do?".
- **Email confirmation tokens** — short-lived signed tokens for verifying email ownership before granting full access.

## 12. Configuration Management

- **Pydantic `BaseSettings`** — typed settings loaded from environment variables and `.env` files.
- **Environment-specific config** — separate `dev`, `test`, `prod` configs selected by an env var.
- **Settings as a dependency** — inject settings via `Depends(get_settings)` so tests can override them.
- **`lru_cache` on settings factory** — read env vars once per process, not per request.
- **Never hardcode secrets** — DB URLs, API keys, JWT signing secrets come from env, never from source.

## 13. Logging and Observability

- **Python `logging` module mental model** — `Logger` (named, hierarchical) → `Handler` (where logs go) → `Formatter` (how they look) → `Filter` (which records pass).
- **Logger hierarchies** — `logging.getLogger("app.auth")` inherits config from `app`; configure at the root and propagate.
- **Structured logging** — JSON output makes logs queryable in log aggregators (Logtail, Datadog, ELK).
- **Correlation IDs** — generate a request ID per incoming request, attach it to every log line for that request, propagate to downstream calls.
- **Custom filters** — e.g., redact email addresses or PII before logs leave the process.
- **Cloud log shipping** — adding a Logtail/Datadog/CloudWatch handler in production only.
- **Sentry for error tracking** — captures exceptions with stack traces, request context, and user info.

## 14. Middleware and Cross-Cutting Concerns

- **Middleware** — code that runs before and after every request; useful for logging, timing, auth headers, compression.
- **CORS middleware** — `CORSMiddleware` configures which origins, methods, and headers a browser may use; required when a separate frontend domain calls the API.
- **Built-in middleware** — GZip, trusted host, HTTPS redirect.
- **Custom middleware** — subclass `BaseHTTPMiddleware` or use the `@app.middleware("http")` decorator.

## 15. Background Tasks

- **FastAPI `BackgroundTasks`** — fire-and-forget work that runs after the response is sent (sending email, generating thumbnails).
- **When `BackgroundTasks` is enough** — short, in-process work that's OK to lose if the worker dies.
- **When you need a real queue** — durable jobs, retries, scheduled jobs, fanout: use Celery, Dramatiq, or arq with Redis/RabbitMQ.
- **Third-party integrations triggered by background tasks** — sending email through Mailgun, queuing image generation through DeepAI, etc.

## 16. File Uploads and Storage

- **`UploadFile`** — streams the upload to a `SpooledTemporaryFile`; doesn't load the whole file into memory.
- **Object storage** — Backblaze B2, S3, or similar; the API receives the upload and forwards it to durable storage, returning a URL.
- **Signed URLs** — let clients upload/download directly to/from object storage without proxying through the API.

## 17. Templates and Server-Rendered Frontends

- **Jinja2Templates** — server-side rendering of HTML responses from FastAPI; useful for admin pages and hypermedia frontends.
- **Static files** — `app.mount("/static", StaticFiles(directory="static"))` for CSS, JS, images.
- **Form-driven endpoints** — receiving HTML form posts as `Form()` parameters and returning rendered HTML.
- **HTMX / Hypermedia patterns** — return HTML fragments from FastAPI endpoints, swap them into the page; FastAPI is well-suited to this style.

## 18. Testing

- **`TestClient`** — Starlette's test client (wraps `requests`-style API) runs the app in-process; the standard way to test FastAPI.
- **pytest fundamentals** — discovery rules, `assert` rewriting, `-s`/`-v` flags, exit codes for CI.
- **Fixtures** — `@pytest.fixture` for reusable setup/teardown; scope (`function`, `module`, `session`) controls lifetime.
- **Parametrize** — `@pytest.mark.parametrize` runs the same test with many input/expected pairs.
- **Test database isolation** — spin up a fresh schema per test session, run each test in a transaction that's rolled back, or use SQLite in-memory.
- **Dependency overrides for tests** — swap real DB/auth/settings dependencies for fakes via `app.dependency_overrides`.
- **Monkeypatching** — `monkeypatch` fixture to replace functions or env vars for the duration of a test.
- **Unit vs integration vs system vs functional** — unit isolates one function, integration crosses module boundaries with real collaborators, system tests the deployed surface, functional tests user-facing behavior end to end.
- **Async tests** — `pytest-asyncio` for `async def` tests when exercising async code paths.

## 19. Deployment and Production

- **Production ASGI process model** — `uvicorn` workers, or `gunicorn` with `uvicorn.workers.UvicornWorker`; multiple workers for CPU parallelism.
- **Docker** — package the app and its dependencies into a deterministic image; `Dockerfile` builds the image, `docker-compose.yml` wires multi-service local stacks.
- **Reverse proxy** — Nginx (or Caddy/Traefik) in front of Uvicorn for TLS termination, static file serving, and rate limiting.
- **HTTPS/TLS** — Let's Encrypt for free certificates; never run a public API over plain HTTP.
- **Managed platforms** — Render, Fly.io, Railway, Heroku-style PaaS; AWS/GCP/Azure for more control.
- **Managed databases** — production PostgreSQL/MySQL hosting with backups and failover.
- **Environment variables in production** — secrets via the platform's secret store, not committed `.env` files.
- **Pydantic v2 migration** — codemod from v1 (`@validator`, `dict()`) to v2 (`@field_validator`, `model_dump()`); know that v2 changed behavior.

## 20. CI/CD

- **CI pipeline goals** — run linting, type checking, tests, security scans on every push and PR before merge.
- **GitHub Actions for Python** — `actions/setup-python`, matrix builds, caching pip, running pytest.
- **CD pipeline goals** — on merge to main, build the image, run migrations, deploy a new revision automatically.
- **Migrations in CI/CD** — `alembic upgrade head` runs before the new code starts serving requests.
- **Smoke tests post-deploy** — hit `/health` and a couple of representative endpoints to confirm the rollout is live.

---

## How to use this list

This isn't a syllabus — it's a self-check. Pick any concept and ask:

1. Can I explain what it is in two sentences without looking it up?
2. Can I recognize it in unfamiliar FastAPI code?
3. Can I write a small example that uses it correctly?

A "no" on any of those three is a topic to study next.
