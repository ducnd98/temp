---
name: nextjs
description: Architecture and coding conventions for this monorepo's Next.js frontend (App Router, TypeScript, shadcn/ui, Marketplace & Catalog architecture, Zero-CLS filtering, Canvas-Integrated sidebars, Compound Card event bubbling isolation, Top-Horizon grid alignment). Use whenever writing, designing, building, or modifying ANY frontend code, pages, catalog, marketplace, home, layout, sidebar, filters, tags, categories, search, cards, pagination, components, or hooks - even if the user never mentions architecture. Triggers on: 'page', 'component', 'route', 'form', 'dashboard', 'widget', 'Next.js', 'làm trang', 'build web', 'marketplace', 'catalog', 'danh mục', 'trang chủ', 'giao diện', 'filter', 'tags', 'card', 'sidebar', 'layout', 'UI'.
---

# Next.js Conventions

How the frontend of this monorepo is structured and written. Companion
skills: `fastapi` covers the backend this frontend talks to (same feature
names — `widgets`, `dashboards`, `datasources` — on both sides), `tdd`
covers process (test-first) and frontend test seams (Vitest + Testing
Library + MSW), and `dataviz` covers chart/KPI visual design — this skill
does not repeat any of their content, only points to it.

## Marketplace & Catalog Layout Architecture Standards

When building catalogs, registries, or marketplace listings, adhere to these 6 non-negotiable UX/UI rules:

### 1. Canvas-Integrated Sidebar (Role Differentiation)
- **Sidebar is a navigation controller, NOT a content card**:
  - Never enclose the desktop filter sidebar inside a heavy card container (`bg-card border shadow-xs`).
  - The sidebar must sit directly and naturally on the page canvas.
  - Only the **content items in the grid** are elevated as cards (`bg-card border border-border shadow-xs`).
  - Enclose each Category item as an interactive button with a subtle border framing both the label and the skill count badge.

### 2. Top-Horizon Grid Alignment
- The top edge of the Left Sidebar and the top edge of the first row of Skill Cards in the Grid must start at the exact same Y baseline.
- Controls like "Sort by" must sit above the 2-column layout in a compact control bar, not pushed inside the right column where it misaligns the grid below the sidebar.

### 3. Compound Card Event Isolation (No Full-Card Links)
- NEVER wrap the entire Card in `<Link>`.
- Title and description link to the detail page.
- Tag pills (`#tag-name`) and Category badges MUST be independent interactive buttons with `e.stopPropagation()` that filter the current catalog view (`onTagClick`, `onCategoryClick`), NEVER navigating away to the detail page.
- Quick action buttons (e.g. Download) are independent interactive controls.

### 4. Zero-CLS Filter Placement (No Injected Top Banners)
- NEVER inject active filter cards or "Reset all" banners at the top of the sidebar. When users click a filter, an injected top banner causes jarring Cumulative Layout Shift (CLS), displacing the items under their cursor.
- Place the minimalist "Clear all" button with an `✕` icon at the **bottom of the sidebar** with a subtle `border-t` divider.
- When filters are active, Category and Tag items must simply stay highlighted (sáng chọn) without moving around.

### 5. Facet Search & Pinned Active Selection (Top-10 Pareto)
- User-generated tags can proliferate to hundreds of items. Never list them all blindly.
- Include an inline real-time search input (`Search tags...`) with proper icon padding (`pl-8`).
- Display Top 10 tags by popularity (most skills count `skill_count`) by default.
- Always PIN selected tags so they stay visible and highlighted at all times, even if outside the top 10 or after search is cleared.

### 6. Slim Utility Footer Proportion
- A single-line copyright footer must be a quiet, slim grounding bar (`py-4`, `mt-12 sm:mt-16`), never a bulky 80-100px block.

## Architecture: feature folders under App Router routing

Next.js reserves `app/` for routing, so the modular-monolith principle
from the `fastapi` skill (one feature = one place) lands as: **routes
stay thin, feature logic lives in `features/`**.

