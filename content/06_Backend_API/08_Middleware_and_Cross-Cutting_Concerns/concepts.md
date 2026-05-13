## Middleware as a request pipeline

Middleware is code that runs around request handling, usually before the main handler and again after it returns. It is the standard place to apply behavior that should affect many routes consistently.

This is useful because some concerns do not belong to one endpoint. Logging, authentication extraction, tracing, and response timing are request-wide responsibilities.

## Cross-cutting concerns

Cross-cutting concerns are behaviors that matter across the whole API rather than within one use case. Examples include logging, correlation IDs, compression, CORS, and request metrics.

Treating these as shared infrastructure instead of copying them into handlers reduces duplication and makes policy changes easier to apply consistently.

## Correlation IDs and request context

A correlation ID is a per-request identifier attached to logs, traces, and often downstream calls. It lets operators reconstruct the story of one request in a high-volume system.

Without request context, logs from concurrent traffic blur together. Correlation is what makes distributed debugging tractable once more than one service or worker is involved.

## CORS and cross-domain policy

Browser clients are subject to cross-origin rules that non-browser clients do not have. CORS configuration tells the browser which origins, methods, and headers may access the API.

This is why an endpoint can work perfectly in `curl` and still fail from a web frontend. The API may be correct functionally but misconfigured for browser security policy.

## Shared response policies

Some response behavior should be applied consistently across many endpoints, such as compression, cache headers, request timing headers, or a standard error envelope.

Putting those behaviors in middleware or other shared hooks keeps them from being reimplemented slightly differently on each route.

## Framework hooks for common behavior

Different stacks expose different hook points: Express uses middleware functions, FastAPI uses middleware and dependencies, Spring uses filters and interceptors. The syntax changes, but the design goal stays the same.

Learning the concept instead of memorizing only framework APIs makes it easier to move between backend ecosystems.
