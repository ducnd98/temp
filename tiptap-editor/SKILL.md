---
name: tiptap-editor
description: Production-grade Tiptap rich-text editor and showcase viewer architecture for Next.js/React with 100% WYSIWYG parity, dedicated Code Block vs Inline Code controls, flawless drag-to-select text selection ergonomics, 120 FPS interactive media resizing, contextual table tooling, high-contrast tables, client-side pre-validation, two-stage media lifecycle management, and automated test suites. Triggers on: tiptap, editor, overview, code block, inline code, bôi đen, soạn thảo, markdown, rich text.
---

# Tiptap Pro Editor & Showcase Architecture

## 1. Architectural Mission & Non-Negotiables

The `tiptap-editor` kit provides an enterprise-ready, production-grade rich text system for Next.js (App Router, TypeScript, Tailwind CSS) consuming FastAPI backends. It balances fluid Notion-like editing ergonomics with the strict HTML standards of Google Docs and Atlassian Confluence.

### Core Non-Negotiables
1. **100% WYSIWYG Parity**: The authoring surface (`OverviewEditorView`) and public reader surface (`OverviewViewer`) share the identical Tiptap schema, extensions, and CSS rules (`.tiptap-pro-content`). The viewer runs `editable: false`.
2. **Zero-Div W3C Table Invariant**: An HTML `<table>` must **never** contain `<div>` tags. Wrapping table content in React `NodeViewContent` triggers browser foster parenting and corrupts table column handles. Tables must subclass `TableView` from `prosemirror-tables`.
3. **Native End-Caret Ergonomics**: Leaf blocks (Images, Videos) and complex blocks (Tables) provide a native-style blinking vertical caret (`1.5px x 20px`, 1s `step-end` blink) on click. Pressing `Enter` or typing printable characters immediately creates a paragraph below the block.
4. **Non-Zero-Sum Column Resizing**: Resizing internal table columns must never squash sibling columns into unreadable slivers. Configure `lastColumnResizable: false` and `table { width: auto; min-width: 100%; table-layout: fixed; }`.
5. **Universal Gutter Drag Handle**: Block drag-and-drop is handled exclusively by `<BlockDragHandle>` positioned in the left gutter (`left = blockRect.left - containerRect.left - 38px`), preserving a mandatory **10px breathing room** so text is never obscured. No redundant drag handles inside media popups.
6. **120 FPS Hardware Drag Resizing**: Media resizing operates directly on DOM style properties with transitions disabled during active drag, eliminating React re-render bottlenecks.
7. **Two-Stage Media Lifecycle**: Direct uploads stage in `/data/uploads_temp/` and commit to `/data/uploads/{skill_id}/` on save. Diff reconciliation deletes removed assets, and orphaned temp files are pruned after 6 hours.
8. **Text Selection Ergonomics & Gutter Isolation**: The left gutter block drag handle wrapper must use `pointer-events-none` (only the 6-dot grip button has `pointer-events-auto`) and freeze detection during `e.buttons > 0` so mouse drag-to-select text is never intercepted or disrupted. Any canvas `onClick` handler must strictly check `!editor.state.selection.empty` and `window.getSelection()` before placing cursor, preventing active selections from collapsing.
9. **Code Block vs Inline Code Distinction**: Editors must provide both `toggleCode()` (inline `<code>...</code>` in formatting dropdown) and a dedicated `toggleCodeBlock()` button on the primary toolbar (multiline `<pre><code>...</code></pre>`). In CSS, style `<pre>` with multiline padding (`0.875rem 1rem`) and reset nested `<pre> code` to transparent background without borders.

---

## 2. Directory Structure & Kit Components

