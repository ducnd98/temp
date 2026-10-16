# Project Template

The canonical starting point for `frontend/`, combining shadcn/ui's
official Next.js template (versions, theming, linting) with this
project's own decisions from the `nextjs` skill (the `src/` layout,
feature folders, the typed API client). Read this once when scaffolding
`frontend/` for the first time — the `nextjs` skill's
`project-structure.md` covers everything that happens *inside* `app/`
and `features/` after this exists.

> Package versions below reflect what's current as of this writing.
> Before scaffolding, check the actually-installed versions
> (`npx create-next-app@latest --help`, `npm view next version`) —
> Next.js has shipped real breaking changes between majors recently
> (Promise-based `params`, the explicit `"use cache"` model — see the
> `nextjs` skill's `data-fetching.md`), so don't assume an older
> version's patterns still apply without checking.

## Why `src/`

Unlike shadcn's own template (which puts `app/`/`components/`/`lib/` at
the project root), this project uses a `src/` directory. In a monorepo
where `frontend/` sits beside `backend/`, keeping config files
(`package.json`, `next.config.ts`, `.env.local`) visually separated from
application source is worth the one extra path segment. The shadcn CLI
detects this automatically (`isSrcDir` in `npx shadcn@latest info`) and
resolves import aliases accordingly — nothing below needs adjusting for
this choice except the path shown in each file.

## package.json

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "format": "prettier --write \"**/*.{ts,tsx}\"",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/lib/api/schema.d.ts"
  },
  "dependencies": {
    "next": "^16.2.0",
    "next-themes": "^0.4.6",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@tanstack/react-query": "^5.62.0",
    "openapi-fetch": "^0.13.0",
    "react-hook-form": "^7.54.0",
    "@hookform/resolvers": "^3.9.0",
    "zod": "^3.24.0",
    "lucide-react": "^0.469.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@types/node": "^22",
    "@types/react": "^19.2.0",
    "@types/react-dom": "^19.2.0",
    "eslint": "^9",
    "eslint-config-next": "^16.2.0",
    "jsdom": "^25.0.0",
    "msw": "^2.7.0",
    "openapi-typescript": "^7.5.0",
    "prettier": "^3.8.0",
    "prettier-plugin-tailwindcss": "^0.8.0",
    "tailwindcss": "^4",
    "tw-animate-css": "^1.3.0",
    "typescript": "^5.7.0",
    "vitest": "^2.1.0"
  }
}
```

The `nextjs`/`fastapi` skills' data-fetching and form conventions
(TanStack Query, openapi-fetch, react-hook-form + zod) are included from
the start — they aren't optional add-ons for this project. Same for the
test stack (vitest, Testing Library, MSW): the `tdd` skill makes
test-first non-negotiable here, so the scaffold ships with `npm test`
working from day one (see `tdd`'s `references/frontend-nextjs.md` for
the vitest config and seam conventions).

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
};

export default nextConfig;
```

`optimizePackageImports` for `lucide-react` from day one — see the
`nextjs` skill's `references/performance.md` for why.

## src/app/globals.css — Tailwind v4, CSS-first

No `tailwind.config.js` — Tailwind v4 configures via CSS. Variables
follow the `name`/`name-foreground` convention from
[customization.md](customization.md):

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
}

@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

These starting values are shadcn's neutral default (`oklch(... 0 0)` —
zero chroma, pure gray) — the actual palette is a `frontend-design`
decision (see that skill; also `npx shadcn@latest apply <preset>` to
adopt a named preset wholesale instead of hand-tuning every variable).

## src/app/layout.tsx

```tsx
import type { ReactNode } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

const fontSans = Geist({ subsets: ["latin"], variable: "--font-sans" });
const fontMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" });

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontSans.variable} ${fontMono.variable} font-sans antialiased`}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

`suppressHydrationWarning` on `<html>` is required with `next-themes` —
the server can't know the client's resolved theme before hydration.
This is the one sanctioned mismatch: don't add
`suppressHydrationWarning` anywhere else, it silences a real class of
bugs (server/client rendering different content).

## src/components/theme-provider.tsx

```tsx
"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem {...props}>
      {children}
    </NextThemesProvider>
  );
}
```

`QueryClientProvider` (from the `nextjs` skill's data-fetching setup)
wraps `children` here too, inside or alongside `ThemeProvider` — order
between the two doesn't matter since they don't depend on each other.

## eslint.config.mjs — flat config (ESLint 9)

```javascript
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);
```

## .gitignore

```
node_modules/
.next/
out/
build/
*.tsbuildinfo
next-env.d.ts
.env.local
.env*.local
```

`package-lock.json` is **not** in this list — commit it, the same way
the `fastapi` skill commits `uv.lock`. A floating dependency tree
resolves differently between your machine, CI, and production; the
lockfile is what makes `npm install` reproducible.

## .prettierrc

```json
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "es5",
  "printWidth": 80,
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "src/app/globals.css",
  "tailwindFunctions": ["cn", "cva"]
}
```

`prettier-plugin-tailwindcss` sorts Tailwind classes into a canonical
order automatically — don't hand-order utility classes, let the
formatter do it. `tailwindFunctions` also sorts classes passed through
`cn()`/`cva()`, not just literal `className` strings.

## components.json

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "radix-nova",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "hooks": "@/hooks",
    "lib": "@/lib",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  }
}
```

`style` is `"radix-<preset-name>"` — the preset name (`nova` here) is a
placeholder; the actual choice is `frontend-design`'s call, applied via
`npx shadcn@latest init --preset <name>` or `apply`. The `base=radix`
half of that value is this project's fixed decision, not up for
per-task revisiting.
