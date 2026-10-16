# Framework Rules — FastAPI usage conventions

Distilled from the official FastAPI skill and community best practices.
Read before writing endpoint, dependency, or schema code.

## Annotated everywhere

All parameter and dependency declarations use `Annotated`. It keeps
signatures honest for other callers, and dependency aliases become
reusable, overridable symbols.

```python
from typing import Annotated

from fastapi import Depends, Path, Query


@router.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(max_length=50)] = None,
): ...


# dependencies: alias once, reuse everywhere
WidgetServiceDep = Annotated[WidgetService, Depends(get_widget_service)]
```

Never use `...` (Ellipsis) as a default for required params or fields —
required is the default. Never use `RootModel`; annotate directly:

```python
@router.post("/items/")
async def create_items(items: Annotated[list[int], Field(min_length=1), Body()]): ...
```

## async def vs def — the event-loop rule

- `async def` only when everything awaited inside is genuinely
  non-blocking (async DB driver, httpx.AsyncClient, asyncio primitives).
- Blocking work (sync SDK, CPU-heavy code, `time.sleep`) in an
  `async def` freezes the event loop for every request in the process —
  the single most damaging FastAPI mistake.
- Plain `def` endpoints/dependencies run in a threadpool: safe default
  for blocking libraries. In doubt, use `def`.
- Mixing both: wrap blocking calls with `run_in_threadpool` (or Asyncer's
  `asyncify`) inside async code.
- CPU-bound jobs don't belong in request handlers at all — threadpools
  don't help past the GIL; use a worker (see conventions.md, background
  tasks).

Repository protocols in this project are async-first (the eventual
MariaDB/MongoDB drivers — asyncmy/SQLModel-async or motor — are async);
in-memory implementations are trivially async.

## Return types on every endpoint

Declare the return type; FastAPI/Pydantic use it to validate, filter
(no accidental leaking of internal fields), document, and serialize fast
(Rust-side). Use `response_model=` only when the returned object differs
from the public schema. Don't reach for `ORJSONResponse`/`UJSONResponse`
(deprecated) — the return type already gives fast serialization.

## Dependencies

Use a dependency when logic needs request data, external resources,
sharing across endpoints, or cleanup. Patterns:

- **Cleanup** — `yield` dependencies; exit code runs after the response
  by default:

  ```python
  def get_db():
      db = DBSession()
      try:
          yield db
      finally:
          db.close()
  ```

- **Prefer function dependencies returning instances** over class
  dependencies (`Depends()` on a class couples the signature to the
  constructor).
- **Chain them**: a `get_current_user` feeds a `get_current_admin`;
  validate-existence dependencies (fetch-or-404) are shared by every
  endpoint with the same path param. Keep path-param names identical
  across endpoints (`widget_id` everywhere) so these compose.
- FastAPI **caches** a dependency's result within one request — shared
  sub-dependencies run once.
- Router-level shared requirements go on the router:
  `APIRouter(dependencies=[Depends(require_user)])`.

## Routers

- `prefix`, `tags`, shared `dependencies` declared on the `APIRouter`
  itself, not in `include_router()` (the app-level `/api/v1` prefix is
  the composition root's one exception).
- One HTTP operation per function — never branch on method inside one
  handler.
- Status codes explicit where they aren't 200: `status_code=201` on
  create, `204` on delete.

## Pydantic

- Let Pydantic do all the validation it can declare: `Field` constraints,
  `Literal` enums, `EmailStr`, `str_strip_whitespace`. The service should
  never re-check what the schema already guarantees.
- If the project needs global serialization behavior (e.g., consistent
  datetime formatting), define one custom base model in `core/` and
  inherit — don't repeat `model_config` per schema.

## Streaming and SSE (when needed)

Server-Sent Events: `response_class=EventSourceResponse` and `yield`
`ServerSentEvent` items (from `fastapi.sse`). Byte/JSON-lines streaming:
`StreamingResponse`. Details in the official FastAPI docs — don't
hand-roll SSE framing.

## Tooling

- **uv** for dependency and environment management (`uv add fastapi`,
  `uv run pytest`); dependencies live in `pyproject.toml`, not
  requirements.txt.
- **Commit `uv.lock`.** It's what makes a build reproducible — a floating
  version can resolve differently between your machine, CI, and
  production, and behave differently once it does. `uv add` updates the
  lockfile automatically; don't hand-edit version pins in
  `pyproject.toml` without re-running `uv lock`.
- **Ruff** for linting AND formatting (replaces black/isort/flake8).
- **httpx** for outbound HTTP (never requests) — and it's already the
  test client.
- Run dev server with `fastapi dev`, production with `fastapi run`;
  entrypoint declared in `pyproject.toml` (`[tool.fastapi]
  entrypoint = "app.main:app"`).
- When the DB lands: **SQLModel** if MariaDB, **motor** (or beanie) if
  MongoDB — inside repository adapters only.
