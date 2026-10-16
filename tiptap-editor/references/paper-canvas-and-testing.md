# Unified Paper Canvas & Automated Testing Discipline

## Overview

A rich-text authoring experience succeeds or fails on the tactile feel of its "paper sheet" surface and the resilience of its automated test suite.

---

## 1. Unified Paper Canvas (Dead-Zone Elimination)

### The Anti-Pattern: Nested Floating Card
```tsx
// Anti-Pattern: On wide screens, clicking the outer card does nothing, confusing the user!
<div className="bg-card border rounded-2xl p-6 sm:p-10">
  <div className="max-w-4xl mx-auto min-h-[500px]">
    <EditorContent editor={editor} />
  </div>
</div>
```

### The Production Pattern: Full-Surface Active Paper
The outer container *is* the paper sheet. Every pixel inside the border has `cursor-text` and active click handlers:

```tsx
<div
  ref={editorWrapperRef}
  onClick={handleCanvasClick}
  className="relative p-6 sm:p-10 lg:p-12 w-full min-h-[500px] cursor-text"
>
  <BlockDragHandle editor={editor} containerRef={editorWrapperRef} />
  <EditorContent editor={editor} />
</div>
```

### Exact-Y Margin Projection
When a user clicks into the left or right padding margin, instead of simply jumping to the very end of the document, project the horizontal coordinates to find the nearest document line:

```ts
const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
  if (!editor || !editor.isEditable) return;

  const target = e.target as HTMLElement;
  // If user clicked directly on text, links, or controls, let native ProseMirror handle it
  if (
    target.closest(
      ".ProseMirror, button, [data-drag-handle], .table-end-caret, .unified-block-wrapper, a, form"
    )
  ) {
    return;
  }

  // Exact-Y projection: clamp horizontal axis to the ProseMirror content bounds
  const editorEl = editor.view.dom as HTMLElement;
  const editorRect = editorEl.getBoundingClientRect();
  const clampedX = Math.max(editorRect.left + 8, Math.min(editorRect.right - 8, e.clientX));

  const coordsPos = editor.view.posAtCoords({ left: clampedX, top: e.clientY });
  if (coordsPos && coordsPos.pos != null) {
    editor.chain().setTextSelection(coordsPos.pos).focus().run();
  } else {
    editor.chain().focus("end").run();
  }
};
```

---

## 2. Stacking Context & Z-Index Hierarchy

When an authoring view has a sticky/docked formatting toolbar and the application has a persistent top bar (containing the user profile avatar and dropdown menu), improper z-indexing causes the toolbar to slice across the avatar's dropdown menu.

### Canonical Stacking Hierarchy
| Level | Component | Tailwind Classes | Description |
|:---|:---|:---|:---|
| **Level 1** | Paper Surface | `z-0` / `z-10` | ProseMirror editing text area |
| **Level 2** | Editor Docked Toolbar | `sticky top-16 z-20` | Stays glued at 64px offset on scroll |
| **Level 3** | App Sidebar | `sticky top-0 z-30` | Left navigation panel |
| **Level 4** | App Header / Navbar | `sticky top-0 z-40` | Top bar hosting UserMenu avatar & theme toggle |
| **Level 5** | Fullscreen Modals & Toasts | `fixed inset-0 z-50` | Dialogs, confirmation alerts, toast feedback |

By setting the Header to `z-40` and the Editor Toolbar to `z-20` (with `top-16` = 64px), content and toolbars slide underneath the header on scroll, and dropdown menus popping out of the header naturally float above all workspace elements.

---

## 3. Automated Testing Suite & JSDOM Polyfills

### Crucial JSDOM Polyfill (`setup.ts`)
ProseMirror internally calls `Range.prototype.getClientRects()` and `getBoundingClientRect()` to calculate cursor coordinates during keyboard navigation (`Enter`, `ArrowDown`).
In standard JSDOM, `Range.prototype.getClientRects` returns `undefined` for text nodes, crashing tests with:
`TypeError: target.getClientRects is not a function` or `singleRect fails`.

Add this to `src/test/setup.ts`:

```ts
if (typeof window !== "undefined") {
  if (!Range.prototype.getClientRects) {
    Range.prototype.getClientRects = function () {
      return [] as any;
    };
  }
  if (!Range.prototype.getBoundingClientRect) {
    Range.prototype.getBoundingClientRect = function () {
      return {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        top: 0,
        right: 0,
        bottom: 0,
        left: 0,
        toJSON: () => {},
      };
    };
  }
}
```

### Critical Testing Library Invariant: No Mutating Actions Inside `waitFor`

```ts
// FATAL ANTI-PATTERN: Mutating inside waitFor causes an infinite 50ms retry loop on failure!
await waitFor(() => {
  fireEvent.click(caret); // NEVER DO THIS INSIDE WAITFOR!
  expect(editor.getText()).toContain("New line");
});

// CORRECT PATTERN: Perform action ONCE, wait strictly for ASSERTION:
fireEvent.click(caret);
fireEvent.keyDown(caret, { key: "Enter" });

await waitFor(() => {
  expect(editor.getText()).toContain("New line");
});
```

### Strict W3C Invariant Regression Test
Always assert that the rendered table contains zero `<div>` tags:
```ts
it("maintains strict W3C table structure with zero div elements inside table", () => {
  const table = container.querySelector("table");
  expect(table).not.toBeNull();
  expect(table?.querySelectorAll("div").length).toBe(0);
});
```
