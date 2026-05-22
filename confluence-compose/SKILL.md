# .cline/skills/confluence-compose/SKILL.md

---
name: confluence-compose
description: "Compose mode for Confluence documentation - explore, draft with templates, iterate, and publish in one flow. Uses draw.io diagrams (.drawio XML). Use when user wants to write and publish documentation to Confluence."
---

# Skill: Confluence Compose

Compose Confluence documentation — explore, draft, iterate, publish. Uses draw.io (.drawio XML) for all visuals.

---

## Stance

- **Iterative** — present draft, gather feedback, improve, repeat; don't publish until user confirms
- **Visual** — ALL diagrams as .drawio files, NEVER ASCII art; reference as `{{drawio:diagram-name}}` placeholders
- **Curious** — ask questions naturally, don't follow a script
- **Adaptive** — follow interesting threads, pivot when needed; use templates as starting points, customize freely
- **Grounded** — reference existing Confluence docs when relevant

---

## Templates

Read the appropriate template from `.cline/skills/confluence-compose/templates/<type>.md` before drafting.

| Template | File | Best For |
|----------|------|----------|
| API Guide | `api-guide.md` | API documentation, endpoint references |
| How-To | `how-to.md` | Step-by-step guides, tutorials |
| Meeting Notes | `meeting-notes.md` | Meeting records, decisions |
| Spec | `spec.md` | Technical specifications, architecture docs |
| Troubleshooting | `troubleshooting.md` | Problem resolution guides |
| Reference | `reference.md` | Lookup tables, catalogs, cheat sheets |

---

## draw.io Reference

### Pipeline

Every diagram: Identify visual → create `.drawio` file in `drafts/diagrams/` → reference as `{{drawio:diagram-name}}` in Markdown.

ASCII code blocks are only OK for: small inline sequences (e.g., `User → API → DB`), file trees, config snippets — never for architecture/flow/schema/state diagrams.

### XML Structure

The `<diagram>` content MUST be base64-encoded raw deflate compressed XML (NOT raw XML):

```xml
<!-- drafts/diagrams/<name>.drawio -->
<mxfile host="app.diagrams.net" agent="confluence-compose" version="26.0">
  <diagram name="<Diagram Title>" id="<unique-id>">
    <base64-encoded-deflated-mxGraphModel-XML>
  </diagram>
</mxfile>
```

**Compression pipeline (MANDATORY):**
1. Build `<mxGraphModel>...</mxGraphModel>` XML with all cells
2. Raw deflate compress (zlib wbits=-15, NO zlib header)
3. Base64-encode the compressed bytes
4. Place base64 string inside `<diagram>` tag

```python
import zlib, base64
compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
compressed = compressor.compress(mxgraphmodel_xml.encode('utf-8')) + compressor.flush()
encoded = base64.b64encode(compressed).decode('utf-8')
```

⚠️ **XML escaping in `value` attributes** — NEVER put unescaped HTML like `<br>` in value attrs. Use spaces or escape as `<br>`. Unescaped `<` causes "Not a diagram file" errors.

❌ `value="Artifact<br>Service<br>:8001"`
✅ `value="Artifact Service :8001"` or `value="Artifact<br>Service<br>:8001"`

### Color Palette

| Preset | Fill | Stroke | Use For |
|--------|------|--------|---------|
| gray | `#F5F5F5` | `#545454` | Default/standard nodes |
| blue | `#DAE8FC` | `#668ABD` | Services, API layer |
| green | `#D5E8D4` | `#75AB56` | Infrastructure, proxies |
| orange | `#FFE6CC` | `#D39000` | Important components |
| yellow | `#FFF2CC` | `#D1AE43` | Warnings, pending states |
| red | `#F8CECC` | `#B0413C` | Errors, rejected states |
| purple | `#E1D5E7` | `#8B639C` | Databases, storage, caches |
| cyan | `#D5F5F5` | `#4A9B9B` | Messaging, event buses |

Apply via `fillColor=<FILL>;strokeColor=<STROKE>;` in each cell's style string.

### Style Templates

Container (swimlane):
```
swimlane;startSize=30;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontStyle=1;fontSize=14;fontColor=#333333;rounded=1;arcSize=8;
```
Standard node: `rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#668ABD;fontColor=#333333;fontSize=12;`
Database node: `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#8B639C;fontColor=#333333;fontSize=12;`
Decision node: `rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D1AE43;fontColor=#333333;fontSize=12;`
State node: `ellipse;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#75AB56;fontColor=#333333;fontSize=12;`
Edge: `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#333333;`
Edge dashed: add `dashed=1;`
Edge with label: add `fontColor=#333333;fontSize=11;`

### Layout Rules

- Node: width=160, height=60 (tall=70 for multi-line)
- Gap: horizontal=80, vertical=100
- Container: padding=40, titleBar=30 (`startSize=30`)
- Grid: `x = col * (nodeWidth + hGap)`, `y = row * (nodeHeight + vGap)`
- Container sizing: `width = maxChildX + maxChildWidth + padding`, `height = maxChildY + maxChildHeight + padding + titleBar`
- IDs: `id="0"` and `id="1"` reserved (root cells); increment from `id="2"` for containers, then nodes, then edges

---

## Formatting Rules

- `#` (H1) for top-level sections → Confluence auto-numbers as 1, 2, 3...
- `##` (H2) for subsections → becomes 1.1, 1.2, 2.1...
- No emoji in headings, no manual numbering in headings (e.g., `## 1. Something`), no `---` between sections
- Blank line before and after Markdown tables
- In tree code blocks, use `│` (U+2502) not `|` (U+007C pipe) — pipe conflicts with Markdown tables

---

## Guardrails

- **Don't publish until user confirms** — iterate until satisfied
- **Don't use ASCII art for diagrams** — always .drawio → `{{drawio:...}}` placeholder
- **Do save draft** to `./drafts/` before publishing
- **Do create .drawio immediately** — don't defer when you identify a visual element
- **Do calculate layout** — every node MUST have explicit x, y, width, height; use `edgeStyle=orthogonalEdgeStyle`

---

## Confluence draw.io Macro

Used when publishing to insert diagrams into the page:

```xml
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="diagramName">diagram-name.drawio</ac:parameter>
  <ac:parameter ac:name="showTitle">false</ac:parameter>
</ac:structured-macro>
```

⚠️ `diagramName` MUST include `.drawio` extension — e.g., `high-level-architecture.drawio`, NOT `high-level-architecture`.
