# TypeScript Best Practices

## Type Safety

All code must be strictly typed. Leverage TypeScript's type system fully — avoid escape hatches and prefer type narrowing over type assertions.

- **Avoid explicit type annotations when TypeScript can infer.** Let inference work; add annotations only where inference is ambiguous.
- **Avoid implicitly `any`.** If inference fails, type it explicitly rather than letting `any` propagate.
- **Use accurate types.** Prefer `Record<PropertyKey, unknown>` over `object` or `any`.
- **Prefer `interface` for object shapes** (e.g., function parameters, React props); use `type` for unions, intersections, and derived types.
- **Prefer `as const satisfies XyzInterface` over plain `as const`** for type-checked constant definitions.
- **Prefer `@ts-expect-error` over `@ts-ignore` over `as any`.** The first fails if the error is removed, alerting you to update the suppression. Never use `as any` as a suppression mechanism.
- **Avoid meaningless null/undefined parameters.** Design strict function contracts with non-nullable types unless null is semantically meaningful.
- **Prefer ES module augmentation** (`declare module '...'`) over `namespace`. Do not use `namespace`-based extension patterns.

### Eliminating `any` with Generics

```typescript
// Before — loses type information
function getProperty(obj: any, key: string): any {
  return obj[key];
}

// After — preserves type via generics
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
// getProperty({ name: "Alice" }, "name") → inferred as string
```

### Narrowing an Unknown API Response

```typescript
interface User { id: number; name: string }

function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

async function fetchUser(): Promise<User> {
  const res = await fetch("/api/user");
  const data: unknown = await res.json();
  if (!isUser(data)) throw new Error("Invalid user shape");
  return data;
}
```

## Branded (Opaque) Types

TypeScript uses structural typing, so two types with the same shape are interchangeable — even when they represent different domain concepts. Use a phantom brand property to create nominal distinction.

```typescript
type Opaque<TValue, TBrand> = TValue & { __brand: TBrand };

type UserId = Opaque<string, "UserId">;
type PostId = Opaque<string, "PostId">;

function getUser(id: UserId): User { /* ... */ }
function getPost(id: PostId): Post { /* ... */ }

const userId = "user-123" as UserId;
const postId = "post-456" as PostId;

getUser(userId); // OK
getUser(postId); // Error: Type 'PostId' is not assignable to type 'UserId'
```

Use branded types for entity IDs, validated data, and any value where mixing up the underlying primitive would cause a bug.

## Discriminated Unions

Model mutually exclusive states with discriminated unions. Each variant has a literal `type` (or `kind`) discriminant that TypeScript narrows on.

```typescript
type ApiResult<T> =
  | { kind: "success"; data: T }
  | { kind: "error"; code: number; message: string }
  | { kind: "loading" };

function handleResult<T>(result: ApiResult<T>) {
  switch (result.kind) {
    case "success":
      // result.data is available (narrowed)
      return result.data;
    case "error":
      // result.code and result.message are available
      return `Error ${result.code}: ${result.message}`;
    case "loading":
      return "Loading...";
  }
}
```

Always use discriminated unions over boolean flags or optional fields to represent state. Every possible state is explicit, and unhandled variants cause type errors.

## Template Literal Types

Use template literal types for string patterns and to derive types from string constants.

```typescript
type Greeting = `Hello, ${string}`;
const valid: Greeting = "Hello, World"; // OK
const invalid: Greeting = "Hi, World";  // Error: doesn't match pattern

// Distribute over unions
type Size = "small" | "medium" | "large";
type Color = "red" | "blue" | "green";
type SizedColor = `${Size}-${Color}`;
// "small-red" | "small-blue" | ... | "large-green"

// Extract parts with infer
type RemoveMaps<T> = T extends `maps:${infer Rest}` ? Rest : T;
type Test = RemoveMaps<"maps:longitude">; // "longitude"
```

## Type Narrowing

Always narrow types through control flow rather than asserting. Use these narrowing techniques in preference order:

1. **Custom type guards** (type predicates) — best for complex validation
2. **`typeof` guards** — for primitives
3. **`instanceof` guards** — for class instances
4. **Discriminant property checks** — for discriminated unions
5. **`in` operator** — for structural checks
6. **Truthiness/equality narrowing** — for null/undefined removal

### Type Predicates

```typescript
interface Fish { swim: () => void }
interface Bird { fly: () => void }

function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined;
}
```

### Generic Type Guards

```typescript
function isNotNull<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

const values = [1, null, 2, undefined, 3];
const filtered = values.filter(isNotNull); // filtered is number[]
```

### Assertion Functions

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}
```

## Async Patterns

- **Prefer `async`/`await`** over callbacks or `.then()` chains.
- **Prefer async APIs over sync ones:** use `import { readFile } from 'fs/promises'`, not `fs.readFileSync`.
- **Use `Promise.all` and `Promise.race`** for concurrent operations where dependencies allow.
- **Never silently swallow promise rejections.** Always handle `.catch()` with logging or explicit fallback.

## Code Quality

- **Use object destructuring** — prefer `const { name } = user` over `const name = user.name`.
- **Use consistent, descriptive naming.** Avoid obscure abbreviations.
- **Replace magic numbers and strings** with well-named constants.
- **Use `for...of` loops** over index-based `for` loops.
- **Prefer the `ms` package** for time-related configuration instead of manually multiplying by 1000.
- **Assign `Date.now()` to a constant once** and reuse within a function for time consistency.
- **Defer formatting to tooling** — no manual formatting conventions beyond what the type system enforces.

## Logging

- **Never log private information** such as API keys, passwords, or tokens.
- **Always log the error in `.catch()` callbacks** — silent `.catch(() => fallback)` swallows failures and makes debugging impossible.
