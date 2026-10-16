# Data Fetching, Mutations, and Forms

> **Check the installed Next.js version before assuming API shapes.**
> Next.js 16 made `params`/`searchParams` Promises and replaced implicit
> cross-request caching with an explicit `"use cache"` model — both
> covered below. If the project's Next.js version is newer still, read
> `node_modules/next/dist/docs/` or the official upgrade guide before
> writing code; don't assume training-data patterns still apply.

## Route params and searchParams are Promises (Next.js 16+)

`params` and `searchParams` in pages, layouts, and metadata functions are
`Promise`s, not plain objects — await them before use:

```tsx
export default async function WidgetPage({
  params,
}: {
  params: Promise<{ widgetId: string }>;
}) {
  const { widgetId } = await params;
  const { data } = await serverApi.GET("/api/v1/widgets/{widget_id}", {
    params: { path: { widget_id: widgetId } },
  });
  // ...
}
```

## Caching is explicit, not implicit (Next.js 16+)

Next.js 16 removed the old implicit, cross-request Data Cache. Every
request is dynamic (re-fetches fresh data) by default — nothing persists
across requests or builds unless a function opts in with `"use cache"`.
This is a deliberate, welcome change (the old implicit caching was a
common source of "why is this stale" bugs), but it means:

- **Don't assume a Server Component fetch is cached across users/requests**
  — it isn't, unless the function is explicitly marked `"use cache"`.
- Reach for `"use cache"` only for data that's genuinely safe to share
  across requests (rarely-changing reference data), not per-user
  dashboard data — caching per-user API responses across requests would
  leak data between users.
- This is separate from the **within-request** fetch deduplication
  described below (calling the same endpoint twice in one render still
  only hits the network once) — that part is unaffected.

## The typed client

One generated schema (`lib/api/schema.d.ts`, see
[project-structure.md](project-structure.md)), two client instances —
one for the server, one for the browser — because they use different
base URLs and the server client can attach server-only headers.

```typescript
// lib/api/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./schema.d.ts";

export const serverApi = createClient<paths>({
  baseUrl: process.env.API_URL,
});

export const browserApi = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL,
});
```

Every call is typed end-to-end from the OpenAPI schema — the path, the
request body, and the response shape all typecheck, including error
responses:

```typescript
const { data, error } = await serverApi.GET("/api/v1/widgets/{widget_id}", {
  params: { path: { widget_id } },
});
if (error) { /* error is typed from the backend's error schema */ }
```

## Server Components: the waterfall is the mistake to avoid

A waterfall — one `await` after another for independent data — is the
single biggest performance killer in Server Components, because each
sequential await adds a full network round trip. React Server Components
execute sequentially **within a tree**, so the fix is usually restructuring
which component fetches what, not just wrapping calls in `Promise.all`.

**Wrong — Sidebar waits for Page's fetch to finish first:**

```tsx
export default async function Page() {
  const header = await serverApi.GET("/api/v1/dashboards/summary");
  return (
    <div>
      <Header data={header.data} />
      <Sidebar /> {/* only starts fetching after header resolves */}
    </div>
  );
}
```

**Right — both fetch simultaneously, each component owns its own fetch:**

```tsx
async function Header() {
  const { data } = await serverApi.GET("/api/v1/dashboards/summary");
  return <HeaderView data={data} />;
}

async function Sidebar() {
  const { data } = await serverApi.GET("/api/v1/widgets");
  return <SidebarNav items={data.items} />;
}

export default function Page() {
  return (
    <div>
      <Header />
      <Sidebar />
    </div>
  );
}
```

When you do have several *known* independent calls in one function,
`Promise.all` is the direct fix:

```typescript
const [widgets, dashboards] = await Promise.all([
  serverApi.GET("/api/v1/widgets"),
  serverApi.GET("/api/v1/dashboards"),
]);
```

And when fetching nested data per item, chain each item's dependent fetch
inside its own promise — don't resolve a whole batch before starting the
next round, or one slow item blocks everyone:

```typescript
// One slow widget blocks every dashboard's data from starting
const widgets = await Promise.all(ids.map((id) => getWidget(id)));
const dashboards = await Promise.all(widgets.map((w) => getDashboard(w.dashboardId)));

// Each item's chain is independent — a slow one only blocks itself
const results = await Promise.all(
  ids.map((id) => getWidget(id).then((w) => getDashboard(w.dashboardId)))
);
```

