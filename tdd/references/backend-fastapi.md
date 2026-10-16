# Backend TDD — FastAPI + pytest

How to run the red-green-refactor loop on the backend of this monorepo.

## Layout and commands

Backend code lives in `backend/` organized as feature modules
(`app/widgets/`, `app/dashboards/` — see the `fastapi` skill
for the structure); tests in `backend/tests/` mirror the modules
(`tests/widgets/test_service.py` for the domain seam,
`tests/widgets/test_router.py` for the API seam). Run tests from
`backend/`:

```bash
uv run pytest                # full suite — run this at every VERIFY GREEN
uv run pytest tests/widgets/test_router.py -x   # one file, stop at first failure — VERIFY RED
```

(`uv run` because this project manages dependencies with uv — see the
`fastapi` skill's tooling rules; a bare `pytest` works only if the venv
happens to be activated.)

Dependencies for testing: `pytest`, `anyio` (or `pytest-asyncio`), `httpx`.

## Seam 1: domain logic — plain functions, plain pytest

Business rules live in service/use-case functions that take data in and
return data out. This is the cheapest seam — no app, no client, no I/O.
Prefer it whenever the behavior doesn't depend on HTTP semantics.

```python
# tests/pricing/test_service.py
from app.pricing.service import apply_discount

def test_discount_caps_at_50_percent():
    assert apply_discount(price=100, percent=80) == 50
```

Expected values are independent literals (`50`), never recomputed with the
same formula as the implementation — a test that mirrors the code passes
by construction and can never disagree with it.

## Seam 2: API — through the ASGI app, never route functions directly

Calling route functions directly skips validation, serialization, status
codes, and dependency injection — most of what the endpoint actually does.
Always go through the app:

```python
# tests/widgets/test_router.py
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

@pytest.mark.anyio
async def test_create_widget_returns_201_with_id(client):
    resp = await client.post("/api/v1/widgets", json={"name": "gauge"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "gauge"

@pytest.mark.anyio
async def test_create_widget_rejects_blank_name_with_422(client):
    resp = await client.post("/api/v1/widgets", json={"name": ""})
    assert resp.status_code == 422
```

Error paths (422 validation, 404 missing, 409 conflict, 401/403 auth) get
the same one-test-per-behavior discipline as happy paths — they are the
behaviors users hit most.

## The database is undecided — design for that

This project hasn't chosen between MariaDB and MongoDB. That is a reason
to keep the domain layer free of any DB driver, and TDD enforces it
naturally: put persistence behind a small repository interface, and let
services depend on the interface.

```python
# app/widgets/repository.py
from typing import Protocol
from app.widgets.models import Widget

class WidgetRepository(Protocol):
    async def add(self, widget: Widget) -> Widget: ...
    async def get(self, widget_id: str) -> Widget | None: ...
```

In tests, inject an in-memory fake through FastAPI's dependency system:

```python
# tests/fakes.py
class InMemoryWidgetRepository:
    def __init__(self):
        self._items: dict[str, Widget] = {}
    async def add(self, widget):
        self._items[widget.id] = widget
        return widget
    async def get(self, widget_id):
        return self._items.get(widget_id)

# in the client fixture — create ONE instance per test and close over it.
# `lambda: InMemoryWidgetRepository()` would build a fresh empty store on
# every request and break POST-then-GET tests (see the fastapi skill's
# module template).
repo = InMemoryWidgetRepository()
app.dependency_overrides[get_widget_repository] = lambda: repo
```

The fake implements the complete interface — every method, real return
shapes — not just the calls one test happens to make. A partial fake hides
structural assumptions and fails silently later.

When the DB is chosen, write a small integration-test layer that runs the
same repository contract against the real database (testcontainers or a
docker-compose test service), marked `@pytest.mark.integration` so the
fast suite stays fast. Domain and API tests don't change at all — that's
the payoff of the seam.

## dependency_overrides, not monkeypatching

For everything injected — auth, clock, external API clients, repositories
— override the dependency. Reserve `unittest.mock.patch` for boundaries
you don't control and can't inject.

```python
app.dependency_overrides[get_current_user] = lambda: User(id="u1", role="admin")
app.dependency_overrides[get_clock] = lambda: FixedClock("2026-01-01T00:00:00Z")
```

Patching internals couples the test to module paths and call mechanics —
it breaks on refactor even when behavior is unchanged.

## Rules of thumb

- One behavior per test; if the name needs "and", split it.
- No network, no real external services, no real DB in unit tests.
- Verify through the interface, not around it: after `POST /widgets`,
  assert `GET /widgets/{id}` returns it — don't query the storage
  behind the API's back.
- Test names state the behavior: `test_get_widget_returns_404_when_missing`,
  not `test_get_2`.
