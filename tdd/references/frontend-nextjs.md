# Frontend TDD — Next.js + Vitest + Testing Library + MSW

How to run the red-green-refactor loop on the frontend of this monorepo.

## Layout and commands

Frontend code lives in `frontend/` organized as feature folders
(`src/features/widgets/` — see the `nextjs` skill for the structure; the
`shadcn` skill governs the UI primitives), with tests colocated next to
the code they test (`features/widgets/widget-form.tsx` +
`features/widgets/widget-form.test.tsx`). Run from `frontend/`:

```bash
npm test                     # vitest run — full suite, every VERIFY GREEN
npx vitest run widget-form   # one file — VERIFY RED
```

Test stack: `vitest`, `@testing-library/react`, `@testing-library/user-event`,
`@testing-library/jest-dom`, `jsdom` (or `happy-dom`), `msw` for the
network boundary, `playwright` for the few real E2E journeys.

## Test what the user sees and does

The seam for a component is its rendered DOM plus user events — not its
props wiring, not its internal state, not which hooks it calls.

```tsx
// features/widgets/widget-form.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WidgetForm } from "./widget-form";

test("shows validation error when name is empty", async () => {
  render(<WidgetForm onSubmit={vi.fn()} />);

  await userEvent.click(screen.getByRole("button", { name: /save/i }));

  expect(screen.getByText(/name is required/i)).toBeInTheDocument();
});

test("submits trimmed name", async () => {
  const onSubmit = vi.fn();
  render(<WidgetForm onSubmit={onSubmit} />);

  await userEvent.type(screen.getByLabelText(/name/i), "  gauge  ");
  await userEvent.click(screen.getByRole("button", { name: /save/i }));

  expect(onSubmit).toHaveBeenCalledWith({ name: "gauge" });
});
```

Query priority: `getByRole` > `getByLabelText` > `getByText` >
`getByTestId` (last resort only, when no accessible query exists). This
isn't style preference — role/label queries fail when the UI stops being
usable (button loses its accessible name, input loses its label), which is
exactly what you want a test to catch. CSS-class and test-id queries keep
passing while the UI breaks for real users.

## Mock at the network boundary with MSW

When a component fetches data, mock the HTTP layer — never `vi.mock` your
own hooks, data functions, or `fetch` itself. Mocking your own modules
couples tests to internal structure (the tell: refactor the hook, tests
break, behavior unchanged). MSW intercepts at the same boundary the real
app uses, so tests exercise your real data path.

```ts
// test/msw-handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/widgets", () =>
    HttpResponse.json([{ id: "w1", name: "gauge", type: "kpi" }])
  ),
];
```

Handler responses mirror the real API's complete shape — every field the
backend returns, not just the fields today's test reads. Partial fixtures
pass today and explode when a component starts reading an omitted field.
When the backend contract changes, update handlers in the same commit.

## shadcn/ui policy

Don't test the primitives themselves — that a `Button` renders or a
`Dialog` opens is Radix/shadcn's contract, not yours. Test YOUR behavior
composed on top: that submitting the form inside the Dialog calls your
API, that selecting an option updates your state. If a test only asserts
that a shadcn component exists on screen, delete the test.

## Server Components and route handlers

Async Server Components don't render in jsdom, and route handlers are just
functions. Keep both thin: extract logic (filtering, aggregation,
validation, mapping) into plain functions and TDD those with plain vitest
— no DOM needed.

```ts
// lib/dashboard.test.ts
import { summarize } from "./dashboard";

test("summarize counts widgets by type", () => {
  expect(
    summarize([{ type: "kpi" }, { type: "kpi" }, { type: "chart" }])
  ).toEqual({ kpi: 2, chart: 1 });
});
```

Interactive behavior stays in Client Components, tested with RTL as above.
The full server-rendered page is covered by the (few) Playwright journeys.

## Playwright — sparingly

Real-browser E2E is the most expensive seam: slow, flaky-prone, needs the
whole stack. Reserve it for critical user journeys (login, the primary
dashboard flow) — a handful of tests, not a layer that re-verifies what
component tests already cover. E2E failures should mean "a critical
journey is broken", not "a button moved".

## Rules of thumb

- One behavior per test; arrange–act–assert, one act per test.
- `userEvent`, not `fireEvent` — it simulates real interaction sequences.
- Async UI: `await screen.findByText(...)`, never manual timeouts.
- Don't assert on implementation: no snapshot-everything, no "renders
  without crashing", no asserting a hook was called.
