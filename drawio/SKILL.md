---
name: drawio
description: Use when the user requests diagrams, flowcharts, architecture diagrams, ER diagrams, UML class/sequence diagrams, network topology, mind maps, workflow diagrams, or any visualization that benefits from structured layout. Also use proactively when explaining systems with 3+ components or complex data flows. Generates native .drawio XML files with professional styling.
---

# Draw.io Diagram Skill

## Overview

Generate professional, clean, and beautiful `.drawio` XML files for any type of diagram. The output is native draw.io format — editable in the draw.io desktop app or diagrams.net web editor.

**Core principle:** Every diagram must be **immediately readable** — clear hierarchy, consistent spacing, no overlapping elements, and a harmonious color palette.

## When to Use

- User asks for a diagram, flowchart, ERD, UML, architecture diagram, sequence diagram, workflow, mind map, network topology, or any visual representation
- Explaining a system with 3+ components that benefits from visualization
- User mentions `.drawio`, `draw.io`, or `diagrams.net`
- User asks to export diagrams to PNG/SVG/PDF
- User asks to **modify or update** an existing `.drawio` diagram

**When NOT to use:**
- Simple 2-3 item lists that don't need visual representation
- User explicitly requests Mermaid, PlantUML, or ASCII diagrams instead
- Gantt charts or timeline charts (draw.io handles these poorly — suggest alternatives)

## Quick Reference

| Diagram Type | Layout | Key Shapes | Spacing |
|-------------|--------|------------|---------|
| Flowchart | TB (top-bottom) | `rounded=1` rectangles, `rhombus` decisions, `ellipse` start/end | 200px vertical |
| ERD | TB | `shape=table` with `childLayout=tableLayout` | 300px between tables |
| UML Class | TB | `swimlane` with 3 sections (name, attributes, methods) | 250px between classes |
| Architecture | LR (left-right) | Cylinders, clouds, rounded rects in swimlane containers | 250px horizontal |
| Sequence | TB | `shape=umlLifeline` participants, horizontal message edges | 200px between lifelines |
| Workflow/BPMN | LR | Horizontal swimlanes (`horizontal=0`), circles, diamonds | 200px horizontal |
| Mind Map | Radial | Rounded rects, varying sizes by depth (200→160→140px wide) | 200px radial |
| Network | Grid | Rectangles (servers), cylinders (DB), clouds (internet) | 250px grid |

---

## XML Structure — MANDATORY Rules

Every `.drawio` file MUST follow this exact structure. **Violations will produce broken files.**

```xml
<mxfile>
  <diagram name="Page-1" id="unique-id">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1169" pageHeight="827"
                  math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- All shapes and edges go here as XML siblings -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Multi-page diagrams:** To create multiple pages, add additional `<diagram name="Page-2" id="unique-id-2">` elements inside `<mxfile>`. Use for large systems (e.g., Page 1: high-level architecture, Page 2: detailed component view).

**Canvas sizing:** Adjust `pageWidth` and `pageHeight` for larger diagrams. For 10+ elements, use `pageWidth="1600" pageHeight="1000"` or larger. Set `dx` and `dy` to match.

### Iron Rules — NEVER violate these

1. **Always include `id="0"` and `id="1"` root cells** — missing these = broken file
2. **Every `mxCell` must have a unique `id`** — use sequential integers starting from `2`
3. **All `mxCell` elements are direct XML children of `<root>`** — NEVER nest `<mxCell>` inside another `<mxCell>` in the XML tree. Logical parent-child relationships (e.g., shapes inside containers) are expressed via the `parent` attribute, NOT by XML nesting. A shape with `parent="2"` is still a direct XML child of `<root>`.
4. **Vertices need `vertex="1"`** — shapes without this won't render
5. **Edges need `edge="1"`** — connectors without this won't render
6. **Edge `source` and `target` must reference existing cell IDs** — mismatched IDs = dangling arrows
7. **Edges MUST use expanded form** — `<mxCell edge="1" ...><mxGeometry relative="1" as="geometry" /></mxCell>`, NOT self-closing `<mxCell ... edge="1" />`
8. **Use XML entities for special characters** — `&amp;` `&lt;` `&gt;` `&quot;` in `value` attributes
9. **Use `&#xa;` for line breaks** in label text, NOT literal `\n`
10. **No `--` inside XML comments** — illegal per XML spec. Prefer avoiding XML comments entirely.
11. **Use uncompressed XML only** — never Base64/compressed format
12. **Child coordinates are RELATIVE to parent container** — When a shape has `parent="X"` where X is a container/swimlane, its `(x, y)` position is relative to the top-left corner of that container's content area (below the title bar). Factor in `startSize` (typically 30px) when calculating y positions inside containers. Only shapes with `parent="1"` use absolute canvas coordinates.
13. **No duplicate style keys** — If you write `rounded=1;rounded=0;` the last value wins, causing confusion. Each style key must appear exactly once.
14. **Calculate container dimensions explicitly** — draw.io does NOT auto-size containers. You must calculate: `width = max(child_x + child_width) + padding`, `height = startSize + max(child_y + child_height) + padding`. Use 40px padding on all sides.

