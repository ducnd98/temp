# Testing Anti-Patterns

Read this before adding any mock, fake, or test utility. These five
failure modes are how test suites become worthless while coverage numbers
stay green. TDD done strictly prevents all of them — if you watched the
test fail against real code first, you can't be testing a mock.

## 1. Testing mock behavior

Asserting that a mock exists or was called, instead of asserting behavior.

```tsx
// BAD: verifies the mock works, not the component
expect(screen.getByTestId("sidebar-mock")).toBeInTheDocument();
expect(mockPayment.process).toHaveBeenCalledWith(cart.total);

// GOOD: verifies observable behavior
expect(screen.getByRole("navigation")).toBeInTheDocument();
expect(result.status).toBe("confirmed");
```

Gate question before asserting on anything mocked: *"Am I testing real
behavior, or just that my mock is wired up?"* If the test would still pass
with the real feature broken, delete the assertion or unmock.

## 2. Implementation coupling

Mocking internal collaborators, testing private methods, asserting call
counts/order, or verifying through a side channel. The tell: refactor with
behavior unchanged → test breaks.

```python
# BAD: bypasses the interface to verify
await create_user(name="Alice")
row = await db.execute("SELECT * FROM users WHERE name='Alice'")
assert row is not None

# GOOD: verifies through the interface
user = await create_user(name="Alice")
assert (await get_user(user.id)).name == "Alice"
```

Mock only at system boundaries — external APIs, database, clock,
randomness, filesystem. Never your own modules, classes, or hooks. If
isolating your own code requires mocks, the design is too coupled: inject
the dependency instead.

## 3. Tautological tests

The expected value is recomputed the same way the implementation computes
it, so the test passes by construction and can never disagree with the
code.

```typescript
// BAD: mirrors the implementation
const expected = items.reduce((sum, i) => sum + i.price, 0);
expect(calculateTotal(items)).toBe(expected);

// GOOD: independent, known literal
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
```

Expected values come from an independent source of truth: a worked
example, the spec, a known-good literal. If you find yourself importing
the same helper the implementation uses to build the expectation, stop.

## 4. Incomplete mocks and partial fakes

Mocking only the fields or methods the current test touches. Downstream
code reads a field you omitted → tests pass, integration fails, silently.

```typescript
// BAD: only what this test reads
const mockResponse = { status: "success", data: { userId: "123" } };

// GOOD: the complete real shape
const mockResponse = {
  status: "success",
  data: { userId: "123", name: "Alice" },
  metadata: { requestId: "req-789", timestamp: 1234567890 },
};
```

Rule: a mock or fake mirrors the COMPLETE real structure — check the
actual API response or implement the full repository interface. If you
don't understand the whole shape, you don't understand it well enough to
mock it: run against the real thing first, observe, then mock minimally.

The same applies to behavior. Before mocking a method, ask what side
effects it has and whether the test depends on any of them. Over-mocking
"to be safe" removes side effects tests silently rely on — they then pass
for the wrong reason or fail mysteriously. Mock the slow/external
operation at the bottom, not the high-level method the test flows through.

## 5. Test-only methods in production code

```typescript
// BAD: destroy() exists only so tests can clean up
class Session {
  async destroy() { /* ... */ }
}

// GOOD: cleanup lives in test utilities
// test-utils/cleanup.ts
export async function cleanupSession(session: Session) { /* ... */ }
```

Gate question before adding any method to a production class: *"Is this
only called from tests?"* If yes, it belongs in `tests/` utilities.
Production classes polluted with test hooks are dangerous (someone will
call them) and confuse the object's real lifecycle.

## Warning signs your mocks have gone too far

- Mock setup is longer than the test logic
- The test fails when you remove a mock (the mock IS the behavior)
- You can't explain why a particular mock is needed
- Mocking "just to be safe" / "it might be slow"

When you see these, prefer an integration-style test with real components
— it's usually simpler than maintaining the mock, and it tests something.
