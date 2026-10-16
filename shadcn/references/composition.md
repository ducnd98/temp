# Component Composition

Adapted from shadcn/ui's official conventions. The through-line: shadcn
ships more than the visible primitive — a `Group`, a `Header`, a
`Fallback` — and skipping those pieces is how "looks right in the
preview" code breaks accessibility or visual consistency later.

## Contents

- Items always live inside their Group
- Callouts use Alert
- Empty states use Empty
- Toasts use sonner
- Choosing between overlay components
- Dialog/Sheet/Drawer always need a Title
- Card uses full composition
- Button has no loading prop
- TabsTrigger must be inside TabsList
- Avatar always needs AvatarFallback
- Prefer existing components over custom markup

---

## Items always live inside their Group

Never render an item directly inside the content container — the Group
is what wires up keyboard navigation and ARIA roles for the collection.

**Incorrect:**

```tsx
<SelectContent>
  <SelectItem value="kpi">KPI</SelectItem>
  <SelectItem value="chart">Chart</SelectItem>
</SelectContent>
```

**Correct:**

```tsx
<SelectContent>
  <SelectGroup>
    <SelectItem value="kpi">KPI</SelectItem>
    <SelectItem value="chart">Chart</SelectItem>
  </SelectGroup>
</SelectContent>
```

| Item | Group |
|---|---|
| `SelectItem`, `SelectLabel` | `SelectGroup` |
| `DropdownMenuItem`, `DropdownMenuLabel`, `DropdownMenuSub` | `DropdownMenuGroup` |
| `MenubarItem` | `MenubarGroup` |
| `ContextMenuItem` | `ContextMenuGroup` |
| `CommandItem` | `CommandGroup` |

## Callouts use Alert

```tsx
<Alert>
  <AlertTitle>Widget deleted</AlertTitle>
  <AlertDescription>This action can't be undone.</AlertDescription>
</Alert>
```

Not a hand-styled `div` with a colored border.

## Empty states use Empty

A dashboard with zero widgets/dashboards/datasources is a common state
here — always route it through `Empty`, not custom markup:

```tsx
<Empty>
  <EmptyHeader>
    <EmptyMedia variant="icon"><LayoutDashboardIcon /></EmptyMedia>
    <EmptyTitle>No widgets yet</EmptyTitle>
    <EmptyDescription>Create your first widget to start building this dashboard.</EmptyDescription>
  </EmptyHeader>
  <EmptyContent>
    <Button>Create widget</Button>
  </EmptyContent>
</Empty>
```

(See the `frontend-design` skill: an empty state is "an invitation to
act," not a blank apology — `Empty`'s structure is built for that.)

## Toasts use sonner

```tsx
import { toast } from "sonner";

toast.success("Widget created.");
toast.error("Couldn't save — try again.");
toast("Widget deleted.", { action: { label: "Undo", onClick: () => undoDelete() } });
```

Pair this with the `nextjs` skill's mutation conventions: fire the toast
from the `onSuccess`/`onError` of the `useMutation` call, not from inside
the component's render logic.

## Choosing between overlay components

| Use case | Component |
|---|---|
| Focused task needing input (create/edit widget) | `Dialog` |
| Destructive action confirmation (delete widget) | `AlertDialog` |
| Side panel with details or filters | `Sheet` |
| Mobile-first bottom panel | `Drawer` |
| Quick info on hover | `HoverCard` |
| Small contextual content on click | `Popover` |

## Dialog, Sheet, and Drawer always need a Title

Required for accessibility even when visually hidden:

```tsx
<DialogContent>
  <DialogHeader>
    <DialogTitle>Edit widget</DialogTitle>
    <DialogDescription>Update the widget's name and type.</DialogDescription>
  </DialogHeader>
  {/* form */}
</DialogContent>
```

Visually hidden but still accessible: `<DialogTitle className="sr-only">`.

## Card uses full composition

Don't dump everything into `CardContent`:

```tsx
<Card>
  <CardHeader>
    <CardTitle>Revenue</CardTitle>
    <CardDescription>Last 30 days</CardDescription>
  </CardHeader>
  <CardContent>{/* the chart or KPI value */}</CardContent>
  <CardFooter>
    <Button variant="ghost" size="sm">View details</Button>
  </CardFooter>
</Card>
```

## Button has no loading prop

There's no `isPending`/`isLoading` — compose `Spinner` + `disabled`:

```tsx
<Button disabled={createWidget.isPending}>
  {createWidget.isPending ? <Spinner data-icon="inline-start" /> : null}
  {createWidget.isPending ? "Saving..." : "Save"}
</Button>
```

## TabsTrigger must be inside TabsList

```tsx
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">...</TabsContent>
</Tabs>
```

## Avatar always needs AvatarFallback

```tsx
<Avatar>
  <AvatarImage src={user.avatarUrl} alt={user.name} />
  <AvatarFallback>{user.name.slice(0, 2).toUpperCase()}</AvatarFallback>
</Avatar>
```

## Prefer existing components over custom markup

| Instead of | Use |
|---|---|
| `<hr>` / `<div className="border-t">` | `<Separator />` |
| `<div className="animate-pulse">` styled divs | `<Skeleton className="h-4 w-3/4" />` |
| `<span className="rounded-full bg-green-100 ...">` | `<Badge variant="secondary">` |
