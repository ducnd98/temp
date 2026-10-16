---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults. In this repo, use it for visual-identity moments - the app shell, theme/palette decisions, landing pages, empty states - and for ALL UX copy (labels, buttons, error and empty-state text). Do NOT apply its "take an aesthetic risk" framing to routine CRUD screens, tables, or forms - those follow the shadcn skill's conventions and stay quiet; charts and data color follow the dataviz skill.
---

# Frontend Design

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. This client has already rejected proposals that felt templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take one real aesthetic risk you can justify.

## Ground it in the subject

If the brief does not pin down what the product or subject is, pin it yourself before designing: name one concrete subject, its audience, and the page's single job, and state your choice. If there's any information in your memory about the human's preferences, context about what they're building, or designs you've made before – use that as a hint. The subject's own world, its materials, instruments, artifacts, and vernacular, is where distinctive choices come from. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is a thesis. Open with the most characteristic thing in the subject's world, in whatever form makes sense for it: a headline, an image, an animation, a live demo, an interactive moment. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the template answer, only use if that's truly the best option.

Typography carries the personality of the page. Pair the display and body faces deliberately, not the same families you would reach for on any other project, and set a clear type scale with intentional weights, widths, and spacing. Make the type treatment itself a memorable part of the design, not a neutral delivery vehicle for the content.

Structure is information. Structural devices, numbering, eyebrows, dividers, labels, should encode something true about the content, not decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence - like a real process or a typed timeline where order carries information the reader needs. Question if choices like numbered markers actually make sense before incorporating them.

Leverage motion deliberately. Think about where and if animation can serve the subject: a page-load sequence, a scroll-triggered reveal, hover micro-interactions, ambient atmosphere. An orchestrated moment usually lands harder than scattered effects; choose what the direction calls for. However, sometimes less is more, and extra animation contributes to the feeling that the design is AI-generated.

Match complexity to the vision. Maximalist directions need elaborate execution; minimal directions need precision in spacing, type, and detail. Elegance is executing the chosen vision well.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: brainstorm, explore, plan, critique, build, critique again

For calibration: AI-generated design right now clusters around three looks: (1) a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta accent; (2) a near-black background with a single bright acid-green or vermilion accent; (3) a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns. All three are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. Just like a human designer who's hired, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the human's design brief: create a compact token system with color, type, layout, and signature.

### Design Intelligence: Leverage `ui-ux-pro-max`
To ground your choices in verified design patterns instead of defaulting to generic AI tropes, run targeted searches:
```bash
# Generate complete design system recommendation (palette, type scale, tokens)
python .gemini/skills/ui-ux-pro-max/scripts/search.py "<subject/industry>" --design-system -p "<ProjectName>"

# Search curated product color palettes and reasoning profiles
python .gemini/skills/ui-ux-pro-max/scripts/search.py "<industry or mood>" --domain color

# Search typography and font pairings matching the aesthetic
python .gemini/skills/ui-ux-pro-max/scripts/search.py "<style keyword>" --domain typography

# Search hero/landing layout structures and CTA patterns
python .gemini/skills/ui-ux-pro-max/scripts/search.py "<page intent>" --domain landing

# Search motion/GSAP presets for purposeful animation
python .gemini/skills/ui-ux-pro-max/scripts/search.py "<animation type>" --domain gsap
```

Use the search output to populate:
- **Color:** describe the palette as 4–6 named hex values (grounded in the `--domain color` or `--design-system` output).
- **Type:** the typefaces for 2+ roles (from `--domain typography`).
- **Layout:** a layout concept, using one-sentence prose descriptions and ASCII wireframes (informed by `--domain landing`).
- **Signature:** the single unique element this page will be remembered by that embodies the brief in an appropriate way.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan exactly and deriving every color and type decision from it.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and a element-based selector like .cta). This can happen often with paddings/margins between sections.

Try to do a lot of this planning and iteration in your thinking, and only show ideas to the user when you have higher confidence it'll delight them.

## Restraint and self-critique

Spend your boldness in one place. Let the signature element be the one memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Not taking a risk can be a risk itself! Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected. Critique your own work as you build, taking screenshots if your environment supports it – a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creators have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## Pragmatic Minimalism & Anti-Overengineering (Developer & Registry Tools)

For developer platforms, skill registries, and technical portals, **clarity, speed, and clean typography strictly trump decorative ornamentation**:

1. **Forbid Fake UI Embellishments**:
   - Never add simulated OS chrome (e.g. fake macOS red/yellow/green window dots) to code boxes.
   - Never inject arbitrary, decorative badges (e.g. "Agent Contract") that carry no concrete system meaning.
   - Never generate bloated 4-column mega footers with filler links when a clean, single-line copyright banner is appropriate.
2. **Bidirectional Control Integrity**:
   - Sort toolbars must provide both criteria selection and an interactive Ascending/Descending direction toggle button (`Asc / Desc`) with directional icons (`ArrowDownWideNarrow` / `ArrowUpNarrowWide`).
3. **Dual-Theme Verification Rigour**:
   - Never hardcode dark colors (e.g. `bg-slate-900`) without explicit light-mode pairing (`bg-slate-100 dark:bg-zinc-950`).
   - Always ensure adequate breathing space between major structural blocks (e.g. `mt-16`/`mt-20` on Footers).
