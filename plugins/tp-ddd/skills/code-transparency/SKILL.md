---
name: code-transparency
description: Ensures code reveals its behavior at the call site — side effects are visible, data flows through return values, control flow is explicit, and commands are separated from queries. Makes code self-documenting and traceable.
when_to_use:
  - "what does this function do"
  - "hidden side effect"
  - "does this return or mutate"
  - "command vs query"
  - "should this function mutate or return"
  - "is this a side effect"
  - "pure function"
  - "where should I put error handling logic"
  - "data is unexpectedly changing after a function call"
  - "can't tell where a value came from"
  - "mutation disguised as query"
paths:
  - "src/**/*"
---

# Code Transparency

Code answers "what does this actually do?" at a glance. Side effects are visible at the call site, data flows through return values, control flow is explicit, and commands are separated from queries. These four principles work together: each one closes a channel where behavior can hide.

## Decision Router

```
IF caller cannot see what the line does without opening the function
  → Visible Side Effects (make effects explicit at call site)

IF function does both return and mutate, or returns through mutation
  → Command-Query Separation + Data Flow (pick one: return or mutate; return the value directly)

IF error handling or branching is hidden inside a helper
  → Explicit Control Flow (move policy to call site, keep mechanism pure)
```

---

# Command-Query Separation + Data Flow

A function must either return a value (query) or cause a side effect (command), never both. Mixing the two makes call sites deceptive: a mutation disguised as a query hides state changes, and a query that secretly throws hides control flow.

If a function produces a result, return it directly. Never rely on mutation of an input parameter to communicate output. Data flows through return values so the reader can trace where each value comes from.

**CQS violation → split into command and query. EDF violation → return the value instead of mutating to produce it.**

## Incorrect

```typescript
// Mutation disguised as query — caller sees assignment but not the mutation
const result = {}
if (featureEnabled)
  applyNewFeature(result)  // mutates result in-place, looks like command but used as query

// Hidden command — looks like pure check but throws
const result = performProcess(param)
validateResult(result)  // throws — caller sees no branching
```

## Correct

```typescript
// Return the value directly — data flow is one line, no hidden mutation
const result = featureEnabled ? applyNewFeature(baseData) : {}

// Explicit control flow — throws visible at call site
const result = performProcess(param)
if (!isValid(result))
  throw new ProcessingError(result)

// Transformation chain — each step produces new value, traceable at every step
const basePrice = calculateLineItems(order.items);
const discountedPrice = applyDiscount(basePrice, order.couponCode);
const taxAmount = computeTax(discountedPrice, order.shippingAddress);
const orderTotal = sumTotal(discountedPrice, taxAmount);
```

## Anti-Pattern: Implicit Chain

```typescript
// Mutation hides which step produced which value
const order = { items: order.items };
applyDiscount(order);   // mutates in-place
computeTax(order);      // mutates in-place
sumTotal(order);        // what is the final value?
```

---

# Visible Side Effects

Side effects — persistence, notifications, external calls — must be visible at the call site, not hidden inside function implementations. A reader scanning the orchestrator must see every effect the system produces without opening any implementation.

## Incorrect

```typescript
// Opaque orchestration — reader must open processOrder to learn what it does
async function handleCheckout(req: Request): Promise<Response> {
  const order = buildOrder(req.body);
  await processOrder(order);  // saves to DB? sends email? charges payment? hidden
  return Response.json({ status: "ok" });
}

async function processOrder(order: Order): Promise<void> {
  await orderRepository.save(order);
  await paymentGateway.charge(order.customerId, order.total);
  await emailService.sendConfirmation(order.customerId, order.id);
  await eventBus.publish("OrderCompleted", { orderId: order.id });
}
```

## Correct

```typescript
// Transparent orchestration — every effect visible
async function handleCheckout(req: Request): Promise<Response> {
  const order = buildOrder(req.body);
  await orderRepository.save(order);
  await paymentGateway.charge(order.customerId, order.total);
  await emailService.sendConfirmation(order.customerId, order.id);
  await eventBus.publish("OrderCompleted", { orderId: order.id });
  return Response.json({ status: "ok" });
}
```

---

# Explicit Control Flow

Error conditions and branching must be visible at the call site — never hidden inside helper functions that look like simple validators. Policy (what to do with a result) stays at the call site; mechanism (pure computation) can be extracted.

## Mechanism vs Policy

- **Mechanism** = `isValid(result)` returns a boolean. Pure function, no side effects.
- **Policy** = the caller decides to throw, log, branch, or ignore.

## Incorrect

```typescript
// validateResult hides throws inside what reads like a passive check
function validateResult(result: Result): void {
  if (!result.success)
    throw new ProcessingError(result.error)
  if (result.value < 0)
    throw new RangeError("Negative value")
}

const result = performProcess(param)
validateResult(result)  // two possible throws invisible at call site

// Feature flag policy hidden inside mechanism
function applyNewFeature(data: Data): Data {
  if (!featureFlags.isEnabled("new-feature"))
    return data  // policy decision buried in transformation
  return transform(data)
}

const output = applyNewFeature(baseData)  // reader cannot tell flag is checked
```

## Correct

```typescript
// Mechanism is pure, policy is explicit
function isValid(result: Result): boolean {
  return result.success && result.value >= 0
}

const result = performProcess(param)
if (!isValid(result))
  throw new ProcessingError(result)

// Feature flag policy at call site, mechanism is pure transformation
function applyNewFeature(data: Data): Data {
  return transform(data)  // always transforms
}

const output = featureEnabled ? applyNewFeature(baseData) : baseData
```

---

# Unified Example

All four principles working together:

```typescript
// Query: pure, returns, no mutation
function calculatePrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// Query: pure, returns, no mutation
function applyDiscount(price: number, code: string): number {
  return code === "SAVE20" ? price * 0.8 : price
}

// Query: pure, returns, no mutation
function isValid(price: number): boolean {
  return price >= 0 && price < 1_000_000
}

// Policy visible at call site — control flow is explicit, no hidden throws
const price = calculatePrice(order.items)
const discounted = applyDiscount(price, order.couponCode)
if (!isValid(discounted))
  throw new ValidationError("Invalid price")

// Commands: side effects visible, no hidden mutations
await db.save({ orderId: order.id, total: discounted })
await paymentGateway.charge(order.customerId, discounted)
```

---

# Anti-Patterns to Avoid

| Pattern | Problem | Fix |
|---------|---------|-----|
| `const x = compute()` then `compute()` again | Mutation disguised as command | Return value, assign once |
| `let x = {}; mutate(x)` | Mutation hidden behind assignment | Return new value, use const |
| `validate(x)` without return check | Hidden throw at call site | Return boolean, explicit if |
| `process(order)` as single opaque call | Side effects hidden in implementation | Expand at call site |
| `formatThenLog(result)` | Two responsibilities in one call | Separate format (mechanism) and log (policy) |
| `if (x) transform(x)` unclear if x mutated | Data flow opaque | Return new value, assign to new name |

---

# References

- [Command-Query Separation](https://en.wikipedia.org/wiki/Command%E2%80%93query_separation)
- [Referential Transparency](https://en.wikipedia.org/wiki/Referential_transparency)
- [Immutability and Pure Functions](https://mostly-adequate.gitbook.io/ch03)