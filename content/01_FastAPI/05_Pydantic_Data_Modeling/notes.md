# Pydantic Data Modeling

Pydantic is FastAPI's data contract. Every request body, every response, every validation error, and most of the auto-generated OpenAPI schema flows through Pydantic models — so they aren't optional infrastructure to understand.

## Key Points

- **`BaseModel`** — subclass it, declare typed fields, get parsing, validation, and serialization for free.
- **`Field()`** — attach `min_length`, `max_length`, `gt`/`ge`/`lt`/`le`, `pattern`, defaults, descriptions, and examples to a field; they flow into the OpenAPI schema.
- **Type coercion** — Pydantic v2 default (lax mode) converts compatible inputs; use `strict=True` to refuse coercion.
- **Optional and default values** — no default = required; `T | None = None` for nullable optional; `Field(default_factory=...)` for mutable defaults.
- **Nested models** — models can contain other models, validated and serialized recursively.
- **v1 vs v2** — `model_dump()` (was `dict`), `model_validate()` (was `parse_obj`), `@field_validator` (was `@validator`), `model_config = ConfigDict(...)` (was `class Config`). Pin your major version.
- **Separate request and response models** — input accepts user-settable fields; output controls what leaves the API and hides internals.
- **`model_config`** — per-model options including `from_attributes=True` (formerly `orm_mode`) to validate from arbitrary objects (e.g. SQLAlchemy rows).
- **Custom validators** — `@field_validator` for single fields; `@model_validator(mode="after")` for cross-field rules. Raise `ValueError`, not `HTTPException`.
- **Automatic 422** — FastAPI returns a structured validation error response on failure without any custom code.
- **Pydantic Settings** — same modeling power, sourced from environment variables instead of a request body.

## Example

A `users` endpoint pair showing separate input and output models, `Field()` validation, a custom cross-field validator, and `from_attributes` for ORM integration:

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator

app = FastAPI()


class UserIn(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "UserIn":
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    # password never appears in output


class UserRow:
    """Simulated ORM row."""
    def __init__(self, id: int, email: str, password_hash: str):
        self.id = id
        self.email = email
        self.password_hash = password_hash


@app.post("/users", response_model=UserOut)
async def create_user(payload: UserIn) -> UserRow:
    row = UserRow(id=1, email=payload.email, password_hash="hashed")
    # Return the ORM-like object directly; from_attributes=True lets
    # UserOut read the fields it needs and drop password_hash.
    return row
```

- Bad email: returns `422` with `loc: ["body", "email"]`.
- Mismatched passwords: returns `422` with the validator's `"passwords do not match"` message.
- Success: returns `{"id": 1, "email": "..."}` — no password fields leak out.
