---
title: Use Existing Libraries Instead of Custom Code
paths:
  - "**/*"
impact: HIGH
---

# Use Existing Libraries Instead of Custom Code

Always search for existing libraries before writing custom code. Every line of custom code is a liability that requires maintenance, testing, and documentation. The "Not Invented Here" (NIH) syndrome leads to fragile, undertested reimplementations of solved problems.

Before writing any utility, helper, or infrastructure code, check for established packages that solve the problem. Custom code is only justified when:
- Specific business logic unique to the domain
- Performance-critical paths with special requirements
- When external dependencies would be overkill
- Security-sensitive code requiring full control
- When existing solutions don't meet requirements after thorough evaluation

## Incorrect

Custom retry logic is implemented from scratch instead of using an established library. This hand-rolled solution lacks features like exponential backoff, jitter, circuit breaking, and proper error classification that battle-tested libraries provide.

```typescript
// Custom retry utility — reinventing the wheel
async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      await new Promise((resolve) => setTimeout(resolve, delay))
    }
  }
  throw lastError!
}

const data = await retry(() => fetchFromApi('/users'))
```

NIH Syndrome — Anti-Pattern to Avoid:
- Writing custom authentication when Auth0, Supabase, or Firebase Auth exists
- Implementing custom state management when Redux, Zustand, or Jotai are battle-tested
- Building form validation from scratch when Zod, Yup, or React Hook Form handle it
- Reimplementing retry logic when Cockatiel or Oxylane provide proven solutions
- Rolling your own HTTP client when Axios or Ky have years of edge-case fixes

These reimplementations typically lack exponential backoff, jitter, circuit breaking, proper error classification, and timeout handling that battle-tested libraries provide out of the box.

## Correct

An established library handles retry logic with proven patterns for backoff, jitter, and circuit breaking out of the box.

```typescript
import { retry, handleAll, ExponentialBackoff } from 'cockatiel'

const retryPolicy = retry(handleAll, {
  maxAttempts: 3,
  backoff: new ExponentialBackoff(),
})

const data = await retryPolicy.execute(() => fetchFromApi('/users'))
```