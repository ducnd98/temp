# Universal Gutter Drag Handle & Block Reordering

## Overview

In block-based modern editors (Notion, Gutenberg), users expect an intuitive grip button (typically a 6-dot vertical grip `GripVertical`) to appear beside the active block when hovered.

Two major bugs frequently plague custom drag-handle implementations:
1. **Container Padding Drift**: Hardcoding `left: -36px` relative to a container with responsive padding (`p-6 sm:p-10 lg:p-12`) pushes the drag handle dozens of pixels away from the block (e.g. 84px gap).
2. **Text Overlap & Obscurity**: Positioning the handle too close to the text edge (e.g. touching `0px` from content) covers the first letter of titles and paragraphs.
3. **Handle Duplication**: Putting a drag handle both in the gutter and inside floating quick-action popups confuses the user and creates competing drag targets.

---

## 1. Mathematical Geometry & The 10px Breathing Room

To position the handle reliably across all viewports and padding configurations:

```ts
const blockRect = blockEl.getBoundingClientRect();
const containerRect = container.getBoundingClientRect();

const top = blockRect.top - containerRect.top + 2;
// Position 38px to the left of the block content
const left = blockRect.left - containerRect.left - 38;
```

### Why `-38px`?
- Handle Button Width: `24px` (`w-6` in Tailwind).
- Button margin-left: `4px` (`ml-1`).
- Button effective right edge: `-38px + 4px + 24px = -10px`.
- **Result**: Exactly **10px of clean breathing space** between the right edge of the button and the first glyph of text, preventing any overlap on headings, paragraphs, lists, or tables.

### The 44px Zero-Gap Hover Bridge
A hover-activated handle disappears if the mouse leaves the block before entering the handle.
The wrapper element spans `width: 44px` from `-38px` to `+6px` (slightly overlapping the block). When the user glides their cursor from the text into the left gutter, the pointer remains inside the wrapper, preventing flicker:

```tsx
<div
  style={{
    position: "absolute",
    top: `${targetBlock.top}px`,
    left: `${targetBlock.left}px`,
    width: "44px", // Extends from 38px left of block to 6px inside the block
    height: `${Math.max(28, Math.min(48, targetBlock.height))}px`,
    zIndex: 35,
  }}
  className="block-drag-handle-wrapper flex items-start justify-start pointer-events-auto"
>
  <div
    draggable="true"
    onDragStart={handleDragStart}
    onDragEnd={handleDragEnd}
    onClick={handleClick}
    className="block-drag-handle-button flex items-center justify-center w-6 h-6 rounded-md bg-muted/90 hover:bg-muted text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing border border-border/60 shadow-xs transition-colors select-none ml-1 mt-0.5"
    title="Hold and drag to move, click to select block"
    aria-label="Hold and drag to move block"
  >
    <GripVertical className="h-3.5 w-3.5" />
  </div>
</div>
```

---

## 2. Top-Level Block Detection Algorithm

To move entire cohesive blocks (paragraphs, tables, media) rather than inline spans, ascend the DOM tree to the direct child of `.ProseMirror`:

```ts
if (prosemirror.contains(target)) {
  let blockEl: HTMLElement | null = target;
  while (blockEl && blockEl.parentElement !== prosemirror) {
    blockEl = blockEl.parentElement;
  }

  if (!blockEl || blockEl === prosemirror) return;

  try {
    const domPos = editor.view.posAtDOM(blockEl, 0);
    const $pos = editor.state.doc.resolve(Math.min(domPos, editor.state.doc.content.size));
    const blockPos = $pos.depth > 0 ? $pos.before(1) : 0;

    const blockRect = blockEl.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    setTargetBlock({
      pos: blockPos,
      dom: blockEl,
      top: blockRect.top - containerRect.top + 2,
      left: blockRect.left - containerRect.left - 38,
      height: blockRect.height,
    });
  } catch {}
}
```

---

## 3. Native ProseMirror Drag Transfer Protocol

When initiating drag from the custom button, bind the drag slice directly to ProseMirror's internal view dragging state:

```ts
const handleDragStart = (e: React.DragEvent) => {
  setIsDragging(true);

  try {
    const nodeSelection = NodeSelection.create(editor.state.doc, targetBlock.pos);
    editor.view.dispatch(editor.state.tr.setSelection(nodeSelection));
  } catch {}

  const view = editor.view as any;
  const selection = editor.state.selection;
  const slice = selection.content();
  view.dragging = { slice, move: true };

  e.dataTransfer.effectAllowed = "move";
  e.dataTransfer.setData("text/plain", "");
  e.dataTransfer.setData("text/html", targetBlock.dom.outerHTML || "<p>block</p>");

  if (targetBlock.dom) {
    e.dataTransfer.setDragImage(targetBlock.dom, 20, 20);
  }
};
```

---

## 4. Single Source of Truth: No Redundant Popup Handles

Leaf nodeviews (Images, Videos) must **not** include an auxiliary grip handle inside their floating quick-action popups (`25%`, `50%`, `75%`, `100%`). The universal gutter `<BlockDragHandle>` manages 100% of block reordering uniformly.
