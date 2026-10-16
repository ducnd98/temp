# Composition Patterns

A dashboard's widgets and forms are exactly the shape of component that
degrades into an unmaintainable pile of boolean props if built naively —
a widget can be a KPI, a chart, or a table; a form can be create, edit,
or duplicate. These patterns (from Vercel Engineering's composition
guidelines) keep that complexity from compounding.

## Avoid boolean props — use composition

Each boolean prop doubles the number of possible states a component can
be in. A `WidgetCard` with `isEditing`, `isCompact`, `showActions`,
`isDragging` has 16 possible states, most of them never intentionally
designed.

**Wrong — booleans create exponential complexity:**

```tsx
function WidgetCard({ widget, isEditing, isCompact, showActions, isDragging }: Props) {
  return (
    <Card className={isDragging ? "opacity-50" : ""}>
      {isEditing ? <WidgetEditForm widget={widget} /> : <WidgetDisplay widget={widget} compact={isCompact} />}
      {showActions && !isEditing ? <WidgetActions widget={widget} /> : null}
    </Card>
  );
}
```

**Right — explicit variants, each one self-documenting:**

```tsx
// Immediately clear what each one renders
<WidgetCard widget={w} />
<EditableWidgetCard widget={w} />
<CompactWidgetCard widget={w} />
```

Read the call site of a component and know what it does — no need to
trace every boolean combination to find out.

## Compound components for shared internal state

When a widget/card/form has several pieces that need shared state, build
it as a compound component with a context, rather than threading props
through every level or accepting a pile of `renderX` callbacks.

```tsx
const WidgetCardContext = createContext<WidgetCardContextValue | null>(null);

function WidgetCard({ widget, children }: { widget: Widget; children: ReactNode }) {
  return (
    <WidgetCardContext value={{ widget }}>
      <Card>{children}</Card>
    </WidgetCardContext>
  );
}

function WidgetCardHeader() {
  const { widget } = use(WidgetCardContext)!;
  return <CardHeader><CardTitle>{widget.name}</CardTitle></CardHeader>;
}

function WidgetCardActions() {
  const { widget } = use(WidgetCardContext)!;
  return <DropdownMenu>{/* edit, delete, duplicate */}</DropdownMenu>;
}

WidgetCard.Header = WidgetCardHeader;
WidgetCard.Actions = WidgetCardActions;
```

```tsx
// Consumers compose exactly what they need
<WidgetCard widget={w}>
  <WidgetCard.Header />
  <KpiDisplay value={w.value} />
  <WidgetCard.Actions />
</WidgetCard>
```

Prefer `children` for structural composition over `renderX` props —
render props are for when the *parent* needs to hand data back to the
child (a `renderItem` for a virtualized list); for static structure like
a card's header/body/footer, `children` reads better and composes more
naturally.

## Context as a dependency-injection interface, not a single global store

When a compound component's state might come from more than one place —
local form state for a "create" dialog, a shared/synced store for a
persisted dashboard layout — define the context as a generic interface
(`state`, `actions`, `meta`) that any provider can implement. Components
consume the interface; only the provider knows the concrete
implementation.

```typescript
interface WidgetFormState { values: WidgetFormValues; isSubmitting: boolean }
interface WidgetFormActions { update: (updater: (s: WidgetFormState) => WidgetFormState) => void; submit: () => void }
interface WidgetFormContextValue { state: WidgetFormState; actions: WidgetFormActions }
```

A `CreateWidgetProvider` (local `useState`) and an `EditWidgetProvider`
(pre-populated from a query, submits a PATCH) both implement the same
interface — the form UI underneath doesn't change, only the provider
swaps.

## React 19 note (this project's Next.js version)

If this project is on React 19 (the default for new Next.js apps as of
this writing): `ref` is a normal prop, no `forwardRef` needed, and `use()`
replaces `useContext()` — `use()` can also be called conditionally.

```tsx
// React 19 — no forwardRef
function WidgetInput({ ref, ...props }: Props & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}

// use() instead of useContext()
const { widget } = use(WidgetCardContext)!;
```

If the project is pinned to React 18, ignore this section — `forwardRef`
and `useContext` are still correct there.