---

## Professional Color Palette

Use these curated color combinations for clean, professional diagrams. Each pair is `(fillColor, strokeColor)`.

### Default Palette — Soft Professional

| Role | Fill | Stroke | Use For |
|------|------|--------|---------|
| Primary | `#dae8fc` | `#6c8ebf` | Main components, services, processes |
| Success | `#d5e8d4` | `#82b366` | Start nodes, databases, positive states |
| Warning | `#fff2cc` | `#d6b656` | Decisions, conditions, gateways |
| Danger | `#f8cecc` | `#b85450` | Errors, end nodes, critical paths |
| Neutral | `#f5f5f5` | `#666666` | External systems, notes, comments |
| Accent | `#e1d5e7` | `#9673a6` | Queues, middleware, special components |
| Info | `#d4e1f5` | `#3a7bbf` | APIs, gateways, interfaces |

**Font color:** `fontColor=#000000` (black) for all elements.

### Dark Palette — Modern Dark Theme

| Role | Fill | Stroke | Use For |
|------|------|--------|---------|
| Primary | `#1a1a2e` | `#4a9eff` | Main components |
| Success | `#0a2e1a` | `#00d68f` | Databases, positive |
| Warning | `#2e2a0a` | `#ffb800` | Decisions |
| Danger | `#2e0a0a` | `#ff4d4d` | Errors |
| Neutral | `#2d2d2d` | `#888888` | External |
| Accent | `#1a0a2e` | `#b366ff` | Special |
| Info | `#0a1a2e` | `#4a9eff` | APIs, gateways |

**Font color:** `fontColor=#e0e0e0` (light gray) for ALL elements when using the dark palette. Using `#000000` on dark backgrounds makes text invisible. Edge labels also use `fontColor=#e0e0e0`.

### Choosing a Palette

- **Default (Soft Professional):** Use unless the user explicitly requests dark mode
- **Dark (Modern Dark Theme):** Only when the user asks for dark mode, dark theme, or dark background
- When in doubt, use the Default palette

### Mapping Guide

| Element Type | Palette Role |
|-------------|-------------|
| Service / Process / Task | Primary |
| Database / Data Store | Success |
| Decision / Gateway / Condition | Warning |
| Error / End / Terminate | Danger |
| External System / User / Actor | Neutral |
| Queue / Cache / Middleware | Accent |
| API / Gateway / Interface | Info |
| Start node | Success (ellipse) |
| End node | Danger (ellipse) |
| Container / Swimlane | Use role of contained tier + `opacity=50` |

---

## Shape Templates

### Vertex (Shape) Template

```xml
<mxCell id="ID" value="LABEL"
  style="SHAPE_STYLE;whiteSpace=wrap;html=1;fillColor=FILL;strokeColor=STROKE;fontFamily=Inter;fontSize=12;fontColor=#000000;rounded=1;arcSize=10;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="X" y="Y" width="W" height="H" as="geometry" />
</mxCell>
```

**Notes:**
- Replace `SHAPE_STYLE` with the specific shape prefix (e.g., `rounded=1;arcSize=10` for rectangles, `ellipse` for circles). Do NOT combine conflicting shape styles (e.g., `ellipse;rounded=1` — `rounded` is meaningless on ellipses).
- `shadow=1` adds a subtle drop shadow. Omit for diagrams with 30+ elements to reduce visual noise.
- For dark palette, change `fontColor=#000000` to `fontColor=#e0e0e0`.

### Edge (Connector) Template

```xml
<mxCell id="ID" value="LABEL"
  style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="SOURCE_ID" target="TARGET_ID">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Notes:**
- For **unlabeled edges**, omit the `value` attribute entirely or set `value=""`. Do NOT use placeholder text.
- For dark palette, change `fontColor=#000000` to `fontColor=#e0e0e0` and `strokeColor` to the palette's stroke color.

### CRITICAL Edge Label Rule

**ALWAYS add `labelBackgroundColor=none;fontSize=12;fontColor=#000000;`** to every edge style. Without this, draw.io renders a white rectangle behind edge labels that covers shapes and other edges. Edge labels MUST be at least 12px size, with transparent backgrounds. This is the #1 visual defect in generated diagrams.

### Common Shape Styles

| Shape | Style Prefix |
|-------|-------------|
| Rectangle (rounded) | `rounded=1;arcSize=10;` |
| Ellipse | `ellipse;` |
| Diamond (decision) | `rhombus;` |
| Cylinder (database) | `shape=cylinder3;size=15;` |
| Cloud | `ellipse;shape=cloud;` |
| Document | `shape=document;` |
| Parallelogram (I/O) | `shape=parallelogram;perimeter=parallelogramPerimeter;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;` |
| Swimlane/Container | `swimlane;startSize=30;` |
| Actor (person) | `shape=mxgraph.basic.person;` |
| Note | `shape=note;size=15;` |

---

## Layout Rules — Clean & Professional

### Spacing Standards

