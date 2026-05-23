---
name: code-architecture
description: Answers "how should I structure this code?" by merging four principles: layered architecture for separation of concerns, functional core with imperative shell for testable business logic, early returns for flat control flow, and function/file size limits for decomposable units. Use when business logic leaks into controllers, tests require heavy mocking, or functions have excessive nesting or length.
when_to_use:
  - "where does business logic go"
  - "where should this logic go"
  - "should domain know about database"
  - "how do I test this without mocks"
  - "too much nesting"
  - "too many parameters"
  - "this function does too much"
  - "function is too long"
  - "I need to scroll to see the main logic"
  - "business logic lives inside controllers or UI components"
  - "cannot test business rules without HTTP stack"
paths:
  - "src/**/*"
---

# Code Architecture: Structure for Maintainability

Three complementary principles govern code structure. They compose: layered architecture defines the topology, functional core keeps business logic testable, and early returns keep functions flat.

## Decision Router

**Q: Where do I put this code?**
- Business rule/calculation that needs no I/O → **pure function** in the domain layer
- Orchestration of multiple steps → **use case/service** that delegates to interfaces
- HTTP/event handling → **controller/adapter** that delegates to use cases
- Data persistence → **repository** implementing a domain interface
- Side effects (email, logging, external APIs) → **imperative shell** at the composition root

**Q: Why is this hard to test?**
- Business logic mixed with I/O → extract to **pure core function**
- Too many mocks required → **push I/O to the shell**, keep core deterministic

**Q: Why can't I read this function?**
- Nested conditionals pushing happy path deep → use **early returns** to flatten
- Too many parameters making the function hard to use → split into **smaller functions with focused signatures**
- Multiple responsibilities mixed → split into **separate functions by concern**

---

## Layered Architecture

Keep business logic in pure domain and use case layers, free of framework or infrastructure dependencies. When domain logic is coupled to controllers, ORMs, or HTTP libraries, it becomes untestable in isolation, impossible to reuse across delivery mechanisms, and fragile to infrastructure changes.

### Critical Principles

- Domain logic must remain framework-agnostic — coupling to web frameworks or ORMs makes the core untestable and unreusable
- Use cases orchestrate business flow through abstract interfaces — concrete implementations belong in infrastructure, not application logic
- Dependency injection inverts control so the domain defines what it needs and infrastructure satisfies it
- Separating concerns at the boundary prevents infrastructure decisions from constraining business rules

### Anti-pattern

Business logic embedded directly in the HTTP handler, coupled to the web framework and database client:

```typescript
// Bad: everything in one place
app.post("/orders", async (req, res) => {
  const { customerId, items } = req.body;

  // Business rule mixed into the controller
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const discount = total > 100 ? total * 0.1 : 0;

  const order = await prisma.order.create({
    data: { customerId, total: total - discount, items: { create: items } },
  });

  res.json(order);
});
```

### Correct

Domain logic in a framework-free function. Controller delegates to use case:

```typescript
// domain/order.ts — pure business logic, no framework imports
export function calculateOrderTotal(items: OrderItem[]): number {
  const subtotal = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const discount = subtotal > 100 ? subtotal * 0.1 : 0;
  return subtotal - discount;
}

// application/create-order.ts — use case depends on abstraction
export class CreateOrder {
  constructor(private readonly orders: OrderRepository) {}

  async execute(customerId: string, items: OrderItem[]): Promise<Order> {
    const total = calculateOrderTotal(items);
    return this.orders.save({ customerId, total, items });
  }
}

// infrastructure/controller.ts — thin adapter
app.post("/orders", async (req, res) => {
  const order = await createOrder.execute(req.body.customerId, req.body.items);
  res.json(order);
});
```

---

## Functional Core, Imperative Shell

Keep business logic in pure functions that take inputs and return outputs with no side effects. Push all side effects — database calls, HTTP requests, logging, file I/O, and state mutations — to an outer "imperative shell" that orchestrates the pure core.

Pure functions are deterministic: given the same inputs they always produce the same outputs. This makes them trivially testable without mocks, easy to reason about, and safe to compose and parallelize.

### Anti-pattern

