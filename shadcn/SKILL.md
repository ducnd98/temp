---
name: shadcn
description: How to add, compose, style, and theme shadcn/ui components correctly in this monorepo's Next.js frontend (Tailwind v4, Radix primitives, Lucide icons, Surface Elevation & Visual Contrast, Tonal Tinting over harsh solid blocks). Use whenever adding a UI component, building a form, a dialog/sheet, a card, a sidebar, tags, badges, buttons, empty states, or any visual element. Also use when styling dark mode, light mode, fixing color contrast, card-in-card ambiguity, or when a component looks 'off' / flat / inconsistent. Triggers on: 'style', 'màu sắc', 'dark mode', 'light mode', 'contrast', 'elevation', 'card', 'badge', 'tag', 'theme', 'ui-ux', 'shadcn', 'tô màu', 'thiết kế', 'giao diện'.
---

# shadcn/ui

shadcn/ui isn't a component library you import — components are installed
as editable source files in this project. That changes the failure mode:
there's no version to pin and no upstream bug to wait out, but there's also
no guardrail stopping you from hand-rolling something that already exists,
or drifting from the conventions that make every component predictable.
This skill is that guardrail.

Companion skill: `nextjs` decides *where* feature code lives (`features/`,
Server vs Client). This skill decides *how* the UI inside that code is
built. `dataviz` and `frontend-design` decide the visual identity (color,
type, chart design) — this skill implements that identity with the right
components, it doesn't choose the palette. `ui-ux-pro-max` provides the
searchable intelligence engine for shadcn component conventions and UX rules.

## Surface Elevation & Visual Contrast Standards

### 1. Mandatory Canvas vs Surface Elevation (Never `--card == --background`)
- **Dark Mode (Luminance Elevation)**:
  - Canvas `--background: 240 10% 3.9%` (`#09090b`).
  - Elevated Surface `--card: 240 6% 8.5%` (`#141418`) — Must have ~5% luminance elevation above background.
  - Clean Boundary `--border: 240 5% 18%` (`#2b2b35`).
  - Recessed Layer `--muted: 240 5% 13%` (`#1f1f25`).
- **Light Mode (Contrast Canvas)**:
  - Soft Canvas `--background: 240 5% 96%` (`#f4f4f7`) — Never pure white `#ffffff` canvas.
  - Elevated Surface `--card: 0 0% 100%` (`#ffffff`) — Pure white popping out with `shadow-xs hover:shadow-md`.
  - Clean Boundary `--border: 240 6% 86%` (`#dadbe3`).

### 2. Zero Opacity Dilution (No `bg-card/60` on Core Surfaces)
- Core containers (Sidebar, Skill Cards, Modal dialogs, Search bar) must use solid `bg-card`, NOT semi-transparent `bg-card/60` or blurry `glass-panel` that dilutes contrast and makes surfaces dissolve into the background.

### 3. Tonal Tinting for Interactive Chips (No Heavy Solid Blocks)
- Filter tags and facet chips are navigation filters, NOT primary "Buy Now" CTA buttons.
- NEVER use harsh, heavy solid blocks like `bg-violet-600 text-white` for active chips.
- USE elegant Tonal Tinting:
  - Inactive: `bg-card/40 border-border/70 text-muted-foreground hover:text-foreground hover:border-violet-500/30`.
  - Active: `bg-violet-500/15 border-violet-500/45 text-violet-300 font-medium shadow-xs` with a `<Check className="h-3 w-3 text-violet-400" />`.

## This project's setup

- **Primitives: Radix** (`base` field is `radix`, not the newer `base`
  library). Radix is the mature, widely-adopted choice; `base` is newer
  and less proven. If `npx shadcn@latest info` ever reports `base`
  instead, something drifted from this decision — flag it.
- **Icons: `lucide-react`.**
- **Tailwind v4**, CSS-first config (`@import "tailwindcss"` +
  `@theme inline`, no `tailwind.config.js`).
- **Dark mode: `next-themes`**, class-based (`attribute="class"` on
  `ThemeProvider`).
- Scaffolded via template: see `references/template.md`.

## Golden rule: compose before you write a single div

Before writing ANY UI markup, check if it already exists:

1. Look in `src/components/ui/` for components already installed.
2. If not installed, check if shadcn has it: `npx shadcn@latest add <component>`.
3. Read `references/composition.md` for how to assemble existing components into patterns.

Every visual element must trace back to a shadcn primitive or an intentional composition of them. Never hand-roll a modal (use `Dialog`), a dropdown (use `DropdownMenu`), a tooltip (use `Tooltip`), or a form field (use `Form` + `FormField`).

## References

- `references/composition.md`: assembling components into common patterns
- `references/styling.md`: customizing styles, themes, and CSS variables
- `references/icons.md`: icon usage conventions and common pairings
- `references/accessibility.md`: keyboard navigation, ARIA, and focus management
- `references/template.md`: initial scaffolding and dependency setup
