# Routing

Placeholder notes for FastAPI routing.

## Key Points

- Routes are defined with decorators: `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`
- Path parameters use `{param}` syntax in the path string
- Query parameters are declared as function arguments without a path match
- `APIRouter` lets you group related routes and mount them with a prefix

## Example

```python
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id}
```