| Context | Minimum Spacing |
|---------|----------------|
| Between shapes (same level) | 200px |
| Between levels/tiers | 250px |
| Between swimlane/container groups | 300px |
| ERD tables apart | 300px |
| UML classes apart | 250px |
| Edge routing corridors between columns | 100px clear space |
| Container internal padding | 40px all sides |
| Decision to error/failed node (vertical) | 60px vertical gap; expand parent swimlane height to at least 220px |

### Anti-Overlap Layout Rules — CRITICAL

**Edges crossing through unrelated shapes is the #1 visual defect.** Follow these rules strictly:

1. **Route edges AROUND containers, not through them** — if an edge connects two shapes in different containers, route it along the outside perimeter of containers using waypoints
2. **Reserve routing corridors** — leave 100px clear horizontal gaps between container groups specifically for edge routing. No shapes should be placed in these corridors
3. **Stagger vertical positions** — when multiple shapes in one column connect to shapes in a non-adjacent column, stagger their `y` positions to avoid edge path collisions
4. **Use explicit waypoints for complex paths** — when auto-routing would cross through shapes, add `<Array as="points"><mxPoint x="..." y="..." /></Array>` inside `<mxGeometry>` to manually route around obstacles
5. **Never let edges overlap with container borders** — ensure edges enter/exit containers cleanly from the edges, not through corners where they might clip titles
6. **For LR layouts with multiple tiers**: arrange containers in a single horizontal row with 100px routing corridors between them. Connect shapes left-to-right only — avoid backward or diagonal edges. If more than 5-6 tiers, consider wrapping to a second row with 300px vertical gap.

### Layout Calculation Guide

Before writing XML, calculate all positions:

```
For TB (top-to-bottom) layout:
  x_center = pageWidth / 2
  y_current = 40  (starting y)
  
  For each level:
    total_width = num_nodes * node_width + (num_nodes - 1) * h_spacing
    x_start = x_center - total_width / 2
    
    For each node in level:
      place at (x_start + i * (node_width + h_spacing), y_current)
    
    y_current += node_height + v_spacing (typically 200px)

For LR (left-to-right) layout:
  Swap x and y logic above
  x_current starts at 40, increments by node_width + h_spacing (200px)
  y positions center-aligned within each column
```

### Alignment Principles

1. **Grid-align all shapes** — snap to 10px grid (coordinates should be multiples of 10)
2. **Center-align shapes within columns** — same `x` for vertical flows
3. **Center-align shapes within rows** — same `y` for horizontal flows
4. **Consistent shape sizes** — same type = same dimensions
5. **Leave routing corridors** — 100px gaps between container groups for edge paths
6. **Group related items** — use physical proximity or containers
7. **Align container heights** — containers in the same row should have similar heights to keep edge routing clean

### Size Recommendations

| Shape Type | Width × Height |
|-----------|----------------|
| Standard process | 160 × 60 |
| Decision diamond | 120 × 80 |
| Start/End ellipse | 100 × 60 |
| Database cylinder | 120 × 80 |
| ERD table | 200 × (rows × 26 + 30) header |
| UML class | 200 × (26 + attributes_height + 8 + methods_height) |
| Container/Swimlane | Calculate: `width = max(child_x + child_width) + 40`, `height = startSize + max(child_y + child_height) + 40` |
| Lifeline (Sequence) | 100 × 400 (adjust height based on number of messages) |

### Typography

| Element | Font | Size | Style | Color |
|---------|------|------|-------|-------|
| Shape labels | Inter | 12px | Regular | Default: `#000000` / Dark: `#e0e0e0` |
| Edge labels | Inter | 12px | Regular, `labelBackgroundColor=none` | Default: `#000000` / Dark: `#e0e0e0` |
| Container titles | Inter | 14px | Bold (`fontStyle=1`) | Default: `#000000` / Dark: `#e0e0e0` |
| Notes/comments | Inter | 12px | Italic (`fontStyle=2`) | Default: `#000000` / Dark: `#e0e0e0` |

**Font note:** `Inter` works in diagrams.net (web) and draw.io desktop if installed on the system. If Inter is unavailable, draw.io falls back to its default sans-serif. For maximum portability, `Helvetica` is also a safe choice.

---

## Workflow — Step by Step

### Step 0: Check for Existing Diagram (Modification Mode)

**If the user asks to modify, update, or add to an existing `.drawio` file:**

1. **Read the existing file** — use `view_file` to load the current XML
2. **Find the highest existing ID** — scan all `id="N"` values, find `max(N)`. New elements start from `max + 1`
3. **Analyze existing layout** — note the current coordinate ranges, spacing patterns, and container boundaries
4. **Plan additions** — determine where new elements fit without disturbing existing positions:
   - Add to unused canvas space (right of or below existing elements)
   - If adding to a container, expand its width/height to accommodate new children
   - Maintain existing spacing standards
5. **Preserve existing content** — do NOT move or restyle existing elements unless the user explicitly asks
6. **Re-validate all edges** — after adding new elements, verify all `source`/`target` references still point to valid IDs

**Skip this step** if creating a new diagram from scratch.

### Step 1: Clarify Requirements

