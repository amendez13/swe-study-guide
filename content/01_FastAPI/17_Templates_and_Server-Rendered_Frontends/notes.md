# Templates and Server-Rendered Frontends

When FastAPI is the whole stack — not just an API behind a SPA — Jinja2 + static files + HTMX gives you most of an interactive frontend without writing JavaScript.

## Key Points

- **`Jinja2Templates`** — `templates.TemplateResponse("file.html", {"request": request, ...})`; the `request` key is required.
- **Static files** — `app.mount("/static", StaticFiles(directory="static"))` for CSS/JS/images; put a CDN in front for production.
- **Form endpoints** — receive HTML form fields with `Form(...)`; redirect with 303 after `POST` to prevent re-submit on refresh.
- **HTMX** — endpoints return HTML fragments that the client swaps into the page; FastAPI handles full pages and fragments from the same router.

## Example

A small books app with a list page, a create form, a detail page, and an HTMX-powered live search:

```python
# main.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

books: list[dict] = []


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "books": books},
    )


@app.post("/books")
async def create_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
):
    book = {"id": len(books) + 1, "title": title, "author": author}
    books.append(book)
    return RedirectResponse("/", status_code=303)


@app.get("/search")
async def search(request: Request, q: str = ""):
    results = [b for b in books if q.lower() in b["title"].lower()]
    # HTMX-aware: return a fragment if requested via HTMX, a full page otherwise
    template = "_results.html" if request.headers.get("hx-request") else "search.html"
    return templates.TemplateResponse(
        template,
        {"request": request, "results": results, "q": q},
    )
```

```html
<!-- templates/index.html -->
<!doctype html>
<html>
<head>
  <title>Library</title>
  <link rel="stylesheet" href="{{ url_for('static', path='/style.css') }}">
  <script src="https://unpkg.com/htmx.org@2.0.0"></script>
</head>
<body>
  <h1>Library</h1>

  <form method="post" action="/books">
    <input name="title" placeholder="Title" required>
    <input name="author" placeholder="Author" required>
    <button>Add</button>
  </form>

  <input name="q" placeholder="Search…"
         hx-get="/search" hx-trigger="keyup changed delay:300ms"
         hx-target="#results" hx-swap="innerHTML">
  <div id="results">
    {% for book in books %}
      <p>{{ book.title }} — {{ book.author }}</p>
    {% endfor %}
  </div>
</body>
</html>
```

```html
<!-- templates/_results.html — HTML fragment returned to HTMX -->
{% if results %}
  {% for book in results %}
    <p>{{ book.title }} — {{ book.author }}</p>
  {% endfor %}
{% else %}
  <p>No matches for "{{ q }}".</p>
{% endif %}
```

Typing in the search box fires `GET /search?q=...` debounced at 300ms; FastAPI sees the `HX-Request` header, returns `_results.html` (just the matching rows), and HTMX swaps them into `#results`. No SPA framework, no JSON API, no build step — just FastAPI and a single `<script>` tag.