Business calculation tangled with logging, database reads, and persistence. Testing requires mocking the logger, database, and notification service:

```typescript
async function applySubscriptionRenewal(
  customerId: string,
  logger: Logger,
  db: Database,
  mailer: Mailer
): Promise<void> {
  const customer = await db.customers.findById(customerId);
  const plan = await db.plans.findById(customer.planId);

  // Pure calculation mixed with side effects
  let price = plan.basePrice;
  if (customer.loyaltyYears >= 3) {
    price = price * 0.85;
    logger.info(`Applied 15% loyalty discount for ${customerId}`);
  }
  if (customer.referralCount >= 5) {
    price = price - 10;
    logger.info(`Applied $10 referral credit for ${customerId}`);
  }
  const tax = price * customer.taxRate;
  const total = price + tax;

  await db.invoices.create({ customerId, total, tax });
  await mailer.send(customer.email, `Your renewal total is $${total}`);
  logger.info(`Renewal processed: ${customerId}, total: ${total}`);
}
```

### Correct

Pure core calculates renewal price with no side effects. Imperative shell fetches data, calls pure function, then performs all I/O:

```typescript
interface RenewalInput {
  basePrice: number;
  loyaltyYears: number;
  referralCount: number;
  taxRate: number;
}

interface RenewalResult {
  price: number;
  tax: number;
  total: number;
  appliedDiscounts: string[];
}

// Pure core — deterministic, no side effects, trivially testable
function calculateRenewal(input: RenewalInput): RenewalResult {
  const discounts: string[] = [];
  let price = input.basePrice;

  if (input.loyaltyYears >= 3) {
    price = price * 0.85;
    discounts.push("loyalty_15pct");
  }
  if (input.referralCount >= 5) {
    price = price - 10;
    discounts.push("referral_credit_10");
  }

  const tax = price * input.taxRate;
  return { price, tax, total: price + tax, appliedDiscounts: discounts };
}

// Imperative shell — orchestrates I/O around the pure core
async function processRenewal(
  customerId: string,
  db: Database,
  mailer: Mailer,
  logger: Logger
): Promise<void> {
  const customer = await db.customers.findById(customerId);
  const plan = await db.plans.findById(customer.planId);

  const result = calculateRenewal({
    basePrice: plan.basePrice,
    loyaltyYears: customer.loyaltyYears,
    referralCount: customer.referralCount,
    taxRate: customer.taxRate,
  });

  await db.invoices.create({ customerId, total: result.total, tax: result.tax });
  await mailer.send(customer.email, `Your renewal total is $${result.total}`);
  logger.info("Renewal processed", { customerId, ...result });
}
```

---

## Early Returns

Always use early returns to handle error conditions and edge cases at the top of functions instead of wrapping logic in nested conditionals. Keeps the happy path at the top level, reducing cognitive load.

Deeply nested code (more than 3 levels) increases cognitive load, obscures the happy path, and makes functions harder to read, review, and maintain.

### Anti-pattern

Validation checks nested inside each other, pushing core business logic deep into indentation:

```typescript
async function validateUser(userId: string, role: string): Promise<User> {
  if (userId) {
    const user = await db.users.findById(userId)
    if (user) {
      if (!user.isDeleted) {
        if (user.role === role) {
          if (user.emailVerified) {
            // happy path buried 5 levels deep
            return user
          } else {
            throw new Error('Email not verified')
          }
        } else {
          throw new Error('Insufficient role')
        }
      } else {
        throw new Error('User is deleted')
      }
    } else {
      throw new Error('User not found')
    }
  } else {
    throw new Error('User ID is required')
  }
}
```

### Correct

Guard clauses handle each error condition with an early return at the top level. The happy path flows naturally at the end:

```typescript
async function validateUser(userId: string, role: string): Promise<User> {
  if (!userId)
    throw new Error('User ID is required')

  const user = await db.users.findById(userId)
  if (!user)
    throw new Error('User not found')
  if (user.isDeleted)
    throw new Error('User is deleted')
  if (user.role !== role)
    throw new Error('Insufficient role')
  if (!user.emailVerified)
    throw new Error('Email not verified')

  return user
}
```

---

## Function Size Limits

