## Pydantic `BaseSettings`

`BaseSettings` from the `pydantic-settings` package gives you typed, validated configuration loaded from environment variables and optional `.env` files. Same modeling power as `BaseModel`, plus environment-aware loading.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )
    database_url: str
    jwt_secret: str
    debug: bool = False
    workers: int = 4
```

With `env_prefix="APP_"`, FastAPI looks for `APP_DATABASE_URL`, `APP_JWT_SECRET`, etc. Field types are enforced — `APP_WORKERS=four` raises a validation error at startup, not on the first request that needs it.

Note: in Pydantic v2, `BaseSettings` moved out of the main package into `pydantic-settings`. Install it explicitly.

## Environment-specific config

Separate `dev`, `test`, and `prod` configs that differ on database URL, log level, debug flag, third-party API endpoints, and feature flags. Select between them with an `APP_ENV` (or `ENVIRONMENT`) environment variable.

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    env: str = "dev"
    database_url: str
    debug: bool = False

# Load a different .env per environment
import os
env = os.getenv("APP_ENV", "dev")
settings = Settings(_env_file=f".env.{env}")
```

The same code runs in every environment; only the env vars differ. This is what makes "build once, deploy anywhere" work — the same Docker image goes to staging and prod with different `APP_DATABASE_URL` values.

## Settings as a dependency

Don't import a module-level settings singleton everywhere — that hardcodes the global into every consumer. Instead, expose settings via `Depends(get_settings)` so tests can override them with `app.dependency_overrides`.

```python
def get_settings() -> Settings:
    return Settings()

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"env": settings.env, "debug": settings.debug}

# In tests
def fake_settings() -> Settings:
    return Settings(env="test", database_url="sqlite:///:memory:")

app.dependency_overrides[get_settings] = fake_settings
```

This is the same pattern as the database session: inject what's environment-dependent, override it in tests.

## `lru_cache` on the settings factory

Constructing a `Settings` instance reads environment variables and validates them — cheap, but not free. Cache the singleton with `functools.lru_cache` so it runs once per process instead of once per request.

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`lru_cache` with no arguments memoizes a parameterless function indefinitely — the result is computed on first call and returned for every subsequent call. Tests that want fresh settings can call `get_settings.cache_clear()` between cases.

## Never hardcode secrets

Database URLs, API keys, JWT signing secrets, OAuth client secrets, third-party tokens — they all come from environment variables (or a secret manager), never from source code or committed files.

```python
# WRONG — secret committed to source
JWT_SECRET = "super-secret-do-not-share"

# Right — sourced from env at startup
class Settings(BaseSettings):
    jwt_secret: str    # no default = required → app refuses to start without it

settings = Settings()
JWT_SECRET = settings.jwt_secret
```

Make secrets required (no default value) so the app fails fast at startup if they're missing — a missing JWT secret should crash the process, not silently sign tokens with `""`. In production, get secrets from the platform's secret store (AWS Secrets Manager, GCP Secret Manager, Render env, Fly secrets); committed `.env` files are for local dev only and should be in `.gitignore`.