If the user's request is ambiguous, ask 1-3 focused questions:
- **Diagram type** — flowchart, ERD, UML, architecture, sequence, workflow?
- **Scope** — how many components? Which entities/services?
- **Output format** — `.drawio` only (default) or export to PNG/SVG/PDF?
- **Theme** — light (default) or dark mode?

Skip clarification if the request is already clear.

### Step 2: Plan the Layout

Before writing any XML:
1. **List all nodes** — identify every shape/entity
2. **List all connections** — identify every edge and its direction
3. **Choose layout direction** — TB for hierarchical, LR for sequential/workflow
4. **Group by tier/layer** — organize logically (e.g., frontend → backend → data)
5. **Calculate grid positions** — assign `(x, y)` coordinates using spacing standards and the layout calculation guide above
6. **Estimate canvas size** — set `pageWidth` and `pageHeight` to fit all elements with margin

### Step 3: Generate XML

Write the `.drawio` file following all mandatory rules:
1. Include the full `<mxfile>` wrapper structure
2. Start with `id="0"` and `id="1"` root cells
3. Add all vertices (shapes) with proper styles, positions, and dimensions
4. Add all edges (connectors) with proper `source`/`target` references
5. Apply the professional color palette based on element roles
6. Ensure consistent spacing and alignment

### Step 4: Self-Review Checklist

Before delivering, verify each of these:

| Check | What to Look For |
|-------|--------------------|
| ✅ Root cells | `id="0"` and `id="1"` present |
| ✅ Unique IDs | No duplicate `id` values |
| ✅ Connected edges | Every `source`/`target` references a valid cell ID |
| ✅ Edge form | ALL edges use expanded form with `<mxGeometry>` child — no self-closing edges |
| ✅ No overlaps | Shapes don't stack on each other; check bounding boxes `(x, y, x+w, y+h)` |
| ✅ Consistent spacing | Minimum 200px between shapes |
| ✅ Grid aligned | All coordinates are multiples of 10 |
| ✅ Readable labels | No truncated text, shapes sized to fit labels |
| ✅ Color consistency | Same type of element uses same color pair |
| ✅ Edge clarity | No edges crossing through unrelated shapes |
| ✅ Edge labels | All edges have `labelBackgroundColor=none;fontSize=12;fontColor=#000000;` |
| ✅ Valid XML | All special characters properly escaped, no `--` in comments |
| ✅ Container children | Children use coordinates relative to parent, not canvas |
| ✅ Container sizing | Containers are large enough to fit all children + 40px padding |

**Automated Validation:**
An automated validation script is provided to verify these rules before final delivery. Run it against any generated `.drawio` file:
```bash
/home/duc/projects/test/.agent/skills/drawio/scripts/validate-drawio.sh path/to/diagram.drawio
```

### Step 5: Export (Optional)


If the user needs PNG/SVG/PDF, the draw.io desktop CLI is required:

```bash
# Check if draw.io CLI is available
which draw.io || which drawio || echo 'Not found'

# Export to PNG
draw.io --export --format png --output output.png input.drawio

# Export to SVG
draw.io --export --format svg --output output.svg input.drawio

# Export to PDF
draw.io --export --format pdf --output output.pdf input.drawio

# Export with embedded diagram (editable in draw.io when reopened)
draw.io --export --format png --embed-diagram --output output.drawio.png input.drawio
```

**If CLI is not available:** Deliver the `.drawio` file and inform the user they can:
1. Open it at https://app.diagrams.net
2. Install draw.io desktop from https://github.com/jgraph/drawio-desktop/releases

---

## Diagram Type Reference

### Flowchart

```xml
<!-- Start node -->
<mxCell id="2" value="Start" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="340" y="40" width="100" height="60" as="geometry" />
</mxCell>

<!-- Process step -->
<mxCell id="3" value="Process Data" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="310" y="150" width="160" height="60" as="geometry" />
</mxCell>

<!-- Decision -->
<mxCell id="4" value="Valid?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="330" y="270" width="120" height="80" as="geometry" />
</mxCell>

<!-- End node -->
<mxCell id="5" value="End" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="340" y="420" width="100" height="60" as="geometry" />
</mxCell>

<!-- Edges -->
<mxCell id="6" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="7" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="3" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="8" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#82b366;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="4" target="5">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### ERD (Entity-Relationship Diagram)

Use `shape=table` with `childLayout=tableLayout` for proper table rendering:

```xml
<!-- Table: Users -->
<mxCell id="2" value="Users" style="shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=13;fontColor=#000000;align=center;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="150" as="geometry" />
</mxCell>

<!-- Row: id (PK) -->
<mxCell id="3" value="id  PK  INT" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;fontFamily=Inter;fontColor=#000000;fontStyle=1;" vertex="1" parent="2">
  <mxGeometry y="30" width="200" height="30" as="geometry" />
</mxCell>

<!-- Row: name -->
<mxCell id="4" value="name  VARCHAR(100)" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;fontFamily=Inter;fontColor=#000000;" vertex="1" parent="2">
  <mxGeometry y="60" width="200" height="30" as="geometry" />
</mxCell>

<!-- FK Relationship -->
<mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6c8ebf;strokeWidth=2;dashed=1;endArrow=ERmandOne;startArrow=ERmandOne;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="3" target="7">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