## Suspense: show the shell before the data is ready

Don't `await` inside the page function if only one section needs the
data — the whole page waits otherwise. Move the `await` into a child
component and wrap it in `Suspense` so the rest of the layout renders
immediately.

```tsx
export default function Page() {
  return (
    <div>
      <Sidebar />
      <Suspense fallback={<WidgetListSkeleton />}>
        <WidgetList />
      </Suspense>
    </div>
  );
}

async function WidgetList() {
  const { data } = await serverApi.GET("/api/v1/widgets");
  return <ul>{data.items.map((w) => <WidgetCard key={w.id} widget={w} />)}</ul>;
}
```

Route-segment `loading.tsx` is the same idea at the page level — Next.js
wraps the whole segment in Suspense automatically with that file as the
fallback. Use a component-level `<Suspense>` when only *part* of a page
should stream; use `loading.tsx` when the whole route should.

Skip Suspense streaming for data the layout needs to decide positioning,
anything SEO-critical above the fold, or small/fast queries where the
streaming machinery costs more than it saves.

## Client Components: TanStack Query for reads and mutations

Any data that's interactive, polled, or mutated goes through TanStack
Query rather than `useEffect` + `fetch` — manual client-side fetching
re-fetches on every mount with no caching or deduplication, and every
sibling instance fires its own redundant request.

Query keys are arrays scoped by feature, matching the hook name — this
keeps invalidation targeted instead of nuking unrelated caches:

```typescript
// features/widgets/queries.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { browserApi } from "@/lib/api/client";

export function useWidgets() {
  return useQuery({
    queryKey: ["widgets"],
    queryFn: async () => {
      const { data, error } = await browserApi.GET("/api/v1/widgets");
      if (error) throw error;
      return data;
    },
  });
}

export function useCreateWidget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: WidgetCreate) => {
      const { data, error } = await browserApi.POST("/api/v1/widgets", { body });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["widgets"] });
    },
  });
}
```

`QueryClientProvider` is set up once in `lib/query-client.ts` and mounted
in the root layout — don't create a new `QueryClient` per component.

## Forms: react-hook-form + zod, backend is still the source of truth

Client-side validation is for immediate UX feedback, not the actual
contract — the backend's Pydantic schema is what's authoritative (see the
`fastapi` skill's schema conventions). Mirror the shape for a good
experience, but map the backend's 422 response into field errors so the
two validations can't silently disagree:

```tsx
"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const widgetFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  type: z.enum(["kpi", "chart", "table"]),
});

export function WidgetForm() {
  const form = useForm({ resolver: zodResolver(widgetFormSchema) });
  const createWidget = useCreateWidget();

  async function onSubmit(values: z.infer<typeof widgetFormSchema>) {
    try {
      await createWidget.mutateAsync(values);
    } catch (error) {
      // Map 422 field errors from the backend onto the form
      if (isValidationError(error)) {
        for (const [field, message] of Object.entries(error.fieldErrors)) {
          form.setError(field as keyof typeof values, { message });
        }
      }
    }
  }
  // ...
}
```

## Server Actions — only when something needs to run server-side

Default to the browser client + TanStack Query for mutations (that's
what CORS was set up for). Reach for a Server Action only when the
mutation needs a server-only secret or server-side logic the browser
shouldn't have. When you do write one, treat it exactly like a public API
endpoint — Server Actions are callable directly, not just from the UI
that renders the button:

```typescript
"use server";

export async function deleteWidget(widgetId: string) {
  const session = await verifySession(); // check auth INSIDE the action
  if (!session) throw new Error("Unauthorized");
  // ...
}
```

(Auth scheme for this project isn't chosen yet — when it is, `verifySession`
above becomes real. Don't invent an auth mechanism speculatively.)

## Route-segment error and empty states

- `error.tsx` per segment for the error boundary — client component,
  receives `error` and `reset`.
- `not-found.tsx` for the 404 case (backend returned 404 for the
  resource).
- Empty states (zero widgets, zero dashboards) are a UI decision, not an
  afterthought — see the `dataviz`/`frontend-design` skills' guidance on
  empty states as "an invitation to act," not a blank page.
