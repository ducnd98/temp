# Strict W3C Table Architecture & Non-Zero-Sum Resizing

## Overview

Tables in rich-text editors are notoriously prone to two fatal engineering pitfalls:
1. **HTML Invariant Violation**: Developers try wrapping `<table>` with React `NodeViewWrapper`/`NodeViewContent`. The browser HTML parser rejects `<div>` children inside `<table>` or `<tbody>`, automatically ejecting them via **foster parenting**. This corrupts the DOM hierarchy, breaks `colgroup` column resizing handles, and renders synthetic wrapper boxes.
2. **Zero-Sum Column Squash**: When an editor enforces `table { width: 100% !important; }` and enables resizing of the outer right table border (`lastColumnResizable: true`), dragging one column separator steals width from sibling columns, squashing adjacent text into unreadable vertical slivers.

The `CustomTableView` and `CustomTable` extensions solve both issues with mathematical precision.

---

## 1. The Strict W3C Table Invariant (Zero-Div Invariant)

The HTML specification strictly dictates that a `<table>` element can **only** contain:
`<caption>`, `<colgroup>`, `<thead>`, `<tbody>`, `<tfoot>`, `<tr>`.
**Never `<div>` or arbitrary elements.**

### The Broken Approach (Do NOT use)
```tsx
// Anti-Pattern: Corrupts DOM through foster parenting!
export function TableComponent() {
  return (
    <NodeViewWrapper>
      <table>
        <NodeViewContent /> {/* Injects <div data-node-view-content-react> inside <table>! */}
      </table>
    </NodeViewWrapper>
  );
}
```

### The Production Pattern: Subclassing `TableView`

Subclass `TableView` directly from `prosemirror-tables`. The parent class manages pure DOM elements (`this.dom = div.tableWrapper`, `this.table = table`):

