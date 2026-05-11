# Content Authoring

How study content is structured, formatted, and rendered by the study site. Read this before adding a new topic or editing an existing `concepts.md` file.

## Directory layout

Study content lives under `content/`:

```
content/
└── <NN>_<Technology>/                # e.g. 01_FastAPI, 02_Java
    ├── technology_concepts.md         # optional: overview at the tech level
    ├── research/                      # optional: course outlines, distilled concepts
    │   ├── course_outlines.md
    │   └── concepts.md
    └── <NN>_<Topic_Name>/             # e.g. 03_Framework_Foundations
        ├── concepts.md                # required for the Concepts tab
        └── notes.md                   # required for the Notes tab
```

Rules:

- Both technology and topic directories are prefixed with a zero-padded integer (`01_`, `02_`, …) which controls sort order in the sidebar.
- The directory name after the prefix becomes the rendered title (underscores → spaces).
- `concepts.md` is the per-topic source of truth for the Concepts tab; `notes.md` is the source for the Notes tab.
- Files under `research/` are author scratch space and not rendered by the topic UI.

## `concepts.md` format

The site supports two formats. Use the **structured format** for new content.

### Structured format (recommended)

Each concept is an `## H2` heading followed by 1–2 paragraphs of body, optionally with code blocks:

```markdown
## ASGI vs WSGI

WSGI is the synchronous Python web standard used by Flask and classic
Django. ASGI extends WSGI to support `async`/`await`, WebSockets, and
long-lived connections.

FastAPI is built on ASGI, which is why `async def` path operations can
cooperatively handle many concurrent requests on a single worker.

## The `FastAPI` application instance

The root object you instantiate once at the top of your app.

```python
from fastapi import FastAPI

app = FastAPI(title="Books API", version="0.1.0")
```
```

The parser splits the file on `## ` lines: each heading becomes a card, the body until the next heading becomes the detail panel content (rendered as Markdown — paragraphs, code blocks, lists, links all work).

### Legacy format (still supported)

A flat list of one-line bullets, no headings:

```markdown
- Path parameters are type-validated automatically by FastAPI
- Query parameters are optional by default when given a default value
- APIRouter allows modular route grouping with shared prefix and tags
```

Legacy-format cards display the bullet text only and are not clickable (no detail panel). Use this only for unconverted topics; prefer the structured format for anything new.

## `notes.md` format

A topic's narrative notes. Convention:

```markdown
# <Topic Title>

One-paragraph intro framing the topic.

## Key Points

- **Concept A** — short explanation.
- **Concept B** — short explanation.

## Example

```python
# A small, runnable example that exercises the topic.
```

Optional trailing paragraph tying the example back to the concepts.
```

`notes.md` is rendered as a single Markdown document on the Notes tab — no special parser. Keep examples small and concrete.

## How the site renders concepts

The frontend at `site/app.js` calls `parseConcepts()` on the `concepts.md` text:

1. If any `## ` heading is present, parse the structured format into `[{title, body}]` records and render each as a clickable card.
2. Otherwise, parse the legacy bullet format into title-only, non-clickable cards.

Clicking a structured-format card opens a detail panel below the grid that renders the concept's body as Markdown. Only one panel is open at a time; click the active card again or the × button to close it.

## Adding a new topic

1. Choose the next available `<NN>_` prefix under the technology folder.
2. Create `content/<NN>_<Technology>/<NN>_<Topic_Name>/`.
3. Write `concepts.md` in the structured format.
4. Write `notes.md` with title, key points, and an example.
5. Reload the local site (`python serve.py`) — the topic appears automatically; there is no manifest to update.

## Quality bar for concepts

A good concept entry should satisfy these checks:

- **Title is scannable.** A reader skimming the card grid should understand what the concept is from the title alone. Use backticks for code-like names (`FastAPI()` instance, `BaseSettings`).
- **Body answers both "what" and "why."** A definition without motivation is fragile; motivation without a definition is vague.
- **Code where it grounds the concept.** A four-line example beats two more paragraphs of prose. Skip code when the concept is purely conceptual (e.g. WSGI vs ASGI).
- **Contrast where helpful.** If the concept is one option among several (Uvicorn vs Hypercorn, Pydantic v1 vs v2, ASGI vs WSGI), name the alternative briefly.
- **No course branding.** Course names, instructor names, and project names from research are scaffolding, not study content.
- **Stop when you've said enough.** A reader should finish each card in under a minute. If the body is creeping past two paragraphs plus one code block, split it into two concepts or move the rest to `notes.md`.

## Where this came from

The Framework Foundations topic ([content/01_FastAPI/03_Framework_Foundations/](../content/01_FastAPI/03_Framework_Foundations/)) is the reference implementation of this workflow. Look there for a worked example.

The structured concept format was added in the same change that introduced the expandable detail panel on the site; the legacy bullet format is preserved so unconverted topics keep rendering.

For an AI-driven version of this workflow see [ai-skills/swe-study-guide-topic-authoring/](../ai-skills/swe-study-guide-topic-authoring/).
