# Deployment and Production

How the code you've been developing actually serves real traffic — workers, containers, reverse proxies, TLS, and managed infrastructure.

## Key Points

- **ASGI process model** — multiple worker processes for parallelism (`--workers N` or Gunicorn with `UvicornWorker`); no `--reload` in production.
- **Docker** — deterministic image, same artifact runs everywhere; `docker-compose` for local multi-service stacks only.
- **Reverse proxy** — Nginx/Caddy/Traefik in front for TLS, static files, rate limiting; configure `--proxy-headers` so the app sees the real client IP and scheme.
- **HTTPS/TLS** — Let's Encrypt is free and automated; never run a public API over plain HTTP.
- **Managed platforms** — Render, Fly.io, Cloud Run for most small/medium apps; defer Kubernetes until you have a reason.
- **Managed databases** — always; never self-host Postgres unless you can dedicate someone to operating it.
- **Production secrets** — platform secret store, not committed `.env`; required fields with no default make the app fail fast on misconfiguration.
- **Pydantic v2 migration** — use `bump-pydantic` codemod, then fix what it misses (custom validators, settings imports).

## Example

A production-ready Dockerfile and a Fly.io deployment for a FastAPI app with a managed Postgres database:

```dockerfile
# Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8000
# --proxy-headers makes request.client.host reflect the real client behind Fly's proxy.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--proxy-headers"]
```

```toml
# fly.toml
app = "my-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[services.tcp_checks]]
  interval = "15s"
  timeout = "2s"
  grace_period = "10s"
```

```bash
# Bootstrap secrets and a managed database (one time)
fly secrets set APP_JWT_SECRET=$(openssl rand -hex 32)
fly postgres create --name my-api-db
fly postgres attach my-api-db    # sets APP_DATABASE_URL automatically
fly secrets set APP_ENV=production APP_SENTRY_DSN="https://..."

# Deploy
fly deploy

# Run migrations in CI/CD or via fly ssh
fly ssh console -C "alembic upgrade head"
```

What this gets you for free:

- TLS terminated at Fly's edge, automatic Let's Encrypt certs for the custom domain.
- Four Uvicorn workers per VM, auto-restart on crash.
- A managed Postgres with daily backups.
- Secrets stored encrypted, injected as env vars at runtime — never in source.
- Multi-region deployment by adding `fly regions add ord` and scaling.

When Fly stops fitting (specialized networking, advanced traffic routing, GPU workloads), move the same Dockerfile to ECS/Fargate or Cloud Run without rewriting the app.
