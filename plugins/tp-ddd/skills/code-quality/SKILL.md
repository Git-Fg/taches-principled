---
name: code-quality
description: Merges three code quality principles: domain-specific naming (avoiding generic names like utils), library-first approach (use battle-tested libs over custom code), and visible error handling (typed errors with logging).
when_to_use:
  - "what should I name this"
  - "is utils a good name"
  - "should I use a library"
  - "why did this error happen"
  - "silent failure"
paths:
  - "**/*"
---

# Code Quality — Idiom Check

Answer one question first to route to the right principle.

## Decision Router

```
Is the issue about HOW something is named?
  → Domain Naming

Is the issue about WRITING vs USING something?
  → Library First

Is the issue about an ERROR being VISIBLE?
  → Visible Errors
```

---

## Domain Naming

Avoid generic module names like `utils`, `helpers`, `common`, `shared`. Use domain-specific names that reflect the bounded context and single responsibility — names like `OrderCalculator`, `UserAuthenticator`, `InvoiceGenerator` make purpose immediately clear.

Generic names signal missing domain analysis. A module named `utils.ts` attracts any unrelated function. A module named `order-pricing.ts` can only do one thing by design.

Domain naming means naming with behavior. A module named after a noun (`UserHelper`) still attracts random functions. A module named after behavior (`AuthenticateUser`) enforces a single purpose by its very name.

### Correct Example

```typescript
// order-pricing.ts — order pricing behavior only
export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function applyVolumeDiscount(subtotal: number, itemCount: number): number {
  return itemCount >= 5 ? subtotal * 0.9 : subtotal;
}

// invoice-generator.ts — invoice creation behavior only
export function generateInvoiceNumber(): string {
  return `INV-${Date.now()}`;
}

export interface InvoiceLine {
  description: string;
  quantity: number;
  unitPrice: number;
}
```

### Anti-Patterns to Avoid

- `utils.ts` with 50 unrelated functions
- `helpers/misc.js` as a dumping ground
- `common/shared.js` with unclear purpose
- `User` class that accumulates unrelated methods

---

## Library First

Search for existing battle-tested libraries before writing custom code. Every line of custom code is a liability that requires maintenance, testing, and documentation.

Custom code is only justified when:
- Specific business logic unique to the domain
- Performance-critical paths with special requirements
- External dependencies would be overkill
- Security-sensitive code requiring full control
- Existing solutions don't meet requirements after thorough evaluation

### Correct Example

```typescript
import { retry, handleAll, ExponentialBackoff } from 'cockatiel'

const retryPolicy = retry(handleAll, {
  maxAttempts: 3,
  backoff: new ExponentialBackoff(),
})

const data = await retryPolicy.execute(() => fetchFromApi('/users'))
```

### NIH Syndrome Anti-Patterns

These reimplementations typically lack exponential backoff, jitter, circuit breaking, proper error classification, and timeout handling:

- Custom authentication when Auth0, Supabase, or Firebase Auth exist
- Custom state management when Redux, Zustand, or Jotai are battle-tested
- Form validation from scratch when Zod, Yup, or React Hook Form handle it
- Retry logic when Cockatiel provides proven solutions
- HTTP client when Axios or Ky have years of edge-case fixes

---

## Visible Errors

Never silently swallow exceptions. Every catch block must use typed error handling and log the error before rethrowing or returning a failure result. Generic `catch (e)` blocks hide the root cause of failures, making production debugging nearly impossible.

Use typed catch blocks that distinguish between expected domain errors and unexpected system failures. Log the error with sufficient context (operation name, relevant IDs) before rethrowing so the failure is traceable in logs even if the caller also catches it.

### Correct Example

```typescript
async function processPayment(orderId: string, amount: number) {
  try {
    const result = await paymentGateway.charge(orderId, amount);
    await db.orders.update(orderId, { status: "paid" });
    return result;
  } catch (error) {
    if (error instanceof PaymentDeclinedError) {
      logger.warn("Payment declined", { orderId, amount, reason: error.reason });
      throw new DomainError(`Payment declined for order ${orderId}`);
    }
    if (error instanceof NetworkError) {
      logger.error("Payment gateway unreachable", { orderId, amount, cause: error });
      throw new InfrastructureError("Payment service unavailable", { cause: error });
    }
    logger.error("Unexpected payment failure", { orderId, amount, error });
    throw error;
  }
}
```

### Anti-Patterns to Avoid

- `catch (e) { return null }` — silently swallowed
- `catch { }` — no error variable at all
- Generic `catch (error)` without type checking
- Catch blocks without logging before rethrow
- Errors disappearing in production with no trace

---

## Merged Quality Checklist

Before finalizing any code, verify:

- [ ] Module names reflect behavior, not generic categories
- [ ] No `utils`, `helpers`, `common`, or `shared` files
- [ ] No utility/helper functions that duplicate library functionality
- [ ] Every catch block has typed handling and logging
- [ ] No silent swallowing of exceptions