## `BaseModel`

`BaseModel` is the base class for Pydantic data models. Subclass it, declare typed fields, and you get parsing, validation, JSON serialization, and schema generation for free.

```python
from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    author: str
```

`Book.model_validate({"id": "1", "title": "x", "author": "y"})` returns a `Book` instance (note the string-to-int coercion); invalid input raises `ValidationError`. `book.model_dump()` returns a plain dict for JSON serialization.

## `Field()` validators

`Field()` attaches declarative constraints and metadata to a model field without writing a custom validator. The constraints flow into the OpenAPI schema, so Swagger UI shows them automatically.

```python
from pydantic import BaseModel, Field

class BookIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    rating: int = Field(..., ge=0, le=5)
    isbn: str = Field(..., pattern=r"^\d{13}$")
    description: str = Field("", description="Optional blurb")
```

Common constraints: `min_length` / `max_length` for strings and collections, `gt`/`ge`/`lt`/`le` for numbers, `pattern` for regex matching, `default`, `description`, and `examples`.

## Type coercion

Pydantic converts inputs to the declared type when the conversion is unambiguous: `"3"` becomes `3`, `"true"` becomes `True`. Incompatible inputs raise `ValidationError`.

```python
class Item(BaseModel):
    count: int

Item.model_validate({"count": "3"})    # ok → count=3
Item.model_validate({"count": "three"}) # raises ValidationError
```

In Pydantic v2 this is called **lax mode** and is the default. Strict mode (`model_validate(..., strict=True)` or per-field `Field(..., strict=True)`) refuses coercion and requires exact types — useful when you've already validated upstream and want to catch programmer errors.

## Optional and default values

A field is required if it has no default; optional if it has one. To allow `None` as a value, use `T | None` (or `Optional[T]`); to also make it optional in the input, set the default to `None`.

```python
class Book(BaseModel):
    title: str                          # required
    author: str = "Unknown"             # optional, defaults to "Unknown"
    isbn: str | None = None             # optional, nullable
    tags: list[str] = Field(default_factory=list)  # mutable default
```

Always use `default_factory` for mutable defaults — never `tags: list[str] = []`, which shares the list across instances.

## Nested models

A field's type can be another `BaseModel`. Pydantic recursively parses, validates, and serializes nested structures, and they show up correctly in the generated OpenAPI schema.

```python
class Author(BaseModel):
    name: str
    country: str

class Book(BaseModel):
    title: str
    author: Author
    co_authors: list[Author] = Field(default_factory=list)
```

Nesting is how you describe rich domain objects without flattening everything into one giant model.

## Pydantic v1 vs v2

Pydantic v2 (2023) is a Rust-backed rewrite that is significantly faster and has breaking API changes from v1. Migrating an older codebase is non-trivial.

| v1 | v2 |
|----|----|
| `model.dict()` | `model.model_dump()` |
| `Model.parse_obj(d)` | `Model.model_validate(d)` |
| `@validator("x")` | `@field_validator("x")` |
| `@root_validator` | `@model_validator(mode="before"|"after")` |
| `Config` inner class | `model_config = ConfigDict(...)` |
| `orm_mode = True` | `from_attributes=True` |

Pin your Pydantic major version explicitly and migrate deliberately when bumping.

## Separate request and response models

A common mistake is using one model for both input and output. They should usually differ: the input model accepts whatever a client may legitimately set, the output model controls what the API returns. Mixing them leaks internals (password hashes, internal IDs) and creates accidentally-required fields.

```python
class UserIn(BaseModel):
    email: str
    password: str        # required on create

class UserOut(BaseModel):
    id: int
    email: str
    # password never returned

@app.post("/users", response_model=UserOut)
async def create_user(payload: UserIn) -> UserOut:
    user = hash_and_persist(payload)
    return UserOut(id=user.id, email=user.email)
```

`response_model` enforces the output schema regardless of what your handler returns — extra fields are dropped.

## `model_config` / Config

Per-model options live in `model_config` (v2) or an inner `Config` class (v1). Common options:

```python
from pydantic import BaseModel, ConfigDict

class Book(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,    # allow Book.model_validate(orm_obj)
        populate_by_name=True,   # accept both field name and alias
        str_strip_whitespace=True,
        json_schema_extra={"examples": [{"title": "...", "author": "..."}]},
    )
    title: str
    author: str
```

`from_attributes=True` (previously `orm_mode`) is what lets you `return sqlalchemy_obj` from a route and have Pydantic read its attributes.

## Custom validators

When `Field()` constraints aren't enough, write a validator. `@field_validator` runs on a single field; `@model_validator` runs on the whole model and can express cross-field rules.

```python
from pydantic import BaseModel, field_validator, model_validator

class DateRange(BaseModel):
    start: int
    end: int

    @field_validator("end")
    @classmethod
    def end_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("end must be positive")
        return v

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end < self.start:
            raise ValueError("end must be >= start")
        return self
```

Raise `ValueError` (not `HTTPException`) — Pydantic turns it into a 422 with a structured error.

## Automatic 422 on validation failure

When Pydantic validation fails on a request, FastAPI returns `422 Unprocessable Entity` with a structured error response that names the failing field, the rule it violated, and the input that triggered the failure. You don't write any code to enable this; it's automatic.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

Clients can rely on this structure for inline form errors. To customize the shape, override the `RequestValidationError` exception handler.

## Pydantic Settings (`BaseSettings`)

The same modeling power, but configured to load values from environment variables (and optionally `.env` files) instead of from a request body. Lives in the `pydantic-settings` package since v2.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
    database_url: str
    jwt_secret: str
    debug: bool = False
```

`APP_DATABASE_URL`, `APP_JWT_SECRET`, etc. are read from the environment. See [Configuration Management](../12_Configuration_Management/) for the broader pattern.
