# Responses and Error Handling

How FastAPI shapes what leaves your API — successful responses, error responses, and the headers that ride along with them.

## Key Points

- **`response_model`** declares the output schema and drops fields not in it; the canonical way to hide internal fields like password hashes.
- **`status_code` on the decorator** sets the success status for the route; prefer `status.HTTP_*` constants over bare numbers.
- **`HTTPException`** is the canonical abort mechanism; raise it with `status_code`, `detail`, and optional `headers`.
- **Custom exception handlers** registered with `@app.exception_handler(SomeError)` translate a domain exception into an HTTP response consistently across the app.
- **Response classes** beyond JSON: `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`.
- **Headers and cookies** are set via a `Response` parameter (FastAPI merges them) or by returning a `Response` subclass directly.

## Example

A users endpoint that combines `response_model` to hide a password hash, a custom exception for not-found, an explicit `201` for creation, and a `Response` parameter for setting the `Location` header:

```python
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class UserIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str


class UserNotFound(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id


@app.exception_handler(UserNotFound)
async def user_not_found_handler(request, exc: UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "user_not_found", "id": exc.user_id},
    )


users: dict[int, dict] = {}


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserIn, response: Response) -> dict:
    user_id = len(users) + 1
    users[user_id] = {
        "id": user_id,
        "email": payload.email,
        "password_hash": f"hashed:{payload.password}",  # dropped by response_model
    }
    response.headers["Location"] = f"/users/{user_id}"
    return users[user_id]


@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    if user_id not in users:
        raise UserNotFound(user_id)
    return users[user_id]


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int) -> None:
    if user_id not in users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="user not found")
    del users[user_id]
```

- Creating returns `201` with a `Location` header and `password_hash` filtered out.
- Reading a missing user goes through `UserNotFound` → custom 404 with `{"error": "user_not_found", ...}`.
- Deleting a missing user uses the built-in `HTTPException` → default 404 with `{"detail": "user not found"}`.
