## Password hashing with bcrypt

Never store plaintext passwords. Hash them on registration with a slow, salted, modern algorithm — bcrypt is the standard choice — and compare hashes on login.

```python
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd.hash("hunter2")            # store this in the DB
ok = pwd.verify("hunter2", hashed)       # True on match
```

bcrypt's slowness is the feature — it makes brute-force attacks expensive. The `CryptContext` lets you upgrade algorithms over time (e.g. bcrypt → argon2) without breaking existing users.

## JWT (JSON Web Tokens)

A JWT is a signed, base64url-encoded string with three parts separated by dots: `header.payload.signature`. The payload is a JSON object containing claims (`sub`, `exp`, custom data); the signature proves the token came from the server and hasn't been tampered with.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE2OTk5OTk5OTl9.<sig>
```

Decoded payload: `{"sub": "123", "exp": 1699999999}`. The server doesn't store the token — it verifies the signature on every request. That makes JWT auth **stateless**: no DB lookup needed to validate the token, which scales horizontally without session stores.

The tradeoff: you can't easily revoke a JWT mid-lifetime. Keep `exp` short and use refresh tokens for longer sessions.

## Token expiration (`exp`)

Every JWT should carry an `exp` claim with a short lifetime — typically 15–60 minutes for access tokens. A stolen access token only works until it expires, which limits the damage from a leaked token or browser exploit.

```python
from datetime import datetime, timedelta, timezone
import jwt

def make_token(user_id: str, minutes: int = 30) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
```

For long-lived sessions, pair the short access token with a longer-lived **refresh token** stored securely (HTTP-only cookie or a server-side session). When the access token expires, the client uses the refresh token to get a new one.

## OAuth2 Password Bearer flow

The simplest OAuth2 flow FastAPI supports: client posts `username` and `password` as form data, server returns an access token, client sends it as `Authorization: Bearer <token>` on subsequent requests. Standard, well-documented, and supported by FastAPI's built-in helpers.

```
POST /token
Content-Type: application/x-www-form-urlencoded

username=alice&password=hunter2

→ 200 OK
{ "access_token": "eyJ...", "token_type": "bearer" }
```

It's called "Password" because the client sees the password (unlike Authorization Code flow used for third-party login). Fine for first-party clients (your own frontend, mobile app) on HTTPS; not for federation or SSO.

## `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm`

FastAPI ships first-class helpers for the password flow:

- `OAuth2PasswordRequestForm` parses the `application/x-www-form-urlencoded` body into `.username` and `.password`.
- `OAuth2PasswordBearer(tokenUrl="...")` declares the auth scheme in OpenAPI and extracts the `Bearer` token from the `Authorization` header on protected routes.

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form.username, form.password)
    if not user:
        raise HTTPException(401, "bad credentials")
    return {"access_token": make_token(user.id), "token_type": "bearer"}

@app.get("/me")
async def me(token: str = Depends(oauth2_scheme)):
    # token already extracted from Authorization: Bearer <token>
    ...
```

Bonus: Swagger UI gets a built-in "Authorize" button that handles the login flow for testing.

## Current user dependency

The canonical pattern: a single `get_current_user` dependency that decodes the token, validates the signature and `exp`, fetches the user row, and returns it. Every protected route depends on it.

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid token")
    user = db.query(User).get(payload["sub"])
    if user is None:
        raise HTTPException(401, "user not found")
    return user
```

This is the dependency-injection win for auth: write it once, get the user object on every protected route for free, and FastAPI's per-request caching means it only runs once per request even with many sub-dependencies needing it.

## Protected routes

A route is protected by depending on the current-user (or current-admin) dependency. If the dependency raises 401, the handler never runs.

```python
@app.get("/orders")
async def list_orders(user: User = Depends(get_current_user)):
    return get_orders_for(user)

@app.delete("/users/{id}")
async def delete_user(
    id: int,
    admin: User = Depends(require_admin),
):
    ...
```

Use `dependencies=[Depends(...)]` on the decorator when you need the side effect (auth check) but the user object isn't used in the handler body.

## Authorization vs authentication

Two distinct questions that get conflated all the time:

- **Authentication** — "Who are you?" Verified by credentials → identity (user ID).
- **Authorization** — "What may you do?" Verified by checking the identity against a policy.

```python
def get_current_user(...) -> User: ...        # authentication
def require_admin(user = Depends(get_current_user)) -> User:    # authorization
    if not user.is_admin:
        raise HTTPException(403, "admin required")
    return user
```

A 401 means "I don't know who you are"; a 403 means "I know who you are, and you're not allowed." Returning the wrong one leaks information (a 403 confirms the resource exists; a 401 doesn't).

## Email confirmation tokens

For email verification (and "forgot password" flows), generate a short-lived signed token, email a link containing it, and accept the token at a confirmation endpoint. JWT works for this, but with a different signing secret and a distinct claim (`type: "email_confirm"`) so confirmation tokens can't be used as access tokens.

```python
def make_email_token(email: str, hours: int = 24) -> str:
    payload = {
        "sub": email,
        "type": "email_confirm",
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
    }
    return jwt.encode(payload, EMAIL_TOKEN_SECRET, algorithm="HS256")

@app.get("/confirm/{token}")
async def confirm(token: str, db = Depends(get_db)):
    payload = jwt.decode(token, EMAIL_TOKEN_SECRET, algorithms=["HS256"])
    if payload.get("type") != "email_confirm":
        raise HTTPException(400, "bad token")
    user = db.query(User).filter_by(email=payload["sub"]).first()
    user.email_confirmed = True
    db.commit()
```

Same shape applies to magic-link sign-in, password reset, and invitation acceptance — short-lived, scope-tagged, single-use where possible.
