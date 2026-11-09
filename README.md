# foe

A deliberately tiny two-agent build loop: an **adversarial, creative product manager**
picks the next move, a **developer** builds it, repeat — until the PM calls it done or
the iteration budget runs out. Think `built`, minus four of the five columns.

- **Loop**: PM (decides, JSON task+spec) → Dev (writes real files into a per-project workspace) → PM sees history, decides again.
- **API**: FastAPI on **:19093** (`/api/...`), self-contained UI on `/` (no CDN dependencies — all CSS/JS inline).
- **Models**: via the litellm gate (`:4000`). Defaults: PM `qwen-flash-noemaforge`, Dev `pixelforge-qwen` — overridable per project.
- **Multi-project**: each project gets its own goal, iteration budget, workspace (`data/workspaces/<id>/`), and nudge box.
- **Publish**: human-triggered `POST /api/projects/{id}/publish` publishes the finished workspace as a public GitHub repo under `ehippy` and enables GitHub Pages. Only works when project status is `done`.
- **QA gate**: `GET /api/projects/{id}/qa` runs a lightweight check (all `.py` files compile, `index.html` structure). Results are surfaced inline in the UI via the **QA** button per project.
- **Safe serialization**: all project fields are accessed via `dict.get()` with defaults so schema drift never crashes the API.

## Quick start

```bash
pip install fastapi uvicorn pydantic
uvicorn foe.app:app --port 19093
```

Open <http://localhost:19093> — the UI is fully self-contained (inline CSS + JS, zero external requests).

## UI features

| Feature | Details |
|---------|---------|
| Create project | Name, goal, model overrides, iteration budget |
| Run / Stop | Start or halt the PM⇄Dev loop |
| Nudge box | Send a free-text note to influence the next PM decision |
| QA button | Triggers compile + HTML structure check; result shown inline |
| Publish button | Disabled until status = `done`; on success shows `repo_url` + `pages_url`; handles 409 conflict |
| Polling | Auto-refresh every 5 s |
| Mobile | Responsive layout, works on narrow screens |

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/` | Serves `static/index.html` (self-contained, no CDN) |
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create (optionally auto-start) |
| GET | `/api/projects/{id}` | Single project |
| DELETE | `/api/projects/{id}` | Remove (409 if running) |
| POST | `/api/projects/{id}/run` | Start loop |
| POST | `/api/projects/{id}/stop` | Halt loop |
| POST | `/api/projects/{id}/note` | Set nudge text |
| GET | `/api/projects/{id}/qa` | Run QA gate |
| POST | `/api/projects/{id}/publish` | Publish to GitHub + Pages (409 if not done) |
| GET | `/api/projects/{id}/iterations` | Full iteration history |

## File layout

```
foe/
├── __init__.py
├── app.py          # FastAPI app, routes, static serving
├── db.py           # SQLite persistence (stdlib only)
├── engine.py       # Supervisor: PM⇄Dev loop, threading
├── llm.py          # litellm gate client
├── publish.py      # GitHub repo + Pages publishing
└── static/
    └── index.html  # Self-contained UI (inline CSS+JS, no CDN)
data/
├── foe.db          # SQLite database
└── workspaces/     # Per-project file workspaces
```

## QA gate details

The QA endpoint checks:
1. Every `.py` file in the project workspace compiles (`py_compile` with `doraise=True`).
2. `index.html` (if present) has a valid doctype and is properly closed.

Results are stored on the project row and rendered inline in the UI.

## Publishing

- **Trigger**: `POST /api/projects/{id}/publish` (UI button, disabled until `done`).
- **Precondition**: project status must be `done` (409 otherwise).
- **Action**: `publish.py` creates a public GitHub repo under the `ehippy` org/user, pushes the workspace, and enables GitHub Pages.
- **Response**: `{"repo_url": "…", "pages_url": "…"}` — both displayed in the UI.
- **Auto-publish**: disabled by default; the `auto_publish` column exists for future use.

## Design notes

- **No external dependencies in the UI**: the HTML page is fully self-contained (inline `<style>` and `<script>`). No CDN links, no external fonts, no framework downloads. This guarantees the page renders even in air-gapped or restricted environments.
- **Thread safety**: SQLite connection uses `check_same_thread=False` + a `threading.Lock`.
- **Supervisor**: a single background thread manages all running projects; each project loop runs in its own thread.
- **Error isolation**: a project error sets `status='error'` and `error_message`; the loop stops but the project remains inspectable.
