# Radix API Reference (and recognizing `base` examples)

This project uses **Radix** primitives (`base` field in `components.json`
is `"radix"`). Most of the time this file just confirms the Radix shape
you'd expect. It matters most when a registry example, blog post, or
AI-generated snippet was written for shadcn's newer `base` primitive
library instead — the two have different APIs for the same component
names, and the wrong one compiles-looking-plausible but behaves wrong
(e.g. silently not opening, or crashing on an array vs scalar mismatch).
If a snippet uses `render={<X />}` instead of `asChild`, it's `base` —
translate it before using it here.

## Composition: asChild (this project) vs render (base)

Radix replaces the default rendered element via `asChild`. Never wrap the
trigger's child in an extra element.

**Incorrect:**

```tsx
<DialogTrigger>
  <div><Button>Open</Button></div>
</DialogTrigger>
```

**Correct (this project, Radix):**

```tsx
<DialogTrigger asChild>
  <Button>Open</Button>
</DialogTrigger>
```

If you see `<DialogTrigger render={<Button />}>Open</DialogTrigger>`
elsewhere, that's the `base` library's syntax — rewrite to `asChild` form
for this project.

Applies to every trigger/close component: `DialogTrigger`, `SheetTrigger`,
`AlertDialogTrigger`, `DropdownMenuTrigger`, `PopoverTrigger`,
`TooltipTrigger`, `CollapsibleTrigger`, `DialogClose`, `SheetClose`,
`NavigationMenuLink`, `BreadcrumbLink`, `SidebarMenuButton`.

## Select

Radix: inline JSX only, no `items` prop, placeholder via `SelectValue`.

```tsx
<Select onValueChange={setType} defaultValue="kpi">
  <SelectTrigger>
    <SelectValue placeholder="Select a widget type" />
  </SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectItem value="kpi">KPI</SelectItem>
      <SelectItem value="chart">Chart</SelectItem>
      <SelectItem value="table">Table</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>
```

Content positioning uses `position="popper"` (not `alignItemWithTrigger`
— that's `base`'s prop name). Radix `Select` is single-select, string
values only — if a snippet shows `multiple` or object values on `Select`,
that's `base`; for multi-select here, compose a `Command` +
`Popover` instead, or ask before reaching for a non-Radix pattern.

## ToggleGroup

Radix: `type="single"` or `type="multiple"`; `defaultValue`/`value` is a
plain string for single-select.

```tsx
<ToggleGroup type="single" defaultValue="7d" spacing={2}>
  <ToggleGroupItem value="24h">24h</ToggleGroupItem>
  <ToggleGroupItem value="7d">7d</ToggleGroupItem>
</ToggleGroup>

// Multi-selection:
<ToggleGroup type="multiple">
  <ToggleGroupItem value="bold">Bold</ToggleGroupItem>
</ToggleGroup>
```

Controlled: `value`/`onValueChange` take a plain string for
`type="single"`. (`base`'s equivalent wraps everything in arrays and uses
a `multiple` boolean instead of `type` — don't mix the two shapes.)

## Slider

Radix always requires an array, even for one thumb:

```tsx
<Slider defaultValue={[50]} max={100} step={1} />
```

(`base` accepts a plain number for a single thumb — if you see
`defaultValue={50}` on a `Slider` example, that's `base`'s shape.)

## Accordion

Radix requires `type="single"` or `type="multiple"` and supports
`collapsible`; `defaultValue` is a string for single mode:

```tsx
<Accordion type="single" collapsible defaultValue="item-1">
  <AccordionItem value="item-1">...</AccordionItem>
</Accordion>
```

(`base` has no `type` prop, uses a `multiple` boolean, and `defaultValue`
is always an array — a different shape from the above.)

## Button/trigger rendering a non-button element

Radix: `asChild` handles this the same way regardless of the target
element (`<a>`, `<span>`, etc.) — no extra prop needed:

```tsx
<Button asChild>
  <a href="/docs">Read the docs</a>
</Button>
```

(`base` requires an explicit `nativeButton={false}` alongside `render`
when the target isn't a real button — not applicable here.)
