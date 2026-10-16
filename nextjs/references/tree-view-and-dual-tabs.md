# Dual-Tab Parity & Authentic Monospace Unix Tree Architecture

This guide documents the architecture, UX patterns, and technical guidelines for building dual-tab showcases and pixel-perfect Unix file trees in Next.js App Router applications.

---

## 1. Dual-Tab Parity Architecture

When an entity detail page offers two views:
- **Tab 1 (Overview / Showcase)**: Rich rendered document (e.g. Tiptap) + sticky Metadata & Actions sidebar.
- **Tab 2 (Files / Inspector)**: Code / document content reader + sticky File Tree explorer.

### Grid Parity Rule (Zero Layout Shift)
To prevent Cumulative Layout Shift (CLS) and jarred column resizing when toggling tabs:
- **Never** switch from a 2:1 column ratio in Tab 1 to a 3:1 column ratio in Tab 2.
- **Always** match the exact layout grid classes across both tabs:
  ```tsx
  {/* Tab 1: Overview */}
  {activeTab === "overview" && (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 xl:gap-10 items-start">
      <div className="lg:col-span-2 space-y-6">
        <OverviewViewer content={skill.overview} />
      </div>
      <div className="lg:col-span-1 sticky top-24">
        <SkillMetadataCard skill={skill} />
      </div>
    </div>
  )}

  {/* Tab 2: Files */}
  {activeTab === "files" && (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 xl:gap-10 items-start">
      <div className="lg:col-span-2 space-y-6">
        <FileContentReader content={fileContent} />
      </div>
      <div className="lg:col-span-1 sticky top-24 space-y-4">
        <FileTree items={files} ... />
      </div>
    </div>
  )}
  ```
- **Result**: The right column retains 100% exact width and sticky viewport coordinates when switching between tabs.

### Tab DOM Retention (CSS Persistence vs Unmounting)
- **The Anti-Pattern (Conditional Unmounting)**:
  `{activeTab === "overview" && <OverviewViewer />}`
  `{activeTab === "files" && <SkillFilesViewer />}`
  Destroying and recreating the DOM on every tab switch drops page height to 0, triggers loading skeleton flickers, resets scroll positions, and re-triggers network fetches, creating the jarring perception that the "whole page is reloading".
- **The Pattern (CSS Persistence)**:
  Keep both tab panels mounted in memory and toggle visibility via CSS:
  ```tsx
  <div role="tabpanel" id="tabpanel-overview" className={activeTab === "overview" ? "block" : "hidden"}>
    <OverviewViewer ... />
  </div>
  <div role="tabpanel" id="tabpanel-files" className={activeTab === "files" ? "block" : "hidden"}>
    <SkillFilesViewer ... />
  </div>
  ```
- **Query Caching (`staleTime`)**:
  Pair with `staleTime: 5 * 60 * 1000` in TanStack Query.
- **Result**: Switching tabs takes **0ms (instantaneous)** with zero skeleton flashes, zero refetches, and zero layout shift.

---

## 2. Authentic Monospace Unix Tree Architecture (1D Flat Row Renderer)

### The Nested Margin Trap (Why lines disconnect)
When rendering tree structures, standard web implementations often wrap child nodes in nested `<div>` containers with `margin-left` or `padding-left`.
- **The Problem**: Wrapping children with margin/padding shifts their HTML origin to the right. When the child line also prints a branch prefix (`├── `), its vertical line characters (`│`) are displaced horizontally from the parent's vertical lines. This produces jagged, disconnected, and misaligned branches.
- **The Invariant**: All tree rows MUST share the exact same horizontal coordinate origin ($x = 0$) as flat siblings.

### The 1D Flat Row Pattern
Flatten the recursive tree into a single 1D flat array (`FlatTreeRow[]`) using mathematical 4-character prefix tokens:
```ts
export interface FlatTreeRow {
  id: string;
  path: string;
  name: string;
  isDir: boolean;
  prefix: string;
  sizeBytes?: number;
}
```

Prefix tokens:
- Not last child: `├── ` (4 characters: `\u251C\u2500\u2500 `)
- Last child: `└── ` (4 characters: `\u2514\u2500\u2500 `)
- Active vertical branch continuation: `│   ` (4 characters: `\u2502` + 3 spaces)
- Terminated branch whitespace: `    ` (4 spaces)

Every row is rendered directly as a flat sibling:
```tsx
<div className="flex flex-col">
  {flatRows.map((row) => (
    <div key={row.path} className="flex items-center h-6 leading-6 whitespace-pre font-mono text-xs select-none">
      <span className="text-muted-foreground/40 shrink-0 select-none font-mono">
        {row.prefix}
      </span>
      {/* Node label with icon */}
    </div>
  ))}
</div>
```
- Because every character at position $N$ occupies the exact same monospace column $N \times \text{charWidth}$, the vertical bar `│` connects with 100% mathematical precision across all lines.

### Horizontal Scroll Container
To prevent long filenames or deep hierarchies from wrapping onto new lines:
```tsx
<div className="overflow-x-auto pb-2 scrollbar-thin">
  <div className="min-w-full w-max inline-block pr-6">
    {/* Tree rows */}
  </div>
</div>
```

---

## 3. Zip Artifact Single-Root Unwrapping Pattern

Real-world packages (e.g. from GitHub tarballs or zip archives) frequently enclose all files within a single parent directory (e.g. `confluence-skill/...`).
- If unhandled, this produces a duplicate parent directory in the tree:
  ```
  confluence-skill/
  └── confluence-skill/  <-- Duplicate!
      ├── evals/
      └── SKILL.md
  ```
- **The Solution**: Detect when `rawTreeNodes.length === 1 && rawTreeNodes[0].isDir`.
  Unwrap the single folder, use its name as the root directory header (`confluence-skill/`), and display its children directly at level 0:
  ```ts
  const { treeNodes, displayRootName } = React.useMemo(() => {
    if (rawTreeNodes.length === 1 && rawTreeNodes[0].isDir) {
      const singleDir = rawTreeNodes[0];
      return {
        treeNodes: singleDir.children,
        displayRootName: singleDir.name,
      };
    }
    return {
      treeNodes: rawTreeNodes,
      displayRootName: defaultRootName,
    };
  }, [rawTreeNodes, defaultRootName]);
  ```

---

## 4. Visual Folder vs File Distinction Rules

1. **Folders**:
   - MUST display an explicit folder icon (`Folder` when collapsed, `FolderOpen` when expanded).
   - MUST append a trailing slash `/` (`scripts/`, `evals/`, `references/`).
   - Default state: Collapsed (empty `expandedFolders: Set<string>`). Click to toggle.
   - Empty folders: When expanded, render `└── (empty)` in subtle italic text to prevent broken dangling branch lines.
2. **Files**:
   - MUST display format-specific file icons (`.md` sky, `.py` emerald, `.json` amber, `.sh` violet, etc.).
   - MUST NOT append a trailing slash.
   - Active file: Styled with high-contrast highlight (`bg-violet-500/20 text-violet-400 font-bold border border-violet-500/30`).
   - Auto-expansion: Automatically expand all ancestor directories of `selectedPath` on mount so the active file is immediately visible to the user.