#### ERD Relationship Arrow Styles

| Relationship | startArrow | endArrow | Notation |
|-------------|-----------|----------|----------|
| 1:1 (mandatory) | `ERmandOne` | `ERmandOne` | ─\|\|──\|\|─ |
| **1:N (mandatory)** | `ERmandOne` | `ERoneToMany` | ─\|\|──\|<─ |
| 0..1:1 | `ERzeroToOne` | `ERmandOne` | ─○\|──\|\|─ |
| **0..1:N** | `ERzeroToOne` | `ERoneToMany` | ─○\|──\|<─ |
| **N:M** | `ERoneToMany` | `ERoneToMany` | ─\|<──\|<─ |
| 0..N:M | `ERzeroToMany` | `ERoneToMany` | ─○<──\|<─ |

### Architecture Diagram

Use LR layout with tier grouping:

```xml
<!-- Container: Frontend Tier -->
<mxCell id="2" value="Frontend" style="swimlane;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;fontFamily=Inter;fontSize=14;fontColor=#000000;fontStyle=1;rounded=1;arcSize=5;opacity=50;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="200" height="300" as="geometry" />
</mxCell>

<!-- Service inside container (coordinates relative to container!) -->
<mxCell id="3" value="Web App&#xa;(React)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;" vertex="1" parent="2">
  <mxGeometry x="20" y="50" width="160" height="60" as="geometry" />
</mxCell>

<!-- Database -->
<mxCell id="8" value="PostgreSQL" style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="700" y="150" width="120" height="80" as="geometry" />
</mxCell>

<!-- Queue -->
<mxCell id="9" value="Redis Queue" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="700" y="280" width="120" height="60" as="geometry" />
</mxCell>
```

### Sequence Diagram

Use `shape=umlLifeline` for participants. Messages are horizontal edges between lifelines.

```xml
<!-- Participant: Client -->
<mxCell id="2" value="Client"
  style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;newEdgeStyle={&quot;curved&quot;:0,&quot;rounded&quot;:0};fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=13;fontColor=#000000;fontStyle=1;size=40;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="40" width="100" height="400" as="geometry" />
</mxCell>

<!-- Participant: Server -->
<mxCell id="3" value="Server"
  style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;newEdgeStyle={&quot;curved&quot;:0,&quot;rounded&quot;:0};fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=13;fontColor=#000000;fontStyle=1;size=40;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="40" width="100" height="400" as="geometry" />
</mxCell>

<!-- Participant: Database -->
<mxCell id="4" value="Database"
  style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;newEdgeStyle={&quot;curved&quot;:0,&quot;rounded&quot;:0};fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=13;fontColor=#000000;fontStyle=1;size=40;"
  vertex="1" parent="1">
  <mxGeometry x="600" y="40" width="100" height="400" as="geometry" />
</mxCell>

<!-- Synchronous message: Client -> Server (solid arrow, filled head) -->
<mxCell id="10" value="login(user, pass)"
  style="html=1;verticalAlign=bottom;endArrow=block;endFill=1;curved=0;rounded=0;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- Synchronous message: Server -> Database -->
<mxCell id="11" value="SELECT user"
  style="html=1;verticalAlign=bottom;endArrow=block;endFill=1;curved=0;rounded=0;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="3" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- Return message: Database -> Server (dashed, open arrow) -->
<mxCell id="12" value="user record"
  style="html=1;verticalAlign=bottom;endArrow=open;endFill=0;dashed=1;curved=0;rounded=0;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="4" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- Return message: Server -> Client -->
<mxCell id="13" value="JWT token"
  style="html=1;verticalAlign=bottom;endArrow=open;endFill=0;dashed=1;curved=0;rounded=0;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="3" target="2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Sequence Diagram Rules:**
- `size=40` in lifeline style controls the participant header box height
- Lifeline height determines how many messages fit (increase for more messages)
- Messages appear in order from top to bottom along the lifeline
- Synchronous calls: `endArrow=block;endFill=1;` (solid filled arrow)
- Return/response: `endArrow=open;endFill=0;dashed=1;` (dashed open arrow)
- Async messages: `endArrow=block;endFill=1;dashed=1;` (dashed filled arrow)
- Self-call: set `source` and `target` to the same lifeline ID
- Space lifelines 200px apart horizontally

### UML Class Diagram

Use `swimlane` with 3 sections: class name (header), attributes, methods.

```xml
<!-- Class: User -->
<mxCell id="2" value="User"
  style="swimlane;fontStyle=1;align=center;startSize=26;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="200" height="130" as="geometry" />
</mxCell>

<!-- Attributes section -->
<mxCell id="3" value="- id: int&#xa;- name: String&#xa;- email: String"
  style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontFamily=Inter;fontSize=12;fontColor=#000000;"
  vertex="1" parent="2">
  <mxGeometry y="26" width="200" height="50" as="geometry" />
</mxCell>

<!-- Separator line -->
<mxCell id="4" value=""
  style="line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;strokeColor=inherit;"
  vertex="1" parent="2">
  <mxGeometry y="76" width="200" height="8" as="geometry" />
