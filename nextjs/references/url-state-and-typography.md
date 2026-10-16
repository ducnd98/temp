# URL State Synchronization & Typography Clamping

## 1. Rule 1: Never Call Router Navigation Inside `setState` Updaters

### The Hazard: React Bad setState in Render
When synchronizing component state with Next.js App Router query parameters, developers often try to compute the next state inside an updater function and trigger routing immediately:

**FATAL ANTI-PATTERN:**
```tsx
// Crashes React with:
// "Cannot update a component ('Router') while rendering a different component ('CatalogContent')"
const handleToggleTag = (tagName: string) => {
  setSelectedTags((prev) => {
    const next = prev.includes(tagName) ? prev.filter((t) => t !== tagName) : [...prev, tagName];
    const params = new URLSearchParams(searchParams.toString());
    params.set("tag", next[0]);

    // FATAL: Mutates Router context inside React's render phase!
    router.replace(`/?${params.toString()}`, { scroll: false });
    return next;
  });
};
```

### The Correct Pattern: Pure Event Handler Scope
State updater functions passed to `setState((prev) => ...)` must remain **pure functions with zero side-effects**. Execute routing in the event handler scope:

**CORRECT:**
```tsx
const handleToggleTag = (tagName: string) => {
  const next = selectedTags.includes(tagName)
    ? selectedTags.filter((t) => t !== tagName)
    : [...selectedTags, tagName];

  setSelectedTags(next);

  const params = new URLSearchParams(searchParams.toString());
  if (next.length === 1) {
    params.set("tag", next[0]);
  } else {
    params.delete("tag");
  }
  params.delete("page");
  router.replace(`/?${params.toString()}`, { scroll: false });
};
```

---

## 2. Rule 2: Decouple Grand Total from Filtered Query Results

### The Flaw
In marketplace/catalog sidebars, an "All Categories" or "All Skills" option displays a badge indicating the total number of items available.
If that badge reads from the currently active query response (`skillsData?.total`), selecting a category (e.g. "DevOps") causes `skillsData.total` to drop from 25 to 5. Consequently, the "All Categories" count badge incorrectly collapses to 5 instead of representing the entire system catalog.

### The Correct Pattern: Independent Grand Total Query
Decouple the global count from the active filtered dataset:

```tsx
// Query 1: Filtered catalog items (depends on filters, search, page)
const { data: skillsData } = useQuery({
  queryKey: ["skills", page, debouncedSearch, selectedCategory, selectedTags, sortBy],
  queryFn: () => fetchSkills({ page, category: selectedCategory, tags: selectedTags, search: debouncedSearch }),
});

// Query 2: Persistent overall count across the whole registry
const { data: allSkillsMeta } = useQuery({
  queryKey: ["skills-grand-total"],
  queryFn: () => fetchSkills({ page: 1, page_size: 1 }),
  staleTime: 60 * 1000,
});

const grandTotalSkills = allSkillsMeta?.total ?? (skillsData?.total || 0);
const filteredSkillsCount = skillsData?.total || 0;

return (
  <>
    {/* Sidebar 'All Categories' always shows grand total */}
    <CatalogSidebar totalSkillsCount={grandTotalSkills} ... />

    {/* Dynamic toolbar displays count of current filtered view */}
    <CatalogToolbar total={filteredSkillsCount} ... />
  </>
);
```

---

## 3. Rule 3: Pure CSS Line-Clamping & Zero DOM `textContent` Mutation

### The Hazard: Wiping Out React Fiber Children
Attempting to dynamically calculate word boundaries by mutating `ref.current.textContent = ""` inside a `useEffect` or `ResizeObserver` wipes out React's internal virtual DOM fiber nodes. Because React doesn't know the DOM was cleared, subsequent re-renders fail to mount text nodes, resulting in **blank or disappearing descriptions** for users.

### The Solution: Native CSS `line-clamp`
Let the browser's C++ rendering engine manage truncation:

```tsx
{/* 3 lines clamp with native ellipsis */}
{skill.description && (
  <p className="text-base text-muted-foreground leading-relaxed line-clamp-3 max-w-3xl">
    {skill.description}
  </p>
)}
```

**Key Benefits:**
1. **Zero DOM Mutation**: React virtual DOM stays 100% stable; text can never disappear.
2. **Native Precision**: The browser appends the ellipsis `...` only when text actually overflows line 3. Texts spanning 1 or 2 lines render naturally without trailing dots.
3. **Zero Layout Shift / Overlap**: Eliminates artificial `absolute` positioning, gradient overlays, and button clashing.