4. **Keyboard Shortcut Legibility**:
   - Keycap indicators (e.g. `Ctrl` and `K`) within a single badge must feature distinct, visible spacing (`gap-2`), never blending into an unreadable `CtrlK`.
5. **Context-Aware Navigation on Auth**:
   - Authentication must never hijack user navigation. Logging in from a public catalog or detail page must keep the user on that page (or return to home), displaying active auth in the navbar. Never force-redirect to admin panels unless the user explicitly intended to access an admin URL.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand, and therefore easier to use. They are design material, not decoration. Bring the same intentionality to copy that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's side of the screen. Name things by what people control and recognize, never by how the system is built. A person manages notifications, not webhook config. Describe what something does in plain terms rather than selling it. Being specific is always better than being clever.

Use active voice as default. A control should say exactly what happens when it's used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the register conversational and tuned: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each element do exactly one job. A label labels, an example demonstrates, and nothing quietly does double duty.

## SaaS Console & Admin Dashboard Architecture (Universal Layout Principles)

When designing or implementing any Admin Console, Management Portal, or SaaS Dashboard, enforce these universal layout and interaction principles across every screen:

### 1. Viewport & Shell Isolation (Full-Bleed Workspace)
- **Shell Separation**: Administrative interfaces must completely unmount consumer/public shells (consumer Navbar and Footer).
- **Full-Bleed Edge-to-Edge**: Admin layouts are strictly `w-full min-h-screen bg-background`. Never artificially wrap dashboard tables inside fixed-width containers (`container`, `max-w-7xl`), preserving maximum screen real-estate for multi-column data tables.
- **Scrollbar Gutter Stabilization**: Enforce `html { scrollbar-gutter: stable; }` in CSS to eliminate the 15px layout shift when navigating between tall and short data tables.

### 2. Flush-Left Collapsible Sidebar
- **Zero-Margin Attachment**: Sidebar is attached flush against the left viewport edge (`left-0 top-0 h-screen sticky border-r w-64`) with 0 margin/padding.
- **Collapsible Workspace Mode**:
  - Top-left header contains a collapse toggle (`PanelLeftClose`). When collapsed, the sidebar slides completely away, freeing 100% width for wide tables. An expand toggle (`PanelLeftOpen`) appears on the persistent top bar.
  - Collapse state MUST be persisted in `localStorage` across page reloads.
- **Typography & Visual Hygiene**:
  - Navigation links must use relaxed **`font-medium`** (never aggressive `font-bold` or `font-semibold` that visually exhausts users).
  - Navigation icons use standardized **16px (`h-4 w-4`)** bounding boxes.
  - Omit distracting numeric badges from navigation menus; omit public shortcuts or sign-out links from the sidebar bottom.

### 3. Global Identity & Corner Anchor Principle
- **Brand Single Source of Truth (`BrandLogo`)**: The webapp logo (icon + styling + typography) must be encapsulated into a single shared component (`BrandLogo`). Changing brand identity anywhere updates the entire system (Public, Admin, Auth) simultaneously.
- **Corner Anchor User Menu (`UserMenu`)**:
  - In top navigation headers, the **User Avatar is ALWAYS anchored at the outermost top-right corner**.
  - Auxiliary utilities (such as Theme Toggles) sit immediately to the left of the avatar, NEVER on the outer corner.
  - Avatar button is circular (`rounded-full`), expanding on click into a dropdown containing user credentials, role badge, dashboard links, and sign-out.

### 4. Action & Control Parity (Reusability & Consistency)
- **Primary Action Button Parity**:
  - Content toolbars across all management views/tabs must use the **identical, standardized button contract**: **`+ Add`** with a `Plus` icon (`h-4 w-4`, `h-10 text-sm`). Never invent divergent ad-hoc labels like "+ Add New Category", "+ Create Skill", or "+ New Item".
- **Table Row Actions**:
  - Table action columns are right-aligned and strictly use **side-by-side icon buttons**: `Pencil` (Edit) and `Trash2` (Delete) at 16px (`h-4 w-4`), avoiding space-wasting text buttons.
- **Clean Filters**:
  - Filter dropdowns show clean entity names in Title Case (e.g. "All Categories", "Productivity"), omitting distracting count suffixes like `(12)`.

### 5. Zero Layout Shift (CLS = 0) & Timed Circular Progress Toasts
- **No Layout-Shifting Banners**: Error banners and success callouts must NEVER be injected into the body of forms, modals, or table headers, preventing jarring layout shifts.
- **Floating Edge Feedback**: All action feedback displays as a floating card anchored at the viewport edge (`fixed bottom-6 right-6 z-50`).
- **Circular Countdown Progress**: Toasts feature an animated SVG circular progress indicator showing the exact auto-dismiss countdown (e.g. 4 seconds) before smoothly vanishing.

### 6. Minimalist Table & Pagination Ergonomics
- **Unbolded Numerical Data**: Standard numeric cells (IDs, download counts, timestamps, bytes) must use `font-mono font-normal`, reserving bold weights solely for primary entity names.
- **Right-Aligned Minimal Pagination**:
  - Table pagination is pinned to the table card footer and right-aligned.
  - Omit verbose verbose sentences like "Showing 1 to 10 of 15 items".
  - Display solely: `[ Previous ]  Page X of Y  [ Next ]`.
  - Pagination status `Page X of Y` is **always visible** whenever data is present.