</mxCell>

<!-- Methods section -->
<mxCell id="5" value="+ getName(): String&#xa;+ setEmail(email): void"
  style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontFamily=Inter;fontSize=12;fontColor=#000000;"
  vertex="1" parent="2">
  <mxGeometry y="84" width="200" height="46" as="geometry" />
</mxCell>

<!-- Class: Order -->
<mxCell id="6" value="Order"
  style="swimlane;fontStyle=1;align=center;startSize=26;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="200" height="130" as="geometry" />
</mxCell>

<mxCell id="7" value="- orderId: int&#xa;- total: double&#xa;- status: String"
  style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontFamily=Inter;fontSize=12;fontColor=#000000;"
  vertex="1" parent="6">
  <mxGeometry y="26" width="200" height="50" as="geometry" />
</mxCell>

<mxCell id="8" value=""
  style="line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;strokeColor=inherit;"
  vertex="1" parent="6">
  <mxGeometry y="76" width="200" height="8" as="geometry" />
</mxCell>

<mxCell id="9" value="+ getTotal(): double&#xa;+ cancel(): void"
  style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;fontFamily=Inter;fontSize=12;fontColor=#000000;"
  vertex="1" parent="6">
  <mxGeometry y="84" width="200" height="46" as="geometry" />
</mxCell>

<!-- Association: User -> Order (1 to many) -->
<mxCell id="15" value="1..*"
  style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;strokeWidth=2;endArrow=diamondThin;endFill=0;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;"
  edge="1" parent="1" source="3" target="7">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**UML Class Diagram Rules:**
- Header `startSize=26` gives enough room for the class name
- Attributes section: use `- ` prefix for private, `+ ` for public, `# ` for protected
- Separator line: height is always `8`
- Methods section: include return types
- Calculate class height: `26 (header) + attributes_height + 8 (separator) + methods_height`
- Each line of text ≈ 16px height; add 4px padding

### Workflow / BPMN

Use horizontal swimlanes (`horizontal=0`) for cross-functional workflows:

```xml
<!-- SWIMLANE: Customer (horizontal=0 makes it a horizontal lane) -->
<mxCell id="2" value="Customer"
  style="swimlane;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;fontFamily=Inter;fontSize=14;fontColor=#000000;fontStyle=1;horizontal=0;rounded=1;arcSize=5;"
  vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="1200" height="180" as="geometry" />
</mxCell>

<!-- Start event (inside Customer swimlane — coords relative to swimlane) -->
<mxCell id="3" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="2">
  <mxGeometry x="60" y="65" width="40" height="40" as="geometry" />
</mxCell>

<!-- Task -->
<mxCell id="4" value="Submit&#xa;Request" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;" vertex="1" parent="2">
  <mxGeometry x="160" y="55" width="130" height="60" as="geometry" />
</mxCell>

<!-- SWIMLANE: System -->
<mxCell id="5" value="System"
  style="swimlane;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=14;fontColor=#000000;fontStyle=1;horizontal=0;rounded=1;arcSize=5;"
  vertex="1" parent="1">
  <mxGeometry x="40" y="250" width="1200" height="180" as="geometry" />
</mxCell>

<!-- Gateway (decision diamond) -->
<mxCell id="6" value="Approved?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;" vertex="1" parent="5">
  <mxGeometry x="370" y="50" width="100" height="70" as="geometry" />
</mxCell>

<!-- End event -->
<mxCell id="7" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Inter;fontSize=12;fontColor=#000000;strokeWidth=3;" vertex="1" parent="5">
  <mxGeometry x="1100" y="65" width="40" height="40" as="geometry" />
</mxCell>

<!-- Cross-swimlane edge (use parent="1" for cross-lane connections) -->
<mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6c8ebf;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="4" target="6">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Workflow/BPMN Rules:**
- Use `horizontal=0` on swimlanes for horizontal (left-to-right) workflow lanes
- Start events: small circle (40×40), Success color, no label or "Start"
- End events: small circle (40×40), Danger color, thicker stroke (`strokeWidth=3`), no label
- Tasks: rounded rectangles, Primary color
- Gateways: diamond/rhombus, Warning color
- Cross-swimlane edges: MUST use `parent="1"` (canvas level), not a swimlane parent
- Within-swimlane edges: can use the swimlane as parent
- Stack swimlanes vertically with 30px gap between them
- All swimlanes should have the same width

### Mind Map

Use radial layout with decreasing sizes by depth:

```xml
<!-- Central Topic (largest, center of canvas) -->
<mxCell id="2" value="Project&#xa;Strategy"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=14;fontColor=#000000;fontStyle=1;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="300" width="160" height="80" as="geometry" />
</mxCell>

<!-- Branch 1: Level 1 (medium, positioned around center) -->
<mxCell id="3" value="Marketing"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=13;fontColor=#000000;arcSize=20;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="140" y="120" width="140" height="50" as="geometry" />
</mxCell>

<!-- Branch 1: Level 2 (smallest) -->
<mxCell id="4" value="Social Media"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=20;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="50" width="120" height="40" as="geometry" />
</mxCell>

