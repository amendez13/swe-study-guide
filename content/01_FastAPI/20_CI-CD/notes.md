# CI/CD

How merging to `main` turns into "running in production" without anyone running a command by hand.

## Key Points

- **CI goals** — lint, type check, test, security scan, coverage gate on every push and PR.
- **GitHub Actions** — `setup-python` with pip cache, matrix builds over Python versions, `pre-commit` and `pytest` as the workhorses.
- **CD goals** — build once, migrate before code rollout, deploy atomically.
- **Migrations** — `alembic upgrade head` runs **before** the new app version starts; backwards-incompatible changes need two coordinated releases.
- **Smoke tests** — shallow post-deploy checks (`/health`, key endpoints) to catch catastrophes that the test suite missed.
- **Health endpoint** — every service exposes `/health` for load balancers and uptime monitors.

## Example

A two-workflow GitHub Actions setup: `ci.yml` runs on every PR, `deploy.yml` runs after a green merge to `main`.

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.11", "3.12"]
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: ci
          POSTGRES_PASSWORD: ci
          POSTGRES_DB: ci
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql://ci:ci@localhost:5432/ci
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pre-commit run --all-files
      - run: pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    concurrency: deploy-prod    # never two deploys at once
    steps:
      - uses: actions/checkout@v4

      # 1. Build the image once
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only --build-only --image-label=${{ github.sha }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      # 2. Migrate the database (against the new image, against prod DB)
      - run: flyctl ssh console -C "alembic upgrade head"
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      # 3. Roll out the new image
      - run: flyctl deploy --remote-only --image registry.fly.io/my-api:${{ github.sha }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      # 4. Smoke test
      - name: Smoke test
        run: |
          set -e
          for i in 1 2 3 4 5; do
            sleep 5
            if curl -fsS https://api.example.com/health | grep -q '"ok":true'; then
              exit 0
            fi
          done
          echo "Smoke test failed — rolling back"
          flyctl releases rollback
          exit 1
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

The contract:

- A red CI run blocks the PR — no merging.
- A merge to `main` triggers a deploy, but only after CI has gone green on the merge commit itself.
- The deploy builds once, migrates, rolls out, then smoke-tests. Any failure rolls back automatically.
- The whole loop from "merge" to "live and verified" is hands-off; the rare manual override is `flyctl releases rollback` if a bug slips past smoke tests into the wild.
