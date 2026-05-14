## Input sanitization and secret handling

Backend APIs must treat incoming data and operational secrets as distinct security concerns. Requests need validation and sanitization so malformed or malicious input does not flow unchecked into storage or downstream systems, while credentials and signing keys need controlled storage outside source code.

These are foundational controls, not optional hardening. Many production incidents start with weak boundary handling or poor secret hygiene.

```text
Common input attacks and defenses:

  Attack              Defense
  ──────────────────  ──────────────────────────────────────
  SQL injection       Parameterized queries (never string concat)
  XSS                 Escape HTML output, Content-Security-Policy
  Command injection   Avoid shell=True; validate/allowlist inputs
  Path traversal      Reject ../ in file paths; use allowlists

Secret management:
  Bad:   DB_URL = "postgres://admin:password@host/db"  (in source code)
  Bad:   .env file committed to git
  Good:  DB_URL from environment variable or secret manager
  Good:  AWS Secrets Manager, HashiCorp Vault, Doppler
  Rule:  If it grants access, it belongs in a secret store, not in code.
```

## Least privilege and operational access

Every component in the system should have only the permissions it actually needs. Application services, background workers, and database users should not receive broad access just because it is convenient during setup.

Least privilege reduces blast radius. If one component is compromised or misconfigured, the damage stays smaller and easier to contain.

Example: the read-only reporting job should not have permission to delete invoices.

## Unit and integration testing

Unit tests isolate small pieces of logic, while integration tests verify that the API surface, validation, persistence, and auth work together. Both matter because APIs fail at both levels: bad pure logic and bad system wiring.

A strong test strategy uses the cheapest level that can prove the thing you care about, then adds deeper tests where boundaries or critical workflows justify them.

```text
Testing pyramid for a backend API:

        /  E2E  \        Few — slow, fragile, prove the full flow
       / ─────── \
      / Integration\     Some — prove routes + DB + auth together
     / ───────────── \
    /    Unit tests    \  Many — fast, isolated, prove business logic
   ─────────────────────

Unit:         assert calculate_total(100, tax=0.2) == 120
Integration:  POST /orders → assert 201 + row exists in DB
E2E:          Sign in → create order → verify email sent
```

## Contract testing

Contract tests verify not only that a route returns success but that it returns the expected schema, status codes, and error shapes. This is especially important when multiple clients or teams depend on the same API.

For backend APIs, contract drift is often a bigger risk than simple algorithm bugs. A test suite that ignores payload shape can miss client-breaking changes completely.

```python
def test_create_order_contract():
    response = client.post("/orders", json={"customerId": 7, "items": [{"sku": "X", "quantity": 1}]})

    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["status"] == "created"
    assert isinstance(body["id"], int)

def test_create_order_validation_contract():
    response = client.post("/orders", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert any(d["field"] == "customerId" for d in body["details"])
```

## Observability and health

Logs, metrics, traces, and health endpoints are part of operating an API safely. They let engineers answer "is it working?", "what is slow?", and "what broke for this request?" without attaching a debugger to production.

Observability is part of the contract with operators. An API that functions only when a specific engineer is awake is not production-ready.

```text
Pillar     What it answers             Example
─────────  ──────────────────────────  ──────────────────────────────
Logs       What happened?              "Order 42 created by user 7"
Metrics    How much / how fast?        p99 latency = 120ms, 5xx rate = 0.1%
Traces     Where did time go?          request → auth (2ms) → DB (45ms) → response
Health     Is the service ready?       GET /health → {"status": "ok", "db": "up"}

Health endpoint with dependency checks:
  GET /health
  200 OK  {"status": "ok", "db": "connected", "cache": "connected"}

  GET /health
  503 Service Unavailable  {"status": "degraded", "db": "connected", "cache": "timeout"}
```

## CI/CD and production readiness

Reliable backend delivery depends on automated checks such as linting, tests, migration steps, and deploy smoke tests. The deployment process should be repeatable enough that shipping a change is routine rather than improvisational.

Production readiness also includes rollback paths, error tracking, and environment-specific configuration. The code is only one part of the system that has to work.

```mermaid
flowchart LR
    A[Commit] --> B[CI checks]
    B --> C[Build artifact]
    C --> D[Deploy]
    D --> E[Smoke checks]
    E --> F[Serve traffic]
```