```
frontend/
  src/
    app/                       # routing only
      (dashboard)/
        widgets/page.tsx       # imports from features/widgets, composes Suspense
        dashboards/[id]/page.tsx
      layout.tsx
    features/                  # one feature = one folder (mirrors backend modules)
      widgets/
        components/            # feature-local components (widget card, widget form)
        queries.ts             # TanStack Query query/mutation hooks
        types.ts               # feature-local domain types
        index.ts               # public surface (what app/ can import)
    components/
      ui/                      # shadcn primitives (Button, Dialog, Card)
    lib/
      api/                     # typed OpenAPI client + error types
      query-client.ts          # QueryClient singleton + default options
      utils.ts                 # cn() and friends
    hooks/                     # cross-feature hooks only
```

Features do not reach into another feature's internals:

- `features/dashboards/` imports from `features/widgets/index.ts`, never
  from `features/widgets/components/private-thing.tsx`.
- `app/` imports page-level components from `features/<name>/`, wraps them
  in Suspense boundaries, and passes route params in. It has no business
  logic, no data fetching, and no state.

## Server Components vs Client Components

Default to Server Components. Add `"use client"` only when a component:

- Uses React hooks (`useState`, `useEffect`, `useQuery`).
- Attaches browser event listeners (`onClick`, `onChange`).
- Uses browser APIs (`localStorage`, `window`).

Keep Client Component boundaries as small as possible — push them down the
tree to the interactive leaf (the button that opens a dialog, the form
input), leaving layouts, page shells, and static content as Server
Components.

## Consuming the FastAPI backend

Do not write raw `fetch` calls. Use the typed client:

1. The client is generated from the backend's OpenAPI schema into
   `src/lib/api/`.
2. Wrap client calls in TanStack Query hooks in `features/<name>/queries.ts`.
3. Client Components consume those hooks.
4. Server Components can call the client directly (no Query hooks needed).

## Cross-Boundary Guidelines (Visual, Authentication, Markdown)

### Layout Shift Prevention on Dynamic Text Containers
Any container whose text content changes dynamically (e.g. rotating phrases, typing animations) **MUST have a fixed height** in CSS (e.g. `h-[3.25rem] sm:h-[4rem]`). This prevents the layout below it from shifting vertically (CLS = 0) as phrases of different lengths swap in.

### Gradient Text Padding for Descenders
When applying `bg-clip-text text-transparent` with a gradient, always add bottom padding (`pb-2` or `pb-3`) to the element. Without this padding, letter descenders (`g, y, p, j, q`) get clipped by the CSS background boundary.

### Context-Aware Login Redirection
- When a user clicks **Login** from any public page (`/`, `/skills/[id]`), the Navbar must preserve that origin via `?redirect=...`.
- After successful authentication, the user MUST be redirected back to the page they came from (or `/`). Never force-redirect users to `/admin` unless they deliberately navigated to `/admin`.
- Non-admin users attempting to access `/admin` must receive a `404 Not Found` response to hide the admin attack surface.

### Markdown Parsing & Display Standards
- Frontmatter stripping: SKILL.md frontmatter (delimited by `---`) must be parsed and presented in a dedicated Metadata card, never rendered as raw YAML inside the Markdown body.
- Table normalization: Un-padded GitHub Markdown tables must be normalized before rendering so standard table parsers handle them reliably.
- Monospace styling: Code blocks and inline code must use dedicated monospace fonts (`JetBrains Mono`, `Fira Code`) with `font-weight: 400`, never fake backticks.

## References

- `references/feature-anatomy.md`: directory layout, exports, and naming
- `references/data-fetching.md`: TanStack Query setup, cache keys, mutations
- `references/testing-seams.md`: where to test (MSW handlers, render seams)
- `references/tree-view-and-dual-tabs.md`: dual-tab layout and Unix tree explorer
