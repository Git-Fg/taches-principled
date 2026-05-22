---
title: Use Domain-Specific Names Instead of Generic Module Names
paths:
  - "**/*"
impact: HIGH
---

# Use Domain-Specific Names Instead of Generic Module Names

Avoid generic module names like `utils`, `helpers`, `common`, and `shared`. These names attract unrelated functions, creating grab-bag files with no cohesion. Use domain-specific names that reflect the bounded context and the module's single responsibility — names like `OrderCalculator`, `UserAuthenticator`, or `InvoiceGenerator` make purpose immediately clear and enforce cohesion by design.

Generic names signal missing domain analysis. When a developer reaches for `utils.ts`, it usually means the function belongs in a domain module that has not been identified yet. Naming modules after their domain concept prevents them from becoming dumping grounds and keeps each module focused on a single, clear purpose.

Domain naming means naming with behavior — the name should tell you what the module does, not just what data it touches. A module named after a noun (`UserHelper`) still attracts random functions. A module named after a behavior (`AuthenticateUser`, `GenerateInvoice`) enforces a single purpose by its very name.

## Incorrect

Generic module names attract unrelated functions, making the file a dumping ground with no cohesion or clear ownership.

```typescript
// utils.ts — grab-bag of unrelated functions
export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function formatUserDisplayName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}

export function generateInvoiceNumber(): string {
  return `INV-${Date.now()}`;
}
```

Generic naming anti-patterns to avoid:
- `utils.js` with 50 unrelated functions
- `helpers/misc.js` as a dumping ground
- `common/shared.js` with unclear purpose

## Correct — Domain Names with Behavior

Each module is named after what it does, not what data it touches. The name implies behavior.

```typescript
// order-pricing.ts — all order pricing behavior
export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function applyVolumeDiscount(subtotal: number, itemCount: number): number {
  return itemCount >= 5 ? subtotal * 0.9 : subtotal;
}

// payment-gateway.ts — payment processing behavior
export interface PaymentAuthorization {
  approved: boolean;
  transactionId: string;
  declineReason?: string;
}

export async function authorizePayment(
  customerId: string,
  amount: number,
  currency: string
): Promise<PaymentAuthorization> { /* ... */ }

// invoice-generator.ts — invoice creation behavior
export function generateInvoiceNumber(): string {
  return `INV-${Date.now()}`;
}

export interface InvoiceLine {
  description: string;
  quantity: number;
  unitPrice: number;
}

export function createInvoice(lines: InvoiceLine[], customerId: string): Invoice { /* ... */ }

// user-authenticator.ts — authentication behavior
export async function authenticateUser(
  email: string,
  password: string
): Promise<AuthResult> { /* ... */ }
```

## Why Behavior Names Work

| Generic Name | Domain Name | Why It Matters |
|---|---|---|
| `User` | `UserAuthenticator` | A `User` class could be anything. `UserAuthenticator` can only do one thing — authenticate users. |
| `Order` | `OrderCalculator` | An `Order` class accumulates unrelated methods. `OrderCalculator` can only compute order values. |
| `Payment` | `PaymentGateway` | A `Payment` class invites all payment-related code. `PaymentGateway` has a clear contract — it talks to an external payment system. |
| `Invoice` | `InvoiceGenerator` | An `Invoice` model becomes a data struct. `InvoiceGenerator` is a factory with behavior. |

When every module name contains a verb or implies a capability (not just a noun), the architecture self-documents.