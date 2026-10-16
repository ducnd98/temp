# Project Structure

Full rationale for the folder layout, environment variables, and tooling
conventions for this frontend.

## Full tree

```
frontend/
  src/
    app/
      (dashboard)/
        layout.tsx              # shared chrome for the dashboard route group
        widgets/
          page.tsx
          loading.tsx           # Suspense fallback for this segment
          error.tsx             # error boundary for this segment
        dashboards/
          [id]/page.tsx
      layout.tsx                 # root layout: html/body, providers
      page.tsx                   # landing/home
      globals.css
    features/
      widgets/
        components/
          widget-card.tsx
        widget-list.tsx           # Server Component
        widget-form.tsx           # Client Component
        queries.ts                 # TanStack Query hooks — the feature's public surface
        types.ts                   # only types the generated schema doesn't cover
      dashboards/
      datasources/
      alerts/
    components/
      ui/                          # shadcn primitives — CLI-managed, don't hand-edit
      app-sidebar.tsx               # shared shell pieces used by 2+ features
    lib/
      api/
        client.ts
        schema.d.ts                 # generated — do not hand-edit
      query-client.ts
      utils.ts                      # cn() helper etc.
    hooks/                          # cross-feature hooks only (e.g. use-media-query)
  public/
  next.config.ts
  package.json
  tsconfig.json
```

Feature package names mirror the backend's module names one-to-one
(`widgets`, `dashboards`, `datasources`, `alerts`) — when a change spans
both halves of the monorepo, the folder you need on each side has the
same name.

## Environment variables — two base URLs, not one

The backend runs the CORS-enabled setup from the `fastapi` skill because
the browser calls it directly. That means the frontend needs **two**
values for the same backend, not one:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000   # embedded in the client bundle — browser calls this
API_URL=http://localhost:8000                # server-only — Server Components/Route Handlers call this
```

They're often the same value in local dev, but they diverge the moment
the backend runs on an internal network address the browser can't
reach (a Docker service name, an internal load balancer) while the
public one goes through a different public hostname. Anything without
the `NEXT_PUBLIC_` prefix never reaches the client bundle — that's the
whole point of keeping them separate; don't "simplify" to one variable.

## Generating the typed API client

The client is generated from the backend's OpenAPI schema, never hand-
written, so a backend contract change becomes a type error on the
frontend instead of a runtime surprise.

```bash
npm install --save-dev openapi-typescript
npm install openapi-fetch
```

```json
// package.json
{
  "scripts": {
    "gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/lib/api/schema.d.ts"
  }
}
```

The URL is deliberately hardcoded to the local dev backend: npm scripts
don't load `.env.local`, and `$VAR` doesn't expand on Windows shells —
generation always runs against your local dev server anyway.

Run `npm run gen:api` whenever the backend's routes/schemas change (with
the backend dev server running), and commit the generated `schema.d.ts`
— it's a build input, not a build artifact, so review shows up in diffs
the same way a migration file would. See
[references/data-fetching.md](data-fetching.md) for how `client.ts` uses
the generated `paths` type to build the server and browser clients.

## shadcn/ui conventions

The `shadcn` skill owns everything about the components themselves —
the CLI, composition rules (`FieldGroup`/`Field`, `Dialog`/`Sheet`
patterns, icon conventions), and theming. Read it for any task that adds,
fixes, or styles a shadcn component. This skill's concern is narrower:
*where* feature UI built from those primitives lives.

- `components/ui/` is CLI-managed — the `shadcn` skill governs what goes
  there and how.
- Compose feature UI **on top of** primitives in `features/<name>/`.
  A `WidgetCard` built from `Card`, `Badge`, `DropdownMenu` is feature
  code; the primitives themselves are not.
- The project scaffold (package versions, Tailwind v4 setup, dark mode,
  linting) is defined once in the `shadcn` skill's
  `references/template.md` — this skill doesn't duplicate it.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Feature folders | plural noun, matches backend module | `features/widgets/` |
| Route segments | matches feature name | `app/(dashboard)/widgets/` |
| Components | PascalCase | `WidgetCard`, `WidgetForm` |
| Query hooks | `use<Verb><Entity>` | `useWidgets`, `useCreateWidget` |
| Query keys | array, feature-scoped, matches hook | `["widgets"]`, `["widgets", id]` |
| Files exporting one component | kebab-case matching the component | `widget-card.tsx` |
