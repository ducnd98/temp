# Day-to-Day Conventions

Naming, errors, config, REST shape, and operational conventions for this
backend. Consult the section your task touches.

## Error handling

Three layers, one direction:

1. **Schemas** reject malformed input → automatic 422. Never re-validate
   schema-guaranteed facts downstream.
2. **Services** raise domain exceptions (`WidgetNotFound`,
   `DuplicateDashboard`) subclassing `app.core.exceptions.DomainError`.
   Services never import `fastapi` or raise `HTTPException`.
3. **Routers** (or global handlers) translate domain exceptions to HTTP.
   For exceptions used across many modules, register central global handlers
   in `core/exceptions.py` instead of try/except in every router:

```python
# app/core/exceptions.py
class DomainError(Exception): ...
class NotFoundError(DomainError): ...   # modules subclass this


# app/main.py (composition root)
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": "NOT_FOUND", "msg": sanitize_message(str(exc))})
```

Status-code mapping: 404 not found · 409 duplicate/conflict · 403
ownership/permission · 422 validation (Pydantic's job) · 400 only for
rule violations that aren't shape problems.

### Standard Error Response Schema
All error responses MUST conform to a uniform schema returning strictly two fields:
```json
{
  "error": "<MACHINE_READABLE_CODE>",
  "msg": "<Actionable English explanation of the business/data cause>"
}
```

### Information Disclosure Prevention (Zero Server Leakage)
The ENTIRE error response payload (including `msg` and any error field) must NEVER leak internal server infrastructure:
- NO server filesystem paths (`D:\...`, `C:\...`, `/var/...`, `/tmp/...`).
- NO internal networking info: IP addresses (`127.0.0.1`, `::1`), ports (`3306`, `8000`), hostnames (`localhost`).
- NO internal database names, table schemas, usernames, passwords, or secret tokens.
- NO HTTP methods or internal API routes (`POST /api/v1/...`).

`msg` focuses strictly on the user-observable data or business problem so the caller knows what to fix.

#### Few-Shot Examples (Error Response Security)

##### Example 1: Database Connection Failure
- ❌ BAD (Leaks IPs, ports, driver socket internals):
```json
{
  "detail": "Can't connect to MySQL server on '127.0.0.1:3306' (Multiple exceptions: [Errno 10061] Connect call failed ('::1', 3306))"
}
```
- ✅ GOOD (Clean, secure, actionable):
```json
{
  "error": "DATABASE_CONNECTION_ERROR",
  "msg": "Unable to connect to the database service. Please ensure the database server is running and check server environment configuration."
}
```

##### Example 2: Missing File or Manifest in Artifact
- ❌ BAD (Leaks local server directory path):
```json
{
  "error": "INVALID_MANIFEST",
  "msg": "SKILL.md not found in directory: D:\\workspace\\backend\\data\\temp\\uuid-123\\extracted"
}
```
- ✅ GOOD (Clean functional explanation, zero server paths):
```json
{
  "error": "INVALID_MANIFEST",
  "msg": "SKILL.md not found in the uploaded package."
}
```

##### Example 3: Request Validation Error
- ❌ BAD (Leaks API endpoint and unparsed framework dump):
```json
{
  "error": "VALIDATION_ERROR",
  "msg": "Failed on POST /api/v1/auth/login with detail: [{'loc': ['body', 'username'], 'msg': 'Field required'}]"
}
```
- ✅ GOOD (Specifies invalid fields without leaking routes or methods):
```json
{
  "error": "VALIDATION_ERROR",
  "msg": "Request validation failed: field 'username' (Field required); field 'password' (Field required)."
}
```

### Central Sanitizer Pattern
Global exception handlers must sanitize outgoing messages using regex filters before returning `JSONResponse`:
```python
# app/core/exceptions.py
import re

def sanitize_message(msg: str) -> str:
    """Strip server filesystem paths, hostnames, IPs, ports, and API routes."""
    if not msg:
        return ""
    # Strip Windows / Unix paths
    cleaned = re.sub(r"[a-zA-Z]:\\[^\s,;'\"\]\)]+", "", msg)
    cleaned = re.sub(r"/(?:[a-zA-Z0-9_\-.]+/)+[a-zA-Z0-9_\-.]*", "", cleaned)
    # Strip IP addresses & ports
    cleaned = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "", cleaned)
    cleaned = re.sub(r"::1|localhost:\d+|:\d{2,5}\b", "", cleaned)
    # Strip HTTP method & API route markers
    cleaned = re.sub(r"\b(?:GET|POST|PUT|DELETE|PATCH)\s+/[^\s,;'\"\]\)]*", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()
```

## Logging

- Configure once in `core/logging.py` with `logging.config.dictConfig`,
  called at startup (lifespan). Level and format come from settings:
  human-readable in dev, one-line structured (JSON) outside dev so log
  aggregators can parse it.
- Every module gets its logger the same way — nothing else:

  ```python
  import logging

  logger = logging.getLogger(__name__)
  ```

  `__name__` gives the module path (`app.widgets.service`) for free, so
  filtering by feature works without any registry. Never `print()`.
- Log **business events** at the service layer (`INFO`: created/deleted,
  `WARNING`: rule rejections worth noticing), not mechanics ("entering
  function"). HTTP access logging is uvicorn's job — don't duplicate it.
- Unhandled errors are logged exactly once, with `logger.exception(...)`
  in the global exception handlers — not at every level they bubble
  through.
- Never log secrets, tokens, or full request bodies. If a value came
  from `Settings` and looks like a credential, it doesn't go in a log
  line.

## Schemas: separate input and output models

Every resource gets distinct request and response models
(`WidgetCreate` / `WidgetOut`) even when they start out similar, because
they diverge immediately: the server generates `id`/`created_at` (output
must have them, input must not accept them), input carries validation
config that output doesn't need, and the response model doubles as the
leak filter — with a shared model, adding an internal field silently
publishes it. Kill the duplication with inheritance, not by merging the
two directions:

```python
class WidgetBase(BaseModel):
    name: str = Field(min_length=1)
    type: WidgetType

class WidgetCreate(WidgetBase):
    model_config = {"str_strip_whitespace": True}

class WidgetOut(WidgetBase):
    id: str
```

Partial update gets its own `WidgetUpdate` with all-optional fields —
don't reuse `WidgetCreate` with hacks.

## Config

- `pydantic-settings` `BaseSettings`, loaded from environment (+ `.env`
  locally). No hardcoded URLs, secrets, or flags anywhere else.
- One `Settings` in `core/config.py` for cross-cutting values (env name,
  CORS origins). A module with several settings of its own gets its own
  `config.py` — module settings stay in the module.
- Expose settings through a dependency (`SettingsDep`) so tests override
  them like everything else; a `@lru_cache` provider makes it a
  singleton.

## CORS (frontend ↔ backend)

The Next.js dev server and the API run on different origins, so the
browser blocks frontend calls until CORS is configured — this is the
first integration hurdle in this monorepo. Wire `CORSMiddleware` once in
`main.py`, origins from settings (never hardcoded). Never use `"*"` in
production regardless of `allow_credentials` — it's not just unsafe with
credentials, it means any site can call the API from a browser at all;
list the actual frontend origin(s) explicitly.

```python
# core/config.py
class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:3000"]

# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Production origins come from the environment; the dev default stays in
code.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Module packages | domain noun — plural for resource collections, singular where plural is unnatural | `widgets/`, `datasources/`, `auth/` |
| Files in a module | fixed anatomy names | `router.py`, `service.py`, ... |
| Routes | plural nouns, no verbs | `POST /widgets`, not `/createWidget` |
| Path params | `<entity>_id`, identical across endpoints | `widget_id` |
| Schemas | `<Entity><Action/Direction>` | `WidgetCreate`, `WidgetOut` |
| Domain models | bare entity | `Widget` |
| Datetime fields | `_at` suffix (UTC) | `created_at` |
| Date fields | `_date` suffix | `report_date` |
| Booleans | `is_`/`has_` prefix | `is_active` |

## REST and versioning

- All routes under `/api/v1` (applied once, in `main.py`). v2 is a new
  prefix, not edited v1 contracts.
- Nesting expresses ownership, one level max:
  `/dashboards/{dashboard_id}/widgets`. Deeper than that, flatten with
  query filters.
- List endpoints paginate from day one — retrofitting pagination is a
  breaking change. Standard shape:

```python
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
```

with `limit: Annotated[int, Query(le=100)] = 20`, `offset >= 0` as a
shared paginator dependency in `core/`.

## Background work

- `BackgroundTasks` only for sub-second, losable side effects (fire an
  event, write a log). It dies with the process and has no retry.
- Anything longer or that must not be lost → a real queue (arq / Celery
  when the need appears). Don't build this speculatively; do refuse to
  put a 30-second export inside a request handler.

## API docs exposure

`/docs` and `/openapi.json` are on in development, off (or auth-gated)
outside it — the OpenAPI schema is a map of your attack surface:

```python
app = FastAPI(
    title="r-dashboard API",
    docs_url="/docs" if settings.environment == "dev" else None,
    openapi_url="/openapi.json" if settings.environment == "dev" else None,
)
```

## When the database decision lands

These apply to the future repository adapters (and only them — nothing
outside `repository*.py` files changes):

- **MariaDB**: SQLModel; explicit constraint/index naming convention set
  on metadata from day one (auto-generated names make later migrations
  painful); Alembic migrations named descriptively
  (`2026-07-04_widget_type_idx.py`); tables lowercase_snake singular
  (`widget`, `dashboard_widget`). Complex read shapes: prefer one SQL
  query with joins/aggregations over N queries + Python stitching.
- **MongoDB**: motor (or beanie); collections lowercase_snake plural;
  the repository maps documents ↔ domain dataclasses at the boundary —
  raw dicts never cross into services.
- Yes, SQL tables are singular and Mongo collections are plural — that
  asymmetry is intentional: each follows its own community's convention,
  not a shared invented one.
- Either way: connection lifecycle in a lifespan handler + `yield`
  dependency; integration tests for adapters run against a real
  containerized DB, marked separately from the fast suite (see the `tdd`
  skill).

## Bootstrap Admin Seeding (Few-Shot)

When seeding an initial administrative user on application startup (`lifespan`):
- ❌ BAD (Spawns duplicate admins or resets passwords on restart when env changes):
```python
# Naive check by username creates redundant admins if INITIAL_ADMIN_USERNAME is renamed:
admin = await session.execute(select(User).where(User.username == settings.initial_admin_username))
if not admin.scalar_one_or_none():
    session.add(User(username=settings.initial_admin_username, ...))
```
- ✅ GOOD (Strict bootstrap invariant — seeds ONLY if 0 admins exist, never overwrites):
```python
# Strictly count existing admins across the system:
admin_count = (await session.execute(select(func.count(User.id)).where(User.is_admin.is_(True)))).scalar() or 0
if admin_count == 0:
    session.add(User(username=settings.initial_admin_username, hashed_password=get_password_hash(settings.initial_admin_password), is_admin=True))
    await session.commit()
    logger.info("No existing admin detected. Seeded initial bootstrap admin: %s", settings.initial_admin_username)
else:
    logger.debug("Admin user(s) already exist (count=%d). Skipping bootstrap seed to protect credentials.", admin_count)
```

## Hot-Reload with Data/Upload Volumes (Few-Shot)

When an application processes file uploads, temporary extractions, or local artifact storage (e.g. `/data` volume):
- ❌ BAD (Uvicorn watches entire directory and constantly reloads during file writes, killing active requests):
```bash
uvicorn app.main:app --reload
```
- ✅ GOOD (Restricts watcher strictly to application code package, ignoring file writes in data/temp volumes):
```bash
uvicorn app.main:app --reload --reload-dir app
```
