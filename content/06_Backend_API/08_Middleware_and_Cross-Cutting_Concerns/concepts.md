## Middleware as a request pipeline

Middleware is code that runs around request handling, usually before the main handler and again after it returns. It is the standard place to apply behavior that should affect many routes consistently.

This is useful because some concerns do not belong to one endpoint. Logging, authentication extraction, tracing, and response timing are request-wide responsibilities.

```mermaid
flowchart LR
    A[Request] --> B[Logging middleware]
    B --> C[Auth middleware]
    C --> D[Route handler]
    D --> E[Response middleware]
    E --> F[Client]
```

## Cross-cutting concerns

Cross-cutting concerns are behaviors that matter across the whole API rather than within one use case. Treating these as shared infrastructure instead of copying them into handlers reduces duplication and makes policy changes easier to apply consistently.

```text
Concern               Where it lives             What it does
────────────────────  ─────────────────────────  ──────────────────────────
Request logging       Middleware (before)         Log method, path, timestamp
Correlation ID        Middleware (before)         Attach X-Request-ID
Authentication        Middleware (before)         Extract and verify token
CORS                  Middleware (before/after)   Add Access-Control headers
Compression           Middleware (after)          Gzip response body
Response timing       Middleware (after)          Add X-Response-Time header
Error envelope        Exception handler          Wrap errors in standard shape
```

## Correlation IDs and request context

A correlation ID is a per-request identifier attached to logs, traces, and often downstream calls. It lets operators reconstruct the story of one request in a high-volume system.

Without request context, logs from concurrent traffic blur together. Correlation is what makes distributed debugging tractable once more than one service or worker is involved.

```http
X-Request-ID: 8e5d3f0a-3d8f-4d7e-a9ab-40a5b7b2a816
```

## CORS and cross-domain policy

Browser clients are subject to cross-origin rules that non-browser clients do not have. CORS configuration tells the browser which origins, methods, and headers may access the API.

This is why an endpoint can work perfectly in `curl` and still fail from a web frontend. The API may be correct functionally but misconfigured for browser security policy.

```http
# Browser sends a preflight request before the actual PATCH:
OPTIONS /orders/42 HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: Authorization, Content-Type

# Server responds with what's allowed:
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 3600

# Browser sees PATCH is allowed → sends the actual request.
```

## Shared response policies

Some response behavior should be applied consistently across many endpoints, such as compression, cache headers, request timing headers, or a standard error envelope.

Putting those behaviors in middleware or other shared hooks keeps them from being reimplemented slightly differently on each route.

Example: adding `X-Response-Time` on every response is a better middleware concern than a handler concern.

## Framework hooks for common behavior

Different stacks expose different hook points: Express uses middleware functions, FastAPI uses middleware and dependencies, Spring uses filters and interceptors. The syntax changes, but the design goal stays the same.

Learning the concept instead of memorizing only framework APIs makes it easier to move between backend ecosystems.

```text
Express      -> app.use(...)
FastAPI      -> @app.middleware("http")
Spring Boot  -> OncePerRequestFilter
```
