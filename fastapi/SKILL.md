---
name: fastapi
description: Architecture and coding conventions for this monorepo's FastAPI backend (modular domain packages, canonical Resource-Oriented RESTful endpoints, MariaDB persistence). Use whenever writing, building, or modifying ANY backend code - creating endpoints, REST APIs, routers, services, repositories, schemas, models, migrations, or deciding URL structure. Strictly enforces canonical REST paths (plural nouns e.g. POST /skills, PUT /skills/{id}, DELETE /skills/{id}) and forbids RPC verb paths (NO /ingest, /create, /update, /delete). Triggers on: 'endpoint', 'API', 'router', 'service', 'module', 'backend', 'FastAPI', 'tạo API', 'viết endpoint', 'thêm skill', 'CRUD', 'REST'.
---

# FastAPI Conventions

How the backend of this monorepo is structured and written. The companion
	dd skill covers the process (test-first); this skill covers where code
goes and what it looks like. Use both together for any backend work.

## Canonical Resource-Oriented RESTful API Standard

All endpoints must follow strict Resource-Oriented REST architecture (nouns, not verbs):
1. **Plural Nouns for Resource Collections**:
   - /api/v1/skills, /api/v1/categories, /api/v1/tags.
2. **Zero RPC Action Verbs in Paths (Strict Prohibition)**:
   - NEVER use verbs in endpoints: NO /ingest, /create, /update, /delete, /add, /sync.
   - The HTTP method communicates the action, the URL communicates the resource:
     - POST /api/v1/skills: Add / Create a new skill (was /skills/ingest).
     - PUT /api/v1/skills/{id}: Replace / Update full skill artifact (was /skills/{id}/ingest).
     - PATCH /api/v1/skills/{id}: Partial metadata update (title, description, tags, category).
     - DELETE /api/v1/skills/{id}: Delete skill.
     - GET /api/v1/skills: Catalog list with pagination, search, category, and tag filters.
     - GET /api/v1/skills/{id}: Retrieve single skill detail.
3. **Backward-Compatibility Aliases**:
   - If legacy callers use old RPC routes, provide an alias with include_in_schema=False, but the canonical endpoint is always the primary route.

## Architecture: modular (package-per-feature)

Each feature is a self-contained package, layered *inside*. There are no
app-wide 
outers/, services/, models/ folders — a feature's code
lives in one place, so adding, changing, or deleting a feature touches one
directory.

`
backend/
  app/
    core/                 # shared kernel: config, errors, security
      config.py           #   pydantic-settings Settings
      exceptions.py       #   base error types + global handlers
    widgets/              # one feature = one package
      router.py           #   HTTP layer: endpoints, status codes, HTTPException
      schemas.py          #   Pydantic request/response models (edge only)
      service.py          #   business logic, plain Python
      repository.py       #   Protocol + InMemory impl (DB adapter later)
      models.py           #   domain entities (dataclasses, no Pydantic/DB types)
      exceptions.py       #   domain-specific error types
      dependencies.py     #   Annotated aliases for injectables
`

Features do not reach into another feature's internals:

- Inward dependencies only: service.py never imports 
outer.py or
  schemas.py.
- Cross-feature calls go through the other feature's public surface
  (service.py function or dependencies.py alias), never its repository
  or private helpers.
- Database independence: models.py has no SQLAlchemy/Beanie/ODM types;
  
epository.py defines a typing Protocol that the in-memory or
  database-backed adapter implements.

## Database decisions: deferred

The team has not chosen between MariaDB (SQLAlchemy async) and MongoDB
(Motor/Beanie). To keep this decision reversible without rewriting business
logic:

1. **Entities are pure Python**: models.py uses @dataclass or plain
   classes, not ORM bases.
2. **Repositories are protocols**: 
epository.py defines class
   WidgetRepository(Protocol): ... and provides InMemoryWidgetRepository
   for tests and current runtime.
3. **Services take repositories via dependency injection**:
   WidgetService(repo: WidgetRepository).
4. When the DB is chosen, we implement SqlAlchemyWidgetRepository or
   MongoWidgetRepository and swap the binding in dependencies.py.
   Zero service code changes.

## Coding rules

- **Annotated everywhere**: Annotated[WidgetService, Depends(...)],
  never bare Depends(...) in parameter defaults.
- **Explicit return types on every function**, including routers and
  fixtures.
- **Pydantic v2 only**: rom pydantic import BaseModel, Field, ConfigDict.
  Use model_config = ConfigDict(...), not inner class Config.
- **Domain errors, not HTTP errors in services**: service raises
  WidgetNotFoundError; router catches it and raises
  HTTPException(status_code=404, detail=...). Services never import
  astapi.HTTPException.
- **Async by default**: all router endpoints and service methods are sync
  def, even if currently wrapping synchronous operations.

## Feature workflow: adding a new endpoint/feature

1. Read 
eferences/feature-anatomy.md for the exact file checklist.
2. Define domain entities in models.py first.
3. Define the repository protocol and in-memory implementation in
   
epository.py.
4. Write the service test first (	ests/test_<feature>_service.py) via the
   	dd skill.
5. Implement service.py.
6. Write the router test (	ests/test_<feature>_router.py) with TestClient
   or httpx AsyncClient.
7. Implement schemas.py and 
outer.py.
8. Register the router in pp/main.py.

## References

Consult these for specific patterns (do not memorize, read on demand):

- 
eferences/feature-anatomy.md: exact file layout, naming, export rules
- 
eferences/error-handling.md: domain errors -> HTTP mapping, error schema
- 
eferences/naming-cheatsheet.md: consistent names across layers
- 
eferences/safe-zip-artifact-inspection.md: in-memory zip handling and pruning
