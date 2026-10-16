# Customization & Theming

The **mechanics** of theming — what a CSS variable does, where it lives,
how dark mode resolves. **What** the palette/typography should actually
be is a `frontend-design` (and `dataviz`, for chart colors) decision —
read those skills for the creative brief; read this file for how to
implement whatever they decide.

## Contents

- How it works
- Color variables (OKLCH)
- Dark mode (next-themes)
- Applying a preset
- Adding a custom color (Tailwind v4)
- Border radius
- Customization order of preference

---

## How it works

1. CSS variables defined in `:root` (light) and `.dark` (dark mode), in
   the project's global CSS file (`app/globals.css` — see
   [template.md](template.md)).
2. Tailwind v4's `@theme inline` block maps them to utility classes:
   `bg-primary`, `text-muted-foreground`, etc.
3. Components reference the utilities, never a raw color — change the
   variable once, every component using it updates.

## Color variables

Every color follows the `name`/`name-foreground` pairing — the base
variable is the background, `-foreground` is text/icons on top of it.

| Variable | Purpose |
|---|---|
| `--background` / `--foreground` | Page background, default text |
| `--card` / `--card-foreground` | Card surfaces |
| `--primary` / `--primary-foreground` | Primary actions |
| `--secondary` / `--secondary-foreground` | Secondary actions |
| `--muted` / `--muted-foreground` | Muted/disabled states |
| `--accent` / `--accent-foreground` | Hover/accent states |
| `--destructive` / `--destructive-foreground` | Errors, destructive actions |
| `--border` / `--input` / `--ring` | Borders, input borders, focus ring |
| `--chart-1` … `--chart-5` | Data visualization — see `dataviz` skill |
| `--sidebar-*` | Sidebar-specific colors |

Colors use OKLCH: `--primary: oklch(0.205 0 0)` (lightness 0-1, chroma —
0 is gray, hue 0-360). OKLCH is perceptually uniform, which is why
shadcn's presets use it instead of hex/RGB — easier to generate a
consistent light/dark pair by adjusting just the lightness channel.

## Dark mode (next-themes)

Class-based toggle (`.dark` on `<html>`), wired once in the root layout
via `next-themes` — see [template.md](template.md) for the exact
`ThemeProvider` setup already in this project's scaffold. Don't
reimplement theme switching with a custom context/localStorage hook;
`next-themes` already handles system-preference detection, no-flash SSR,
and persistence.

## Applying a preset

If `frontend-design` specifies a named preset or a preset code from
ui.shadcn.com:

```bash
# Overwrite: preserves nothing, use when components aren't customized yet.
npx shadcn@latest apply <preset-code>

# Preserve components, only update theme/fonts:
npx shadcn@latest apply <preset-code> --only theme,font

# Merge (keep local edits, update everything else) — see cli.md for the
# full per-file dry-run/diff workflow.
```

Never hand-decode a preset code — always pass it straight to the CLI.

## Adding a custom color (Tailwind v4)

This project is Tailwind v4 (CSS-first — see [template.md](template.md)),
so custom tokens are added directly in `app/globals.css`, never in a
separate file and never via a `tailwind.config.js` (v4 doesn't use one):

```css
/* 1. Define light and dark values. */
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}
.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}

/* 2. Register with Tailwind's @theme inline block. */
@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

```tsx
// 3. Use it like any other semantic token.
<div className="bg-warning text-warning-foreground">Approaching limit</div>
```

## Border radius

`--radius` controls border radius globally — `rounded-lg` derives from
`var(--radius)`, `rounded-md` is `calc(var(--radius) - 2px)`, etc.
Changing one variable reshapes every component consistently; don't
override `rounded-*` per-component to "fix" a radius that's actually a
global design decision.

## Customization order of preference

Try these in order — reach for the next one only when the current one
genuinely can't express what's needed:

1. **Built-in variant** — `<Button variant="outline" size="sm">`.
2. **`className` for layout** (not color/typography) — `<Card className="max-w-md mx-auto">`.
3. **A new variant**, added to the component's source (it's local source
   code, editing it is normal here) via its `cva` config:
   ```tsx
   // components/ui/button.tsx
   warning: "bg-warning text-warning-foreground hover:bg-warning/90",
   ```
4. **A wrapper component**, composing primitives into a higher-level one:
   ```tsx
   export function ConfirmDeleteDialog({ resourceName, onConfirm, children }: Props) {
     return (
       <AlertDialog>
         <AlertDialogTrigger asChild>{children}</AlertDialogTrigger>
         <AlertDialogContent>
           <AlertDialogHeader>
             <AlertDialogTitle>Delete {resourceName}?</AlertDialogTitle>
             <AlertDialogDescription>This can't be undone.</AlertDialogDescription>
           </AlertDialogHeader>
           <AlertDialogFooter>
             <AlertDialogCancel>Cancel</AlertDialogCancel>
             <AlertDialogAction onClick={onConfirm}>Delete</AlertDialogAction>
           </AlertDialogFooter>
         </AlertDialogContent>
       </AlertDialog>
     );
   }
   ```

Skipping straight to (3) or (4) when (1)/(2) would've worked is how a
codebase ends up with three near-identical button variants nobody
remembers the difference between.

## Customizing without breaking accessibility

Radix gives every primitive correct keyboard navigation, focus
management, and screen-reader semantics for free — that's most of the
value of not hand-rolling a `Dialog` or `Select`. Editing a primitive's
source (option 3 above) or restructuring its markup can silently break
that: removing a wrapping element changes focus trap boundaries,
overriding `role`/`aria-*` attributes changes what a screen reader
announces, reordering children can change tab order. If a customization
touches structure (not just Tailwind classes), tab through it with the
keyboard and check the accessible name/role make sense before moving on
— don't assume "it still looks right" means "it still works right."
