# shadcn CLI Reference

Trimmed to the commands this project actually uses — full upstream
reference (registry authoring, monorepo scaffolding flags, Laravel/Astro
templates) is at `reference/shadcn-ui/ui/skills/shadcn/cli.md` if a task
ever needs it.

> Only use flags documented below — don't invent or guess flags.
> The CLI auto-detects the package manager from the lockfile.

## info — always run this first

```bash
npx shadcn@latest info
```

Reports `framework`, `isRSC`, `tailwindVersion`, `tailwindCssFile`,
`aliasPrefix`, `packageManager`, and (from `components.json`) `base`,
`style`, `iconLibrary`, `aliases`, `resolvedPaths`. Use these actual
values — never hardcode `@/components/ui` or assume `lucide-react`.

## add — install components

```bash
npx shadcn@latest add button dialog card       # multiple at once
npx shadcn@latest add button --dry-run          # preview files, write nothing
npx shadcn@latest add button --diff button.tsx  # diff a specific file
npx shadcn@latest add button --diff globals.css # diff the CSS changes too
npx shadcn@latest add @acme/some-block          # from a community registry
```

**Always use `--dry-run`/`--diff` to preview — never fetch raw files from
GitHub manually.** The CLI resolves paths, aliases, and CSS diffing
correctly; manual fetching doesn't.

Before adding, check what's already installed (`components/ui/` or the
`components` list from `info`) — don't re-add, don't hand-write what the
CLI would generate.

## search / view / docs

```bash
npx shadcn@latest search -q "sidebar"           # search all configured registries
npx shadcn@latest view @shadcn/button           # inspect a registry item before installing
npx shadcn@latest docs button dialog select     # print doc/example URLs — then fetch them
```

**Always run `docs` and fetch the URLs before using an unfamiliar
component** — this replaces guessing an API from general React
knowledge (which is exactly how `base`/Radix API mismatches happen, see
[base-vs-radix.md](base-vs-radix.md)).

## Updating a component from upstream (smart merge)

Never use `--overwrite` without explicit confirmation — a component may
have local edits worth preserving.

1. `npx shadcn@latest add <component> --dry-run` — see affected files.
2. `npx shadcn@latest add <component> --diff <file>` — per file, see
   upstream vs local diff.
3. No local changes → safe to overwrite that file. Local changes → read
   the file, apply the upstream change while preserving the local edit.
4. Only use `--overwrite` if the user explicitly says "just update
   everything."

## Third-party registry components — check imports after adding

Components from community registries (not `@shadcn`) may hardcode import
paths (`@/components/ui/...`) that don't match this project's actual
aliases, or import a different icon library than `lucide-react`. After
adding, check the non-`ui` files added and rewrite imports/icons to match
`npx shadcn@latest info`'s reported aliases and `iconLibrary`.

## Registry must be explicit

If the user asks to add a block/component without naming a registry
(`@shadcn`, `@tailark`, `owner/repo`, etc.), ask which one — never guess.
