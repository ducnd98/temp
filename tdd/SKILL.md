---
name: tdd
description: Test-Driven Development discipline for this monorepo (FastAPI backend + Next.js/shadcn frontend). Use whenever writing ANY production code - new features, API endpoints, services, React components, hooks, bug fixes, or behavior changes - even if the user never mentions tests. Also use when the user says implement, add, build, create, fix, refactor, endpoint, component, or TDD. Enforces red-green-refactor - write one failing test, watch it fail for the right reason, write minimal code to pass.
---

# Test-Driven Development

## Core principle

Write the test first. Watch it fail. Write minimal code to pass.

If you didn't watch the test fail, you don't know if it tests the right
thing. A test that passes on its first run is unverified — it may assert
nothing, test the wrong seam, or test a mock. Watching the failure is the
proof that the test can catch a bug. That proof is the entire point.

## The iron law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it and reimplement test-first. Don't
keep it "as reference", don't "adapt it while writing tests" — that is
testing after, with extra steps. Delete means delete. (Exploratory spikes
are fine: explore, learn, throw the spike away, then TDD the real thing.)

## When this applies

**Always:** new features, bug fixes, refactoring, behavior changes —
backend and frontend alike.

In this monorepo, **ALL frontend utilities** (formatting, data transformation),
**data normalization** (markdown parsing, frontmatter preservation),
**custom hooks** (debounce, hotkeys), and **stateful components** (search,
sorting, optimistic counters) REQUIRE Vitest unit/component tests first.

**Exceptions (confirm with the user first):** throwaway spikes, pure
declarative SVG icons, static asset imports with zero logic.

Thinking "skip TDD just this once because it's frontend"? That's a
rationalization — see the table below.

## Strict Scoped Verification: Frontend vs Backend Isolation

Never run full-monorepo cross-suite tests during routine task execution:

- **When working on Frontend (`frontend/`):** ONLY run `npm test` (Vitest)
  and `npm run build`. **NEVER** run `pytest` or activate `.venv`. UI
  modifications cannot break backend Python logic.
- **When working on Backend (`backend/`):** ONLY run `pytest` in the
  activated `.venv`. **NEVER** run `npm test` or `npm run build`.
- **Only run both suites:** When executing full-system End-to-End (E2E)
  integration milestones or altering shared OpenAPI contracts.

## The loop

One cycle = one seam, one test, one minimal implementation. Never write a
batch of tests upfront (that's horizontal slicing — you'd be testing
imagined behavior instead of letting each cycle teach the next).

```
1. RED       Write ONE minimal failing test for the next behavior.
   VERIFY    Run it. It must FAIL, and fail for the RIGHT reason:
             an assertion about missing behavior — not an import error,
             typo, or broken fixture. Passes immediately? The test is
             wrong or the behavior already exists. Stop and fix the test.

2. GREEN     Write the MINIMUM code to pass. No extra parameters, no
             speculative options, no "while I'm here" improvements.
             The fix belongs in the implementation — a test that's still
             failing after your change is telling you the implementation
             is wrong, not that the test is. Editing the test to match
             broken behavior instead of fixing the behavior is the
             single easiest way to silently defeat the whole practice.
   VERIFY    Run the package's full suite. Everything passes, output
             clean (no warnings, no skips you introduced).

3. REFACTOR  Only now: remove duplication, improve names, extract
             helpers. Tests stay green. Never add behavior here.

4. Repeat until the acceptance criteria are covered — including error
   paths (validation failures, 404s, empty states), not just happy paths.
```

## Pick the seam before writing the test

A **seam** is the public boundary you test at — where behavior is
observable without reaching inside. Tests written at seams read like
specifications and survive refactors; tests written against internals
break when structure changes even though behavior didn't.

Seams in this repo, most preferred first:

| Layer | Seam | Tools |
|---|---|---|
| Backend domain | service / use-case function in→out | pytest |
| Backend API | HTTP request→response through the ASGI app | pytest + httpx |
| Frontend component | rendered DOM + user events | Vitest + Testing Library |
| Frontend ↔ API contract | the network boundary | MSW |
| Critical user journey | real browser, real stack | Playwright — sparingly |

Distribution: many domain/API tests, some component tests, very few E2E
(reserve Playwright for login/checkout-class critical paths). If it's
unclear which behaviors matter enough to test, confirm the seams with the
user before writing anything.

## Stack-specific guides — read before writing the first test

- **Backend work (FastAPI, pytest, DB)** → read
  [references/backend-fastapi.md](references/backend-fastapi.md).
  Covers testing through the ASGI app, `dependency_overrides`, and the
  repository pattern that keeps domain tests independent of the (still
  undecided) database choice.
- **Frontend work (Next.js, Vitest, RTL, MSW)** → read
  [references/frontend-nextjs.md](references/frontend-nextjs.md).
  Covers user-facing queries, mocking at the network boundary, shadcn/ui
  policy, and Server Component logic extraction.
- **Before adding any mock, fake, or test utility** → read
  [references/anti-patterns.md](references/anti-patterns.md).
  The five failure modes that make test suites worthless, and the gate
  questions that catch them.

## Bug fixes

Never fix a bug without a test. The reproduction test is as much the
deliverable as the fix — it's the regression guard.

1. Write a test that reproduces the bug. Run it — it must fail in the way
   the bug report describes.
2. Write the minimal fix.
3. Full suite green.
4. Refactor if the fix exposed duplication.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks too. The test takes 30 seconds. |
| "I'll write tests after" | Tests that pass immediately prove nothing — you never saw them catch anything. |
| "Tests-after achieve the same thing" | Tests-after answer "what does this do?" Tests-first answer "what should this do?" — they discover edge cases instead of confirming remembered ones. |
| "I already manually tested it" | Ad-hoc, unrecorded, can't re-run. Gone on the next change. |
| "Deleting X hours of work is wasteful" | Sunk cost. Unverified code is debt, not progress. |
| "Deadline pressure" | Debugging untested code in production is the slow path. |
| "The test is hard to write" | Listen to it: hard to test = hard to use. Fix the design, not the discipline. |

## Red flags — stop and start over

Code before test · test passed on first run and you moved on · can't
explain why the test failed · mock setup longer than the test · asserting
that a mock was called instead of asserting behavior · loosening or
rewriting an assertion because the implementation doesn't satisfy it ·
"keep it as reference" · "this case is different because…"

## Definition of done

Before reporting the work complete, verify every box:

- [ ] Every new behavior has a test you watched fail first
- [ ] Each failure was for the right reason (missing behavior, not setup errors)
- [ ] Implementation is minimal — nothing the tests don't demand
- [ ] Full suite passes with clean output
- [ ] Scoped Verification enforced: frontend tests only for frontend; backend tests only for backend
- [ ] Fakes/mocks only at system boundaries (DB, network, clock, auth) — never your own modules
- [ ] Error paths and edge cases covered, not just happy paths
- [ ] Test names describe behavior ("returns 404 when widget missing"), not mechanics ("test_get_2")

Can't check every box? The work isn't done — resume the loop.