<mxCell id="5" value="SEO"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=20;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="110" width="120" height="40" as="geometry" />
</mxCell>

<!-- Branch 2: Level 1 -->
<mxCell id="6" value="Engineering"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontFamily=Inter;fontSize=13;fontColor=#000000;arcSize=20;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="680" y="120" width="140" height="50" as="geometry" />
</mxCell>

<!-- Edges: curved for organic feel -->
<mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;strokeColor=#82b366;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;strokeColor=#82b366;strokeWidth=1;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="3" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;strokeColor=#82b366;strokeWidth=1;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="3" target="5">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="23" style="edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;strokeColor=#9673a6;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="2" target="6">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Mind Map Rules:**
- Central topic: largest (160×80), use ellipse or rounded rect, bold font 14px
- Level 1 branches: medium (140×50), rounded rect, font 13px, `shadow=1`
- Level 2 branches: smallest (120×40), rounded rect, font 12px, no shadow
- Use `curved=1` on edges for an organic feel
- Edge `strokeWidth`: 2 for level 0→1 connections, 1 for level 1→2
- Color each branch family with the same palette role
- Radial positioning: spread branches around the center at ~45° intervals
- Use `exitX/exitY` and `entryX/entryY` to control edge connection points

### Network Topology

Use a grid layout with infrastructure icons:

```xml
<!-- Internet Cloud -->
<mxCell id="2" value="Internet"
  style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="380" y="40" width="160" height="80" as="geometry" />
</mxCell>

<!-- Firewall -->
<mxCell id="3" value="Firewall"
  style="shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="390" y="200" width="140" height="60" as="geometry" />
</mxCell>

<!-- Load Balancer -->
<mxCell id="4" value="Load Balancer"
  style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#d4e1f5;strokeColor=#3a7bbf;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="370" y="340" width="180" height="60" as="geometry" />
</mxCell>

<!-- Server 1 -->
<mxCell id="5" value="Web Server 1"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="140" y="490" width="160" height="60" as="geometry" />
</mxCell>

<!-- Server 2 -->
<mxCell id="6" value="Web Server 2"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="380" y="490" width="160" height="60" as="geometry" />
</mxCell>

<!-- Server 3 -->
<mxCell id="7" value="Web Server 3"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Inter;fontSize=12;fontColor=#000000;arcSize=10;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="620" y="490" width="160" height="60" as="geometry" />
</mxCell>

<!-- Database Primary -->
<mxCell id="8" value="DB Primary"
  style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="270" y="640" width="120" height="80" as="geometry" />
</mxCell>

<!-- Database Replica -->
<mxCell id="9" value="DB Replica"
  style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Inter;fontSize=12;fontColor=#000000;shadow=1;"
  vertex="1" parent="1">
  <mxGeometry x="530" y="640" width="120" height="80" as="geometry" />
</mxCell>

<!-- Edges -->
<mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#666666;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="3" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6c8ebf;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=0.25;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="4" target="5">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="23" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6c8ebf;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="4" target="6">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="24" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6c8ebf;strokeWidth=2;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;exitX=0.75;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="4" target="7">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<mxCell id="25" value="Replication" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#82b366;strokeWidth=2;dashed=1;fontFamily=Inter;fontSize=12;fontColor=#000000;labelBackgroundColor=none;" edge="1" parent="1" source="8" target="9">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Network Topology Rules:**
- Use distinct shapes per device type: cloud (internet), hexagon (firewall/security), parallelogram (load balancer), rectangle (servers), cylinder (databases)
- Grid layout: align devices in horizontal rows by tier (internet → security → routing → compute → data)
- Use `exitX` fractions to fan out connections from load balancers: `0.25`, `0.5`, `0.75` for 3 servers
- Dashed edges for replication/backup connections
- Label edges with protocol names (TCP, HTTP, etc.) when relevant

---

## Common Mistakes & Fixes

| Mistake | Fix |
|---------|-----|
| Missing `id="0"` and `id="1"` root cells | Always include both at the top of `<root>` |
| Shapes not connected | `source` and `target` on edge must match existing shape `id` values |
| Self-closing edge `<mxCell ... edge="1" />` | MUST use expanded form with `<mxGeometry relative="1" as="geometry" />` child |
| `--` inside XML comments | Illegal per XML spec — avoid XML comments entirely |
| Special characters in `value` | Use XML entities: `&amp;` `&lt;` `&gt;` `&quot;` |
| Literal `\n` in label text | Use `&#xa;` for line breaks in `value` attributes |
| Overlapping shapes | Scale spacing (200–350px); leave 100px routing corridors between container groups |
| **Edge labels with white background** | **ALWAYS add `labelBackgroundColor=none;fontSize=12;fontColor=#000000;` to every edge style — this is mandatory** |
| **Edges crossing through shapes** | **Route around shapes using waypoints or increase spacing. NEVER allow an edge to visually pass through an unrelated shape or bend inside containers over other blocks/labels. Use explicit waypoints in routing corridors.** |
| All shapes same color | Apply the color palette based on element role |
| **Tiny unreadable or colored text** | **All text must be at least `fontSize=12`. Default palette: `fontColor=#000000`. Dark palette: `fontColor=#e0e0e0`** |
| Inconsistent shape sizes | Same element type should have identical width/height |
| Containers too close together | Maintain 100px routing corridors between containers — edges need clear paths |
| **Container children at wrong position** | **Remember: child coordinates are RELATIVE to the parent container, not absolute canvas coordinates** |
| **Container too small for children** | **Calculate container size explicitly. Draw.io does NOT auto-resize containers** |

