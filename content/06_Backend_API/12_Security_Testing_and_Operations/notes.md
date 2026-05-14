# Security, Testing, and Operations

The last stage of backend API maturity is operational discipline. A service that has clean routes but weak secrets, no contract tests, and no deploy visibility is still fragile in production.

## Key Points

- **Validate input and protect secrets** - Boundary hygiene and secret management are baseline security work.
- **Use least privilege** - Application components should not have broader access than necessary.
- **Test at multiple levels** - Unit and integration tests catch different classes of failure.
- **Contract testing protects consumers** - Schema and status-code drift can break clients even when the server "works."
- **Observability is part of operability** - Logs, metrics, traces, and health endpoints make production behavior understandable.
- **CI/CD reduces release risk** - Automated checks, migration steps, and smoke tests turn deployment into a repeatable process.

## Example

A production readiness checklist for a backend API — the operational surface beyond just working code:

```text
Security:
  ✓ All secrets in environment variables or secret manager
  ✓ Parameterized queries (no string concatenation in SQL)
  ✓ Input validation on every endpoint
  ✓ CORS restricted to known origins
  ✓ Rate limiting on auth endpoints (5/min per IP)
  ✓ Least-privilege DB user (no DROP, no GRANT)

Testing:
  ✓ Unit tests for business logic (calculate_total, apply_discount)
  ✓ Integration tests for each endpoint (status codes + response shape)
  ✓ Contract tests for error responses (422 body matches spec)
  ✓ Auth tests (401 without token, 403 wrong role)

Operations:
  ✓ GET /health returns {"status": "ok", "db": "up", "cache": "up"}
  ✓ Structured JSON logs with request_id, user_id, duration
  ✓ Metrics: request count, latency p50/p99, error rate
  ✓ CI pipeline: lint → test → build → deploy → smoke test
  ✓ Rollback plan: revert to previous container image

Deployment:
  ✓ Environment-specific config (dev/staging/prod) via env vars
  ✓ Database migrations run before traffic is served
  ✓ Smoke test: POST /health after deploy, verify 200
  ✓ Error tracking (Sentry) alerts on new exceptions
```

Each item is a small piece of work, but together they are the difference between "it works on my machine" and "it runs reliably in production."
