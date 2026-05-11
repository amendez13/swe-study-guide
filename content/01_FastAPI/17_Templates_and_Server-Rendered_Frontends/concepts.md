## `Jinja2Templates`

FastAPI ships first-class support for Jinja2 templates via `Jinja2Templates`. Render HTML from a template, pass it the request and any context, return a `TemplateResponse`.

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "books": [{"title": "Example"}]},
    )
```

```html
{# templates/index.html #}
<!doctype html>
<title>Library</title>
<ul>
{% for book in books %}
  <li>{{ book.title }}</li>
{% endfor %}
</ul>
```

The `request` key in the context is required — Jinja2 needs it to resolve `url_for` and other request-scoped helpers. Templates are loaded lazily and cached; in dev, enable auto-reload to pick up changes.

## Static files

`StaticFiles` mounts a directory at a URL prefix and serves the contents directly — useful for CSS, JS, images, robots.txt, favicons, generated bundles. Mount it like another sub-app:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

```html
<link rel="stylesheet" href="{{ url_for('static', path='/style.css') }}">
```

For production, put static files behind a CDN or reverse proxy that can serve them more efficiently than Python — `StaticFiles` is fine for dev and small deployments.

## Form-driven endpoints

Browser HTML forms submit with `Content-Type: application/x-www-form-urlencoded` (or `multipart/form-data` for file uploads). Receive the fields as `Form(...)` parameters, render the result as another template.

```python
from fastapi import Form
from fastapi.responses import RedirectResponse

@app.post("/books")
async def create_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
):
    book = repo.create(title=title, author=author)
    return RedirectResponse(f"/books/{book.id}", status_code=303)

@app.get("/books/{id}")
async def show_book(request: Request, id: int):
    return templates.TemplateResponse(
        "book.html",
        {"request": request, "book": repo.get(id)},
    )
```

The Post/Redirect/Get pattern (status 303) is what prevents accidental re-submits when the user refreshes after submitting a form.

## HTMX and hypermedia patterns

HTMX is a small JavaScript library that lets HTML elements trigger HTTP requests and swap the response in place. The server returns **HTML fragments**, not JSON; the client mutates the page without writing JavaScript or running a SPA framework.

```html
<!-- index.html: clicking the button loads a fragment in place -->
<div id="result"></div>
<button hx-get="/search?q=fastapi" hx-target="#result" hx-swap="innerHTML">
  Search
</button>
```

```python
# Endpoint returns a fragment, not a full page
@app.get("/search")
async def search(request: Request, q: str):
    results = repo.search(q)
    return templates.TemplateResponse(
        "_results.html",     # partial template, not a full layout
        {"request": request, "results": results},
    )
```

FastAPI is well-suited to this style because the same handler can return either a full page or a fragment depending on the request — typically branching on the `HX-Request` header HTMX sets. You get most of the interactivity of a SPA with a fraction of the JavaScript.
