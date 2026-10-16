# Module Template — complete worked example

A full feature module (`app/widgets/`), file by file. Copy the shapes, not
the widget domain. Every new module follows this anatomy; delete what a
tiny module doesn't need, but keep the layering and the import direction.

## `models.py` — domain entities

Plain dataclasses. No Pydantic, no DB types, no FastAPI imports — this
file must stay importable in a world where the HTTP framework and the
database both changed.

Note a deliberate difference from many FastAPI codebases, where
`models.py` means ORM models: here it holds domain entities, because the
DB is undecided. When the DB lands, SQLModel table classes or ODM
document mappings live beside the adapter in `repository*.py` — they are
persistence detail, and this file stays as it is.

```python
from dataclasses import dataclass


@dataclass
class Widget:
    id: str
    name: str
    type: str
```

## `repository.py` — the persistence seam

A `Protocol` the service depends on, plus today's in-memory
implementation. When the DB decision lands (MariaDB → SQLModel adapter,
MongoDB → motor adapter), the adapter implements this same protocol in
this same file (or `repository_mariadb.py` beside it) and gets swapped at
the composition root. Nothing else changes.

```python
from typing import Protocol

from app.widgets.models import Widget


class WidgetRepository(Protocol):
    async def add(self, widget: Widget) -> Widget: ...
    async def get(self, widget_id: str) -> Widget | None: ...
    async def list(self) -> list[Widget]: ...


class InMemoryWidgetRepository:
    def __init__(self) -> None:
        self._items: dict[str, Widget] = {}

    async def add(self, widget: Widget) -> Widget:
        self._items[widget.id] = widget
        return widget

    async def get(self, widget_id: str) -> Widget | None:
        return self._items.get(widget_id)

    async def list(self) -> list[Widget]:
        return list(self._items.values())
```

Implement the complete protocol — every method, real return shapes. A
partial fake hides structural assumptions and fails silently later.

## `exceptions.py` — domain errors

Services raise these; they know nothing about HTTP. The router (or a
global handler in `core/`) maps them to status codes.

```python
from app.core.exceptions import DomainError


class WidgetNotFound(DomainError):
    def __init__(self, widget_id: str) -> None:
        super().__init__(f"widget {widget_id!r} not found")
        self.widget_id = widget_id
```

## `service.py` — business logic

Depends only on the protocol and domain types. No `fastapi` import, no
Pydantic, no `HTTPException`. This is the domain seam the `tdd` skill
tests first.

```python
from uuid import uuid4

from app.widgets.exceptions import WidgetNotFound
from app.widgets.models import Widget
from app.widgets.repository import WidgetRepository


class WidgetService:
    def __init__(self, repository: WidgetRepository) -> None:
        self._repository = repository

    async def create(self, name: str, type: str) -> Widget:
        widget = Widget(id=str(uuid4()), name=name, type=type)
        return await self._repository.add(widget)

    async def get(self, widget_id: str) -> Widget:
        widget = await self._repository.get(widget_id)
        if widget is None:
            raise WidgetNotFound(widget_id)
        return widget
```

## `schemas.py` — Pydantic at the edge only

Request/response models. Validation that can be declared here (lengths,
enums via `Literal`, formats) belongs here, not in the service.

```python
from typing import Literal

from pydantic import BaseModel, Field

WidgetType = Literal["kpi", "chart", "table"]


class WidgetCreate(BaseModel):
    model_config = {"str_strip_whitespace": True}

    name: str = Field(min_length=1)
    type: WidgetType


class WidgetOut(BaseModel):
    id: str
    name: str
    type: WidgetType
```

## `dependencies.py` — providers and aliases

One provider per injectable, exported as an `Annotated` alias so routers
stay clean and tests override a single well-known symbol.

```python
from typing import Annotated

from fastapi import Depends

from app.widgets.repository import InMemoryWidgetRepository, WidgetRepository
from app.widgets.service import WidgetService

_repository = InMemoryWidgetRepository()  # composition-root default; DB adapter replaces this


def get_widget_repository() -> WidgetRepository:
    return _repository


def get_widget_service(
    repository: Annotated[WidgetRepository, Depends(get_widget_repository)],
) -> WidgetService:
    return WidgetService(repository)


WidgetServiceDep = Annotated[WidgetService, Depends(get_widget_service)]
```

## `router.py` — HTTP translation only

Router-level `prefix`/`tags`; return types on every endpoint; domain
exceptions mapped to `HTTPException` here (or globally, see
conventions.md). If a router function grows past ~15 lines it is doing
service work — move it. Note the collection route is `""`, not `"/"` —
with `prefix="/widgets"`, `"/"` would register `/widgets/` (trailing
slash) while the convention and every client/test call is `/widgets`.

```python
from fastapi import APIRouter, HTTPException, status

from app.widgets.dependencies import WidgetServiceDep
from app.widgets.exceptions import WidgetNotFound
from app.widgets.schemas import WidgetCreate, WidgetOut

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_widget(payload: WidgetCreate, service: WidgetServiceDep) -> WidgetOut:
    widget = await service.create(name=payload.name, type=payload.type)
    return WidgetOut(id=widget.id, name=widget.name, type=widget.type)


@router.get("/{widget_id}")
async def get_widget(widget_id: str, service: WidgetServiceDep) -> WidgetOut:
    try:
        widget = await service.get(widget_id)
    except WidgetNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="widget not found")
    return WidgetOut(id=widget.id, name=widget.name, type=widget.type)
```

## Wiring in `main.py` — the composition root

```python
from fastapi import FastAPI

from app.dashboards.router import router as dashboards_router
from app.widgets.router import router as widgets_router

app = FastAPI(title="r-dashboard API")

api_prefix = "/api/v1"
app.include_router(widgets_router, prefix=api_prefix)
app.include_router(dashboards_router, prefix=api_prefix)
```

`main.py` is the only place that knows which concrete implementations are
in play. It stays boring on purpose.

## Tests mirror the module

```
tests/
  conftest.py             # shared anyio backend config
  widgets/
    conftest.py           # client fixture: ASGITransport + dependency_overrides
    test_service.py       # domain seam: service + in-memory repo, no HTTP
    test_router.py        # API seam: through the ASGI app
```

The client fixture overrides `get_widget_repository` with one in-memory
instance per test (capture the instance in a closure — a `lambda:
InMemoryWidgetRepository()` builds a new empty store per request and
breaks POST-then-GET tests). Process and discipline: see the `tdd` skill.
