# Performance

Distilled from Vercel Engineering's 70-rule React/Next.js guidelines,
narrowed to what actually matters for a data-heavy dashboard of this
size. Waterfalls and Suspense streaming (the two highest-impact items)
are covered in [data-fetching.md](data-fetching.md) since they're really
data-fetching decisions; this file covers bundle size, rendering, and
the rerender mistakes worth knowing by name.

## Bundle size

**`optimizePackageImports` for icon/utility libraries.** shadcn/ui pulls
in `lucide-react`, and libraries like it ship an entry file with
thousands of re-exports — importing even a few icons from the barrel can
cost 200–800ms per cold start and multiple seconds of extra dev-server
time. Configure this from the first `shadcn add`:

```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
};
```

Import icons normally (`import { Check } from "lucide-react"`) — Next.js
transforms them to direct imports at build time, so you keep full
TypeScript support without hand-managing deep import paths.

**Dynamic imports for heavy, non-critical components.** A chart library,
a rich text editor, anything not needed for first paint:

```tsx
import dynamic from "next/dynamic";

const ChartRenderer = dynamic(() => import("./chart-renderer"), { ssr: false });
```

This is exactly the shape of a **widget-type registry** — a dashboard
inevitably needs to render a component based on a `widget.type` string
(`"kpi" | "chart" | "table"`). Use an explicit map of import thunks, not
a dynamically-composed import path — the bundler needs to see every
possible module statically to trace/split correctly:

```typescript
// Wrong — bundler can't tell what might be imported, breaks tracing/splitting
const Widget = await import(`./widgets/${widget.type}`);

// Right — explicit map keeps every reachable module visible to the bundler
const WIDGET_COMPONENTS = {
  kpi: dynamic(() => import("./widgets/kpi-widget")),
  chart: dynamic(() => import("./widgets/chart-widget")),
  table: dynamic(() => import("./widgets/table-widget")),
} as const;

const Widget = WIDGET_COMPONENTS[widget.type];
```

## Rendering

**Explicit conditional rendering.** `count && <Badge>{count}</Badge>`
renders the literal `0` when `count` is `0` (React renders falsy numbers,
just not `false`/`null`/`undefined`). Use a ternary when the condition
can be a number:

```tsx
{count > 0 ? <Badge>{count}</Badge> : null}
```

**`content-visibility: auto` for long lists.** A dashboard's data tables
and log/event lists can run into hundreds of off-screen rows; skipping
their layout/paint work until they scroll into view is a 10x initial
render improvement at effectively zero code cost:

```css
.table-row { content-visibility: auto; contain-intrinsic-size: 0 40px; }
```

## Re-renders — the two mistakes worth knowing by name

**Never define a component inside another component.** It creates a new
component *type* every render, so React remounts it from scratch —
losing state, re-running effects, resetting scroll and focus. The usual
motive is "I need a parent variable without prop-drilling it" — pass the
prop instead.

```tsx
// Wrong — WidgetHeader is redefined (and remounted) every render
function WidgetCard({ widget, theme }) {
  function WidgetHeader() { return <h3 className={theme}>{widget.name}</h3>; }
  return <WidgetHeader />;
}

// Right — defined once, receives what it needs as props
function WidgetHeader({ name, theme }: { name: string; theme: string }) {
  return <h3 className={theme}>{name}</h3>;
}
```

**Functional `setState` when the update depends on the previous value.**
Avoids stale closures and lets the callback skip the state dependency
entirely:

```tsx
// Wrong — recreated every time items changes, and easy to forget the dependency
const addItems = useCallback((next) => setItems([...items, ...next]), [items]);

// Right — stable reference, always operates on the latest value
const addItems = useCallback((next) => setItems((curr) => [...curr, ...next]), []);
```

## Client-side storage

Dashboard UI preferences (collapsed sidebar, saved table column widths,
per-widget display density) are exactly the kind of thing that ends up in
`localStorage`. Version the key and store only what the UI needs — not a
whole cached API response:

```typescript
const PREFS_KEY = "dashboard-prefs:v1";

function savePrefs(prefs: { sidebarCollapsed: boolean }) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  } catch {
    // Throws in private browsing / quota exceeded — safe to ignore
  }
}
```

Always wrap `localStorage` access in `try`/`catch` — it throws in private
browsing in some browsers, and versioning the key lets you change the
shape later without a crash for users with the old shape cached.

## What's deliberately not in this file

The remaining ~55 rules in the Vercel source set (micro-optimizations
like RegExp hoisting, `Map`-based lookups, SVG precision, resource hints,
`useDeferredValue`) are real but low-impact at this project's current
size — reach for them if profiling actually points at one, not
preemptively. Don't let this list turn into speculative optimization.