## Red Flags — STOP and Fix

- Shapes at negative coordinates or outside canvas (`x > pageWidth` or `y > pageHeight`)
- Edges with `source`/`target` pointing to non-existent IDs
- More than 2 edges visually overlapping on the same path
- Labels cut off by shape boundaries
- No color differentiation between different element types
- Missing `<mxGeometry>` on any edge element
- **Edge labels showing white/opaque background or not being size 12** — check if `labelBackgroundColor=none;fontSize=12;` is present
- **Any edge visually crossing through an unrelated shape** — reroute with waypoints or increase spacing
- **Containers touching or overlapping each other** — add 100px routing corridors between them
- **Vertically stacked error/failed path nodes inside a swimlane with < 60px spacing or < 220px swimlane height** — expand swimlane and increase vertical gap
- **Children appearing outside their container** — verify coordinates are relative to parent, not canvas
- **Duplicate IDs** — scan all id values; every one must be unique
- **Dark theme with black fontColor** — must use `fontColor=#e0e0e0` for dark palettes

---

## Edge Routing Best Practices

1. **Use `edgeStyle=orthogonalEdgeStyle`** for clean right-angle routing
2. **Add `rounded=1`** for smooth edge corners
3. **ALWAYS add `labelBackgroundColor=none;`** — edge labels must never have opaque backgrounds
4. **Distribute entry/exit points** — when multiple edges connect to one shape, spread them using the full style syntax:
   ```
   exitX=0.25;exitY=1;exitDx=0;exitDy=0;    (exit from bottom-left quarter)
   exitX=0.5;exitY=1;exitDx=0;exitDy=0;     (exit from bottom center)
   exitX=0.75;exitY=1;exitDx=0;exitDy=0;    (exit from bottom-right quarter)
   entryX=0.5;entryY=0;entryDx=0;entryDy=0; (enter at top center)
   ```
   Common positions: top center `(0.5, 0)`, bottom center `(0.5, 1)`, left center `(0, 0.5)`, right center `(1, 0.5)`
5. **Label placement** — use edge labels sparingly; place on the middle of the edge where no shapes exist
6. **Route edges around shapes, NEVER through them** — use explicit waypoints when auto-routing fails:
   ```xml
   <mxCell id="ID" style="edgeStyle=orthogonalEdgeStyle;..." edge="1" source="A" target="B">
     <mxGeometry relative="1" as="geometry">
       <Array as="points">
         <mxPoint x="400" y="200" />
         <mxPoint x="400" y="350" />
       </Array>
     </mxGeometry>
   </mxCell>
   ```
7. **For architecture diagrams**: route all edges through the routing corridors between containers — edges should exit one container and travel through clear space to reach the next container
8. **Prevent overlapping text/blocks**: For cross-container connections or connections between non-adjacent vertical blocks, default orthogonal routing often bends lines inside the containers, crossing other blocks and covering their text labels. You **MUST** add explicit waypoints (`<Array as="points"><mxPoint x="..." y="..." /></Array>`) to force the line to bend only in the corridors/margins outside the containers, never inside container spaces or over other shapes.
9. **Arrow styles** by relationship type:

| Relationship | Arrow Style |
|-------------|-------------|
| Standard flow | `endArrow=blockThin;endFill=1;` |
| Optional/async | `dashed=1;endArrow=blockThin;endFill=1;` |
| Inheritance (UML) | `endArrow=block;endFill=0;` |
| Composition (UML) | `endArrow=diamondThin;endFill=1;` |
| Aggregation (UML) | `endArrow=diamondThin;endFill=0;` |
| Dependency (UML) | `dashed=1;endArrow=open;endFill=0;` |
| Realization (UML) | `dashed=1;endArrow=block;endFill=0;` |
| ERD relationship | `endArrow=ERmandOne;startArrow=ERmandOne;` |
| Bidirectional | `endArrow=blockThin;startArrow=blockThin;endFill=1;startFill=1;` |
| Sequence sync call | `endArrow=block;endFill=1;` |
| Sequence return | `dashed=1;endArrow=open;endFill=0;` |
| Data flow | `endArrow=classicThin;endFill=1;` |

### Large Diagram Guidelines

For diagrams with **30+ elements**:
- Increase `pageWidth` and `pageHeight` proportionally
- Consider splitting into **multi-page diagrams** (separate `<diagram>` elements in `<mxfile>`)
- Omit `shadow=1` to reduce visual noise
- Use containers/swimlanes to group related elements and reduce visual complexity
- Increase spacing between groups to 300-400px
- Use dashed edges for secondary/optional connections to create visual hierarchy