```
frontend/src/
├── components/
│   ├── overview-viewer.tsx            # Public read-only showcase (editable: false)
│   └── admin/
│       ├── overview-editor-view.tsx    # Authoring canvas & toolbar orchestration
│       ├── block-drag-handle.tsx       # Universal 6-dot gutter drag handle
│       ├── upload-dropzone.tsx         # File drag-and-drop modal with pre-validation
│       └── edit-skill-dialog.tsx       # Entity lifecycle & dialog container
├── lib/
│   ├── tiptap-extensions.tsx          # Schema, CustomTableView, UnifiedBlockWrapper
│   ├── admin-api.ts                   # Backend upload & media commit clients
│   └── markdown.ts                    # Frontmatter-preserving markdown parser
└── test/
    ├── setup.ts                       # JSDOM Range rect polyfills
    ├── overview-editor-dialog.test.tsx # Authoring UI & table caret tests
    ├── overview-viewer.test.tsx       # Showcase viewer parity tests
    └── block-drag-handle.test.tsx     # Gutter handle drag-and-drop tests
```

---

## 3. Quick Reference & Core Patterns

### Unified Extensions Registry (`getSharedTiptapExtensions`)

```ts
export function getSharedTiptapExtensions(options: { editable: boolean }) {
  return [
    StarterKit.configure({
      paragraph: false,
      heading: false,
      trailingNode: false,
      dropcursor: { color: "#2563eb", width: 3 },
      link: {
        openOnClick: !options.editable,
        HTMLAttributes: {
          target: options.editable ? undefined : "_blank",
          rel: options.editable ? undefined : "noopener noreferrer",
          class: "text-blue-600 dark:text-blue-400 underline underline-offset-2 hover:text-blue-500 font-medium transition-colors",
        },
      },
    }),
    TrailingNode,
    CustomParagraph,
    CustomHeading.configure({ levels: [1, 2, 3, 4, 5] }),
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    TextAlign.configure({ types: ["heading", "paragraph", "tableCell", "tableHeader"] }),
    CustomTable.configure({
      resizable: options.editable,
      lastColumnResizable: false, // Critical: disables squashing sibling columns
      cellMinWidth: 80,
      View: CustomTableView,      // Strict W3C table with sibling end-caret
    }),
    TableRow,
    CustomTableHeader,
    CustomTableCell,
    CustomImage.configure({ inline: false, allowBase64: true }),
    CustomVideo,
    Youtube.configure({ inline: false, width: 800, height: 450 }),
    Markdown.configure({ html: true, transformPastedText: true, transformCopiedText: true }),
  ];
}
```

---

## 4. Architectural Deep Dives

Detailed implementation rules and code patterns are organized into targeted reference documents:

- **[Unified Block Wrapper & Native End-Caret Architecture](references/unified-block-caret.md)**: Details `<UnifiedBlockWrapper>`, the 1.5px vertical blinking cursor, position derivation, and keyboard event dispatch.
- **[Strict W3C Table Architecture & Non-Zero-Sum Resizing](references/w3c-table-resizing.md)**: Rules for `CustomTableView`, avoiding React `NodeViewContent` foster parenting, `lastColumnResizable: false`, and flexible column expansion.
- **[Universal Gutter Drag Handle & Block Reordering](references/gutter-drag-handle.md)**: Mathematical positioning geometry (`left = blockRect.left - containerRect.left - 38px`), 10px breathing room, and 44px hover bridge.
- **[Unified Paper Canvas & Automated Testing Discipline](references/paper-canvas-and-testing.md)**: Active canvas surface design, Exact-Y coordinate projection, JSDOM `Range.prototype.getClientRects` polyfill, and Vitest async stability rules.

---

## 5. Golden Rules for Developers

1. **NEVER use `NodeViewContent` inside `<table>`**: It violates W3C specs and breaks column resizing. Always subclass `TableView`.
2. **NEVER hardcode drag handle offsets to `left: -36px`**: Always derive `left` dynamically from `blockRect.left - containerRect.left - 38px`.
3. **NEVER add duplicate drag handles inside media popups**: Leaf block quick controls are reserved strictly for size percentages (`25%`, `50%`, `75%`, `100%`) and alignment.
4. **NEVER put mutating `fireEvent` inside `waitFor()`**: It causes an infinite 50ms retry loop in Vitest. Fire the action once, then `waitFor()` assertions.
5. **NEVER export static HTML (`output: "export"`) in Next.js**: SkillHub relies on dynamic routing (`/skills/[id]`) and dynamic REST API communication.
