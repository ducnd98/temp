# Unified Block Wrapper & Native End-Caret Architecture

## Overview

In rich text document editing (like Notion, Google Docs, Confluence), non-text leaf blocks (Images, Videos, Embeds) and complex container blocks (Tables) suffer from a classic contenteditable failure: **cursor trapping**. Users click or navigate to the end of a block and cannot easily place a caret beside or directly below the block to create a new paragraph.

The `UnifiedBlockWrapper` and `CustomTableView` provide a standardized, battle-tested solution: **The Native-Style Blinking End-Caret**.

---

## 1. Architectural Principles

1. **Visual Parity**: The end-caret renders as an exact OS-style vertical bar (`1.5px` width, `20px` height) with a stepped blink animation (`step-end` 1s cycle), indistinguishable from a native text cursor.
2. **Sibling Isolation**: The caret element is **never** placed inside HTML table tags or image tags. It lives as a sibling DOM element within the block's wrapper layout (`display: flex; align-items: flex-end;`).
3. **Dynamic Position Resolution**: Instead of relying on brittle closure positions (which become stale during document transactions), position is dynamically derived via `editor.view.posAtDOM(this.dom, 0)` or `state.doc.descendants()`.
4. **Keyboard Command Parity**:
   - `Enter`: Inserts a new empty paragraph immediately after the block and focuses the selection inside it.
   - Printable Key (e.g. typing `A`): Inserts a paragraph with that character and places the cursor right after it.
   - `Backspace` / `Delete`: Selects and deletes the block cleanly.
   - `ArrowDown` / `ArrowUp`: Navigates to the adjacent text block without breaking selection state.

---

## 2. Component Implementation: `UnifiedBlockWrapper`

Used for leaf nodeviews (`ResizableImageComponent`, `ResizableVideoComponent`):

```tsx
export interface UnifiedBlockWrapperProps {
  node: any;
  editor: any;
  getPos?: () => number;
  alignment?: "left" | "center" | "right";
  className?: string;
  caretAriaLabel?: string;
  children: React.ReactNode;
}

export function UnifiedBlockWrapper({
  node,
  editor,
  getPos,
  alignment = "left",
  className = "",
  caretAriaLabel = "Caret beside block",
  children,
}: UnifiedBlockWrapperProps) {
  const [isCaretActive, setIsCaretActive] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const caretInputRef = React.useRef<HTMLDivElement | null>(null);

  const isEditable = editor?.isEditable ?? true;

  let alignJustify = "justify-start";
  if (alignment === "center") alignJustify = "justify-center";
  if (alignment === "right") alignJustify = "justify-end";

  // Clicking empty space beside or at the end of the block activates the blinking caret
  const handleWrapperClick = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement;

    // Guard: ignore clicks on interactive buttons, inputs, links, or resize handles
    if (
      target.closest(
        "button, input, textarea, form, td, th, [data-drag-handle], a, .floating-link-popover"
      )
    ) {
      setIsCaretActive(false);
      return;
    }

    if (!editor || !editor.isEditable || typeof getPos !== "function") {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    setIsCaretActive(true);
    setTimeout(() => {
      caretInputRef.current?.focus();
    }, 0);
  };

  const handleCaretKeyDown = (e: React.KeyboardEvent) => {
    if (!editor || typeof getPos !== "function") return;

    if (e.key === "Enter") {
      e.preventDefault();
      setIsCaretActive(false);

      const pos = getPos();
      const afterPos = pos + node.nodeSize;

      editor
        .chain()
        .insertContentAt(afterPos, { type: "paragraph" })
        .setTextSelection(afterPos + 1)
        .focus()
        .run();
    } else if (e.key === "Backspace" || e.key === "Delete") {
      e.preventDefault();
      setIsCaretActive(false);
      const pos = getPos();
      editor.chain().setNodeSelection(pos).deleteSelection().focus().run();
    } else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      setIsCaretActive(false);

      const pos = getPos();
      const afterPos = pos + node.nodeSize;

      editor
        .chain()
        .insertContentAt(afterPos, {
          type: "paragraph",
          content: [{ type: "text", text: e.key }],
        })
        .setTextSelection(afterPos + 2)
        .focus()
        .run();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setIsCaretActive(false);
      const pos = getPos();
      const afterPos = pos + node.nodeSize;
      if (afterPos < editor.state.doc.content.size) {
        editor.chain().setTextSelection(afterPos + 1).focus().run();
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setIsCaretActive(false);
      const pos = getPos();
      if (pos > 0) {
        editor.chain().setTextSelection(Math.max(0, pos - 1)).focus().run();
      }
    }
  };

  return (
    <NodeViewWrapper
      ref={containerRef}
      onClick={handleWrapperClick}
      className={`unified-block-wrapper w-full my-5 flex items-end ${alignJustify} ${
        isEditable ? "cursor-text" : ""
      } ${className}`}
    >
      {children}

      {isEditable && isCaretActive && (
        <div
          ref={caretInputRef}
          tabIndex={0}
          onKeyDown={handleCaretKeyDown}
          onBlur={() => setIsCaretActive(false)}
          className="relative inline-flex items-center ml-1 self-end mb-1 outline-none focus:outline-none cursor-text select-none"
          title="Press Enter for new line"
          aria-label={caretAriaLabel}
        >
          <span className="w-[1.5px] h-5 bg-foreground inline-block animate-cursor-blink" />
        </div>
      )}
    </NodeViewWrapper>
  );
}
```

---

## 3. CSS Animation Token: Native Cursor Blink

In `globals.css`:

```css
@keyframes cursor-blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.animate-cursor-blink {
  animation: cursor-blink 1s step-end infinite;
}
```

Using `step-end` replicates the discrete, high-contrast on/off cadence of the Windows / macOS system text cursor rather than a floaty, distracting ease curve.
