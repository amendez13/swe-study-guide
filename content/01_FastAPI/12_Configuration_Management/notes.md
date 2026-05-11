# Configuration Management

How to keep environment-specific values (DB URL, secrets, feature flags) out of source code while still having them typed, validated, and easy to override in tests.

## Key Points

- **`BaseSettings`** — typed config loaded from env vars and `.env` files; lives in `pydantic-settings` since Pydantic v2.
- **`env_prefix`** — namespacing avoids collisions with other env vars (`APP_DATABASE_URL` vs `DATABASE_URL`).
- **Environment-specific configs** — `.env.dev`, `.env.test`, `.env.prod` selected by an `APP_ENV` flag; same image, different env values.
- **Settings as a dependency** — `Depends(get_settings)` makes settings overridable in tests via `app.dependency_overrides`.
- **`lru_cache`** — wrap the settings factory so env vars are parsed once per process, not per request.
- **Secrets stay out of source** — required fields with no default mean the app fails fast if a secret is missing; production secrets come from the platform's secret store.

## Example

A complete settings setup wired through dependency injection:

```python
# app/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )
    env: str = "dev"
    database_url: str         # required
    jwt_secret: str           # required
    debug: bool = False
    workers: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```python
# app/main.py
from fastapi import Depends, FastAPI
from app.config import Settings, get_settings

app = FastAPI()


@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "env": settings.env,
        "debug": settings.debug,
        # never return secrets:
        # "jwt_secret": settings.jwt_secret  ← absolutely not
    }
```

```bash
# .env (local dev only, gitignored)
APP_DATABASE_URL=postgresql://localhost/myapp_dev
APP_JWT_SECRET=dev-only-not-for-prod
APP_DEBUG=true
```

```python
# tests/conftest.py
import pytest
from app.config import Settings, get_settings
from app.main import app

@pytest.fixture
def test_settings():
    return Settings(
        env="test",
        database_url="sqlite:///:memory:",
        jwt_secret="test-secret",
    )

@pytest.fixture(autouse=True)
def override_settings(test_settings):
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield
    app.dependency_overrides.clear()
```

In production the platform supplies `APP_DATABASE_URL` and `APP_JWT_SECRET` from its secret store — no `.env` file is deployed. If either is missing, `Settings()` raises a `ValidationError` at import time and the process exits.
