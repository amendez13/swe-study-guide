## CI pipeline goals

Continuous Integration runs the same automated checks on every push and PR before code can be merged. The goals are simple and non-negotiable:

1. **Lint and format** — `black`, `isort`, `flake8`, `mypy`. Catch style and type drift before reviewers waste time on it.
2. **Tests** — `pytest`, including DB-integrated tests against a fresh fixture database.
3. **Security scans** — `bandit` for code-level issues, `pip-audit` for known-vulnerable dependencies, secret scanning (`gitleaks`) for committed credentials.
4. **Coverage gate** — minimum coverage threshold (e.g. 90%) so untested code can't sneak in.

A good CI run finishes in under 10 minutes on a representative PR. Anything slower and developers start working around it.

## GitHub Actions for Python

GitHub Actions is the default CI for Python projects on GitHub. A minimal FastAPI workflow:

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
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pre-commit run --all-files
      - run: pytest --cov=app --cov-fail-under=90
```

Key building blocks:

- **`actions/checkout@v4`** — pulls the repo into the runner.
- **`actions/setup-python@v5`** with `cache: pip` — installs Python and caches pip's wheel cache by `requirements*.txt` hash.
- **Matrix builds** — run the same job across Python versions or OSes; one job per cell.
- **Reusable workflows / composite actions** — when the file gets too long, extract steps into a `workflow_call` workflow.

## CD pipeline goals

Continuous Delivery (or Deployment) takes a green commit on `main` and ships it. The bar is "every merge is deployable, deploys happen automatically." Three things must be true:

1. **Build the artifact once** — same Docker image promoted through environments; never rebuild between staging and prod.
2. **Migrate the database before code rolls out** — `alembic upgrade head` runs as a step before the new app version starts serving traffic.
3. **Roll out atomically** — old and new versions of the code only overlap when the schema supports both; otherwise drain old, deploy new.

The mental model: CI proves "this build is correct"; CD makes "correct build" automatically become "running in production."

## Migrations in CI/CD

The hardest part of CD for a stateful service. Two rules cover most cases:

1. **Always run `alembic upgrade head` before the new app version starts.** The new code can rely on the schema being current.
2. **For backwards-incompatible schema changes, deploy in two phases.** Phase 1: ship code that works with both old and new schema, then migrate. Phase 2: ship code that only uses the new schema and drop the old columns.

Example two-phase column rename (`title` → `name`):

```
Phase 1 (current release):
  - Add `name` column (nullable, populated on write to both columns)
  - Code writes to both, reads from `title` preferentially
  - Migrate: backfill name = title

Phase 2 (next release):
  - Code reads from `name`, ignores `title`
  - Migrate: drop `title`
```

This sequence means there's never a moment when the running code disagrees with the running schema — even mid-rollout with two app versions live.

## Smoke tests post-deploy

After a deploy completes, run a handful of representative requests to confirm the new version is actually serving correctly. Failures here trigger an automatic rollback.

```yaml
# In the deploy job, after `fly deploy`
- name: Smoke test
  run: |
    set -e
    curl -fsS https://api.example.com/health | grep -q '"ok":true'
    curl -fsS https://api.example.com/openapi.json | jq -e '.info.version' > /dev/null
    # Maybe a couple of read-only auth-required endpoints with a test token
```

Smoke tests are deliberately shallow — they catch "the new version doesn't start" or "I forgot to set an env var," not subtle business bugs. Subtle bugs are what the test suite is for; smoke tests catch the catastrophes that slip past it.

Pair smoke tests with a real **health endpoint** in the app (`/health` returning `{"ok": true}`, optionally with DB/cache pings) so load balancers and uptime monitors can poll it cheaply.