```ts
import { TableView } from "prosemirror-tables";
import { Selection } from "@tiptap/pm/state";

export class CustomTableView extends TableView {
  caret: HTMLElement;
  view: any;
  getPos: any;
  isCaretActive = false;

  constructor(node: any, cellMinWidth: number, view?: any, getPos?: any) {
    super(node, cellMinWidth);
    this.view = view;
    this.getPos = getPos;

    // 1. Create the Sibling End-Caret Element AFTER <table>, INSIDE .tableWrapper
    this.caret = document.createElement("div");
    this.caret.className =
      "table-end-caret relative inline-flex items-center ml-1 self-end mb-1 outline-none focus:outline-none cursor-text select-none shrink-0";
    this.caret.tabIndex = 0;
    this.caret.title = "Press Enter for new line";
    this.caret.setAttribute("aria-label", "Caret beside table");
    this.caret.style.display = "none";
    this.caret.innerHTML =
      '<span class="w-[1.5px] h-5 bg-foreground inline-block animate-cursor-blink"></span>';
    
    // Sibling append: outside <table>, preserving pure W3C table markup!
    this.dom.appendChild(this.caret);

    // 2. Click catcher on margin beside table activates caret
    this.dom.addEventListener("click", (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.closest(
          "td, th, button, input, textarea, form, a, [data-drag-handle], .floating-link-popover"
        )
      ) {
        this.deactivateCaret();
        return;
      }
      if (this.view && !this.view.editable) return;

      e.preventDefault();
      e.stopPropagation();
      this.activateCaret();
    });

    // 3. Keyboard handlers on end-caret
    this.caret.addEventListener("keydown", (e: KeyboardEvent) => {
      if (this.view && !this.view.editable) return;

      if (e.key === "Enter") {
        e.preventDefault();
        this.deactivateCaret();

        const pos = this.getTablePos();
        const afterPos = pos + this.node.nodeSize;
        const { state, dispatch } = this.view;
        const pNode = state.schema.nodes.paragraph.createAndFill();
        let tr = state.tr.insert(afterPos, pNode);
        const sel = Selection.near(tr.doc.resolve(afterPos + 1));
        tr = tr.setSelection(sel);
        dispatch(tr);
        this.view.focus();
      } else if (e.key === "Backspace" || e.key === "Delete") {
        e.preventDefault();
        this.deactivateCaret();

        const pos = this.getTablePos();
        const { state, dispatch } = this.view;
        const tr = state.tr.delete(pos, pos + this.node.nodeSize);
        dispatch(tr);
        this.view.focus();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        this.deactivateCaret();

        const pos = this.getTablePos();
        const afterPos = pos + this.node.nodeSize;
        if (afterPos < this.view.state.doc.content.size) {
          const { state, dispatch } = this.view;
          const sel = Selection.near(state.doc.resolve(afterPos + 1));
          dispatch(state.tr.setSelection(sel));
          this.view.focus();
        }
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        this.deactivateCaret();

        const pos = this.getTablePos();
        if (pos > 0) {
          const { state, dispatch } = this.view;
          const sel = Selection.near(state.doc.resolve(Math.max(0, pos - 1)));
          dispatch(state.tr.setSelection(sel));
          this.view.focus();
        }
      }
    });

    this.caret.addEventListener("blur", () => {
      this.deactivateCaret();
    });
  }

  // Dynamic document position resolution
  getTablePos(): number {
    if (typeof this.getPos === "function") return this.getPos();
    if (this.view && typeof (this.view as any).getPos === "function") return (this.view as any).getPos();
    try {
      const domPos = this.view.posAtDOM(this.dom, 0);
      const resolved = this.view.state.doc.resolve(
        Math.min(domPos, this.view.state.doc.content.size)
      );
      for (let d = resolved.depth; d > 0; d--) {
        if (resolved.node(d).type.name === "table") {
          return resolved.before(d);
        }
      }
      let found = -1;
      this.view.state.doc.descendants((node: any, pos: number) => {
        if (node === this.node) {
          found = pos;
          return false;
        }
      });
      if (found !== -1) return found;
    } catch {}
    return 0;
  }

  activateCaret() {
    this.isCaretActive = true;
    this.caret.style.display = "inline-flex";
    setTimeout(() => {
      this.caret.focus();
    }, 0);
  }

  deactivateCaret() {
    this.isCaretActive = false;
    this.caret.style.display = "none";
  }

  ignoreMutation(record: any) {
    if (
      this.caret &&
      (record.target === this.caret || this.caret.contains(record.target as any))
    ) {
      return true;
    }
    return super.ignoreMutation(record);
  }
}
```

---

## 2. Non-Zero-Sum Column Resizing Rules

### Rule A: Disable Resizing the Outer Right Table Border
In extension configuration, set:
```ts
CustomTable.configure({
  resizable: options.editable,
  lastColumnResizable: false, // Critical: dragging handles only separates internal columns
  cellMinWidth: 80,
  View: CustomTableView,
})
```

### Rule B: Flexible Layout CSS
In `globals.css`:
```css
/* Flexible container with horizontal scroll when columns exceed container width */
.ProseMirror .tableWrapper {
  max-width: 100%;
  overflow-x: auto;
  margin: 1.25rem 0;
  display: flex;
  align-items: flex-end;
}

/* Allow table to naturally expand without squashing sibling columns */
.ProseMirror table {
  border-collapse: collapse;
  table-layout: fixed;
  width: auto;
  min-width: 100%;
  margin: 0;
  overflow: hidden;
  flex-shrink: 0;
}
```

---

## 3. Keyboard Escape Hatches

Tables must never trap keyboard-only users. Configure keyboard shortcuts on `CustomTable`:
1. `Mod-Enter` (`Ctrl + Enter` / `Cmd + Enter`): Instantly inserts a paragraph immediately after the table and moves focus into it.
2. `ArrowDown` at the last row of the table: Gracefully exits the table into the following paragraph.