Decompose functions longer than 80 lines into smaller, focused functions of 50 lines or fewer. When a function grows beyond 80 lines, it is almost certainly doing more than one thing.

Keep files under 200 lines. Large files accumulate multiple responsibilities, making them harder to test, review, and reuse. Extract cohesive blocks into named functions that each serve a single purpose. If extracted functions are only used in the same context, keep them in the same file. When a file exceeds 200 lines after decomposition, split related functions into separate modules grouped by responsibility.

### Anti-pattern

Single function over 80 lines handling validation, transformation, persistence, and notification:

```typescript
// Bad: one function does everything
async function handleUserRegistration(input: unknown): Promise<User> {
  // validation (20 lines)
  // transformation (20 lines)
  // persistence (20 lines)
  // notification (20 lines)
  // total: 80+ lines, impossible to test in isolation
}
```

### Correct

Decompose by responsibility, keep related functions in same file:

```typescript
function validateRegistrationInput(input: unknown): RegistrationInput {
  if (!input || typeof input !== 'object') throw new Error('Invalid input')
  const { email, name, password, role } = input as Record<string, unknown>
  if (!email || typeof email !== 'string') throw new Error('Email required')
  if (!name || typeof name !== 'string') throw new Error('Name required')
  if (!password || typeof password !== 'string') throw new Error('Password required')
  if (password.length < 8) throw new Error('Password too short')
  if (!/[A-Z]/.test(password)) throw new Error('Password needs uppercase')
  if (!/[0-9]/.test(password)) throw new Error('Password needs digit')
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Invalid email format')
  return { email, name, password, role: typeof role === 'string' ? role : 'user' }
}

async function normalizeAndHash(input: RegistrationInput): Promise<NormalizedUser> {
  return {
    email: input.email.toLowerCase().trim(),
    name: input.name.trim().replace(/\s+/g, ' '),
    password: await bcrypt.hash(input.password, 12),
    role: input.role === 'admin' ? 'user' : input.role,
  }
}

async function persistUser(data: NormalizedUser): Promise<User> {
  const existing = await db.users.findUnique({ where: { email: data.email } })
  if (existing) throw new Error('Email already registered')
  return db.users.create({ data: { ...data, createdAt: new Date(), updatedAt: new Date() } })
}

async function processUserRegistration(input: unknown): Promise<User> {
  const validated = validateRegistrationInput(input)
  const normalized = await normalizeAndHash(validated)
  const user = await persistUser(normalized)
  return user
}
```

Each function stays under 20 lines. Related functions remain in the same file. Testing is isolated and focused.

---

## How They Compose

These four principles work together:

1. **Layered architecture** defines where code lives (domain vs infrastructure)
2. **Functional core** keeps domain logic pure and testable
3. **Early returns** keep functions flat and readable
4. **Size limits** keep functions focused and decomposable

Example that uses all three:

```typescript
// 1. Domain layer: pure function with early return
export function validateOrder(order: Order): ValidationResult {
  if (!order.items?.length)
    return { valid: false, error: "Order must have items" };
  if (!order.customerId)
    return { valid: false, error: "Customer required" };

  const total = order.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  if (total <= 0)
    return { valid: false, error: "Order total must be positive" };

  return { valid: true, total };
}

// 2. Use case: orchestrates through interfaces, uses early returns
export class PlaceOrder {
  constructor(
    private readonly orders: OrderRepository,
    private readonly payments: PaymentGateway
  ) {}

  async execute(data: PlaceOrderData): Promise<Order> {
    // Early return on validation
    const validation = validateOrder(data);
    if (!validation.valid)
      throw new ValidationError(validation.error);

    // Pure calculation
    const total = validation.total!;

    // Infrastructure call in shell
    const order = await this.orders.create({ ...data, total });
    await this.payments.charge(data.customerId, total);

    return order;
  }
}

// 3. Controller: thin adapter that delegates
app.post("/orders", async (req, res) => {
  const order = await placeOrder.execute(req.body);
  res.status(201).json(order);
});
```

---

## Reference

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Functional Core, Imperative Shell - Gary Bernhardt](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Boundaries - Gary Bernhardt (talk)](https://www.destroyallsoftware.com/talks/boundaries)