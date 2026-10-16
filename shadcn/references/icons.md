# Icons

This project's icon library is **`lucide-react`** — confirm with
`npx shadcn@latest info` rather than assuming, since the CLI can install
a different library depending on the preset it's invoked with.

## Icons in Button use data-icon, not a wrapper or margin

`data-icon="inline-start"` (before the label) or `"inline-end"` (after).
No sizing or margin classes on the icon itself — the component's CSS
handles sizing based on the `data-icon` attribute.

**Incorrect:**

```tsx
<Button>
  <SearchIcon className="mr-2 size-4" />
  Search
</Button>
```

**Correct:**

```tsx
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

<Button>
  Next
  <ArrowRightIcon data-icon="inline-end" />
</Button>
```

## No sizing classes on icons inside any shadcn component

Applies beyond `Button` — `DropdownMenuItem`, `Alert`, `Sidebar*`, and
others all size their icon children via CSS. Adding `size-4`/`w-4 h-4`
fights the component's own sizing rather than adjusting it.

```tsx
// Correct — no sizing class needed.
<DropdownMenuItem>
  <SettingsIcon />
  Settings
</DropdownMenuItem>
```

Exception: an icon rendered *outside* any shadcn component (e.g. bare in
a custom layout) sizes normally with Tailwind classes — this rule is
specifically about icons as children of shadcn primitives.

## Pass icons as component references, not string keys

**Incorrect:**

```tsx
const iconMap = { kpi: TrendingUpIcon, chart: BarChartIcon, table: TableIcon };

function WidgetTypeIcon({ type }: { type: string }) {
  const Icon = iconMap[type];
  return <Icon />;
}
```

**Correct:**

```tsx
import { TrendingUpIcon, BarChartIcon, TableIcon } from "lucide-react";

const WIDGET_TYPE_ICONS = {
  kpi: TrendingUpIcon,
  chart: BarChartIcon,
  table: TableIcon,
} as const;

function WidgetTypeIcon({ type }: { type: keyof typeof WIDGET_TYPE_ICONS }) {
  const Icon = WIDGET_TYPE_ICONS[type];
  return <Icon />;
}
```

This keeps the icon typed as a component (catches a typo'd key at
compile time, not at render) and keeps the import list statically
analyzable — relevant to the `nextjs` skill's bundle-size guidance on
`optimizePackageImports` for `lucide-react`.
