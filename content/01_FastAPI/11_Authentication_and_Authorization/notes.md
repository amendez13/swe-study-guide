# Authentication and Authorization

How FastAPI handles "who are you?" and "what may you do?" — typically with bcrypt-hashed passwords, JWT access tokens, and the OAuth2 password bearer flow.

## Key Points

- **bcrypt for password hashing** — never plaintext; `passlib.CryptContext` lets you upgrade algorithms over time.
- **JWT** — signed `header.payload.signature` tokens; stateless verification, no DB lookup per request.
- **Short `exp`** — 15–60 min for access tokens; pair with a refresh token for long sessions.
- **OAuth2 Password Bearer** — username/password in a form, access token in the response, `Authorization: Bearer <token>` on subsequent requests.
- **FastAPI helpers** — `OAuth2PasswordRequestForm` parses the login body; `OAuth2PasswordBearer` extracts the bearer token and powers the Swagger "Authorize" button.
- **`get_current_user` dependency** — decode + validate + fetch user, once per request, reused on every protected route.
- **Protect routes** — declare `Depends(get_current_user)` (or `require_admin`); FastAPI rejects unauthenticated requests automatically.
- **Authn vs authz** — 401 = "don't know who you are"; 403 = "know who you are, not allowed".
- **Email confirmation tokens** — short-lived signed tokens with a `type` claim; same shape works for password reset and magic links.

## Example

A complete login → protected-route → admin-only flow with JWT and bcrypt:

```python
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

JWT_SECRET = "..."   # from env in real code — see Configuration Management
ALGO = "HS256"

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


# Fake user store
class User:
    def __init__(self, id: int, username: str, password_hash: str, is_admin: bool):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin


users: dict[str, User] = {
    "alice": User(1, "alice", pwd.hash("hunter2"), is_admin=True),
    "bob": User(2, "bob", pwd.hash("password"), is_admin=False),
}


def authenticate(username: str, password: str) -> User | None:
    user = users.get(username)
    if user and pwd.verify(password, user.password_hash):
        return user
    return None


def make_token(user_id: int, minutes: int = 30) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)


# --- Authentication dependency ---
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    for u in users.values():
        if u.id == int(payload["sub"]):
            return u
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")


# --- Authorization dependency ---
def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin required")
    return user


# --- Endpoints ---
@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad credentials")
    return {"access_token": make_token(user.id), "token_type": "bearer"}


@app.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: User = Depends(require_admin)):
    return {"deleted": user_id, "by": admin.username}
```

- `POST /token` with `alice/hunter2` returns a JWT.
- `GET /me` with that JWT returns alice's identity.
- `DELETE /users/2` with alice's token works (admin); with bob's token returns 403.
- Any request without `Authorization` returns 401.
