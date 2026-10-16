# Styling & Tailwind

## Contents

- Semantic colors, not raw Tailwind colors
- Built-in variants before custom styles
- className is for layout, not color/typography overrides
- No space-x-*/space-y-* — use gap-*
- size-* over w-* h-* when equal
- truncate shorthand
- No manual dark: overrides
- Use cn() for conditional classes
- No manual z-index on overlay components

---

## Semantic colors, not raw Tailwind colors

Every semantic token has a `-foreground` pair for text/icons on that
background. Raw palette colors (`bg-blue-500`, `text-emerald-600`) don't
adapt to dark mode or a theme change — semantic tokens do, because
they're CSS variables (see
[customization.md](customization.md)).

**Incorrect:**

```tsx
<div className="bg-blue-500 text-white">
  <p className="text-gray-600">Last updated 2 minutes ago</p>
</div>
<span className="text-emerald-600">+20.1%</span>
```

**Correct:**

```tsx
<div className="bg-primary text-primary-foreground">
  <p className="text-muted-foreground">Last updated 2 minutes ago</p>
</div>
<Badge variant="secondary">+20.1%</Badge>
```

For status indicators (positive/negative deltas, active/inactive), prefer
`Badge` variants or `text-destructive` over inventing a raw color. If a
genuinely new semantic meaning is needed (e.g. a "warning" state this
project doesn't have yet), that's a `customization.md` decision (a new
CSS variable), not a one-off Tailwind class.

## Built-in variants before custom styles

**Incorrect:**

```tsx
<Button className="border border-input bg-transparent hover:bg-accent">Cancel</Button>
```

**Correct:**

```tsx
<Button variant="outline">Cancel</Button>
```

Customization order of preference (detailed in
[customization.md](customization.md)): variant → semantic token →
new variant → wrapper component. Reach for the next one only when the
previous genuinely doesn't cover the need.

## className is for layout, not color/typography overrides

`className` is for layout (`max-w-md`, `mx-auto`, `mt-4`) — never for
overriding a component's colors or typography.

**Incorrect:**

```tsx
<Card className="bg-blue-100 text-blue-900 font-bold">
```

**Correct:**

```tsx
<Card className="max-w-md mx-auto">
```

## No space-x-*/space-y-* — use gap-*

```tsx
// Wrong: space-y-4
// Right:
<div className="flex flex-col gap-4">
  <Input />
  <Input />
  <Button>Submit</Button>
</div>
```

## size-* over w-* h-* when equal

`size-10`, not `w-10 h-10` — for icons, avatars, skeletons, anything
square.

## truncate shorthand

`truncate`, not `overflow-hidden text-ellipsis whitespace-nowrap`.

## No manual dark: overrides

Semantic tokens already resolve differently in light/dark via CSS
variables (see [customization.md](customization.md)'s dark mode section
and the project scaffold in [template.md](template.md), which wires
`next-themes`). Don't
write `bg-white dark:bg-gray-950` — write `bg-background text-foreground`
and let the token handle both modes.

## Use cn() for conditional classes

```tsx
import { cn } from "@/lib/utils";

<div className={cn("flex items-center", isActive ? "bg-primary text-primary-foreground" : "bg-muted")}>
```

Not a manual template-literal ternary.

## No manual z-index on overlay components

`Dialog`, `Sheet`, `Drawer`, `AlertDialog`, `DropdownMenu`, `Popover`,
`Tooltip`, `HoverCard` manage their own stacking context. Adding `z-50`
or `z-[999]` on top is either a no-op or, worse, breaks stacking relative
to a different overlay.

## Badge & Tag Tokens: The Light/Dark Mode Contrast Trap

Never hardcode white-based borders or backgrounds like `border-white/10 bg-white/5` for tags or badges. On light backgrounds (`#ffffff` / `#f8fafc`), white is completely invisible, leaving tags looking borderless and broken.

**Incorrect:**
``tsx
tag: "border border-white/10 bg-white/5 text-muted-foreground"
``

**Correct:**
``tsx
tag: "border border-border/80 bg-muted/40 text-muted-foreground hover:text-foreground hover:border-violet-500/40 dark:border-white/10 dark:bg-white/5"
category: "border border-indigo-500/30 bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 font-medium"
``
Using `border-border/80` resolves cleanly to `--border` (`#e2e8f0` in light mode), guaranteeing high-contrast, accessible borders in both light and dark themes.

## Compact Tag Overflow (+N Pattern) on Cards

When displaying entity tags on catalog/grid cards (e.g. `SkillCard`), never render an unbounded list that wraps onto multiple lines and misaligns grid cards.
Instead, render at most 3 tags, and aggregate remaining items into a `+N` badge:

``tsx
<div className="flex flex-wrap gap-1.5 mt-4 min-h-[26px]">
  {skill.tags && skill.tags.length > 0 ? (
    skill.tags.slice(0, 3).map((tag) => (
      <Badge key={tag} variant="tag" className="text-[10px] py-0 px-2 font-normal">
        #{tag}
      </Badge>
    ))
  ) : (
    <span className="text-[11px] text-muted-foreground/60 italic">No tags</span>
  )}
  {skill.tags && skill.tags.length > 3 && (
    <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded-md border border-border bg-muted/60 text-muted-foreground self-center">
      +{skill.tags.length - 3}
    </span>
  )}
</div>
``
