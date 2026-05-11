## Production ASGI process model

In dev, `uvicorn app:app --reload` runs one worker with auto-reload — fine for a single developer. In production you want multiple worker processes for CPU parallelism, no auto-reload, and a process supervisor that restarts dead workers.

Two common shapes:

```bash
# Uvicorn standalone with worker processes
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn process manager + Uvicorn worker class (older, battle-tested)
gunicorn app:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

Rule of thumb: workers ≈ (2 × CPU cores) + 1 for I/O-bound apps; equal to CPU cores for CPU-bound ones. Each worker is a separate process with its own memory — share-nothing concurrency.

## Docker

Package the app and its dependencies into a deterministic image. Same image runs everywhere — dev, staging, prod — eliminating "works on my machine" failures.

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

For multi-service local stacks (API + Postgres + Redis), `docker-compose.yml` wires them together:

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      APP_DATABASE_URL: postgresql://app:secret@db/app
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: secret
```

Production typically uses the Dockerfile but not docker-compose — orchestration moves to Kubernetes, ECS, or a managed PaaS.

## Reverse proxy

Don't expose Uvicorn directly to the internet. Put **Nginx** (or Caddy, Traefik) in front for TLS termination, static file serving, rate limiting, and request buffering against slow clients.

```nginx
# nginx config sketch
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Behind a proxy, configure FastAPI with `--proxy-headers` and `--forwarded-allow-ips` (or the equivalent in Gunicorn) so `request.client.host` and `request.url.scheme` reflect the real client, not the proxy's loopback address.

## HTTPS / TLS

Never run a public API over plain HTTP. **Let's Encrypt** provides free, auto-renewing certificates via Certbot or built into tools like Caddy/Traefik (which fetch and renew automatically).

```bash
# Certbot — one-shot manual issuance
sudo certbot --nginx -d api.example.com

# Caddy — TLS is automatic; just declare the domain
api.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Most managed platforms (Render, Fly.io, Vercel, Cloudflare) terminate TLS at the load balancer and forward to your app over plain HTTP inside their network — that's fine, just check that headers (`X-Forwarded-Proto`) are set correctly so OAuth callbacks and absolute URLs reflect HTTPS.

## Managed platforms

For a typical FastAPI app, a managed platform deploys faster than rolling your own infrastructure. The big three classes:

- **PaaS** — Render, Fly.io, Railway, Heroku-style. Push a Dockerfile or buildpack, get a managed app with TLS, logs, env vars, and rollback. Best ergonomics-per-cost for small/medium apps.
- **Container orchestration** — AWS ECS/Fargate, GCP Cloud Run, Azure Container Apps. More control over networking, secrets, and scaling rules.
- **Kubernetes** — AWS EKS, GCP GKE, self-hosted. Maximum control, maximum operational complexity.

Pick the simplest tier that meets your needs. A FastAPI app that earns $0–$1M ARR rarely outgrows Render or Fly; defer Kubernetes until you have a real reason.

## Managed databases

Same logic applies to the database: managed Postgres/MySQL (AWS RDS, GCP Cloud SQL, Render Postgres, Neon, Supabase) is almost always the right call over self-hosting. The provider handles backups, point-in-time recovery, version upgrades, monitoring, and failover.

The connection-string change from local Postgres to managed is one line:

```
APP_DATABASE_URL=postgresql://user:pass@db.example.com:5432/myapp
```

Two production rules: **always have automated backups verified by periodic restore tests**, and **never run migrations from a developer's laptop** — they go through CI/CD with reviewed, version-controlled scripts.

## Environment variables in production

Secrets — DB URLs, API keys, JWT signing keys — come from the platform's secret store, not from a committed `.env` file. Every modern platform has this: Render env vars, Fly secrets, Heroku config vars, AWS Secrets Manager, GCP Secret Manager, Kubernetes Secrets.

```bash
# Fly.io
fly secrets set APP_JWT_SECRET=$(openssl rand -hex 32)
fly secrets set APP_DATABASE_URL="postgresql://..."

# Render — set in the dashboard or via API
# Kubernetes — kubectl create secret generic app-secrets --from-literal=...
```

Rotate secrets periodically and on any suspected compromise. The reason `BaseSettings` makes secret fields required (no default) is to force a fail-fast crash on misconfiguration rather than a quiet startup with empty secrets.

## Pydantic v2 migration

If you inherited a Pydantic v1 codebase, plan the migration deliberately rather than letting it block adopting newer libraries that require v2.

The codemod path:

1. Pin `pydantic==1.x` and add `pydantic` to your test matrix so the suite still runs.
2. Install `bump-pydantic` (Pydantic team's tool) — runs an AST codemod that converts most v1 patterns to v2.
3. Replace `model.dict()` → `model.model_dump()`, `Model.parse_obj()` → `Model.model_validate()`, `@validator` → `@field_validator`, `class Config` → `model_config = ConfigDict(...)`.
4. Move settings: `pip install pydantic-settings` and import `BaseSettings` from there.
5. Run tests, fix remaining breakage (mostly around custom validators with `pre=True`/`always=True` semantics).

Allocate a day or two; bigger codebases will surface edge cases in custom validators and `root_validator` chains.
