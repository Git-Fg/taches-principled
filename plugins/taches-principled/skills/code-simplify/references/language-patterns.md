# Language-Specific Simplification Patterns

> Before/after examples with WHY notes for each supported language.
> Use these as reference during the Simplify stage of the pipeline.

---

## JavaScript / TypeScript

### Replace if/else chains with ternary or early return

**Before:**
```ts
function getStatus(user) {
  if (user.isAdmin) {
    return 'admin';
  } else if (user.isModerator) {
    return 'moderator';
  } else {
    return 'user';
  }
}
```

**After (early return):**
```ts
function getStatus(user) {
  if (user.isAdmin) return 'admin';
  if (user.isModerator) return 'moderator';
  return 'user';
}
```

**WHY:** Early returns flatten the control flow, removing nested scopes and the redundant `else` keyword. Each branch stands alone and is easier to reorder or extract later.

---

### Replace switch with object lookup

**Before:**
```ts
function getColorName(code) {
  switch (code) {
    case 1: return 'red';
    case 2: return 'green';
    case 3: return 'blue';
    default: return 'unknown';
  }
}
```

**After:**
```ts
const COLORS: Record<number, string> = {
  1: 'red',
  2: 'green',
  3: 'blue',
};

function getColorName(code: number): string {
  return COLORS[code] ?? 'unknown';
}
```

**WHY:** Object/Map lookups separate data from logic. Adding a new case doesn't require touching the function body. TypeScript narrows the return type automatically. The `??` operator makes the default explicit.

---

### Flatten async/await chains, remove unnecessary Promise wrapper

**Before:**
```ts
async function loadData() {
  return new Promise(async (resolve) => {
    const result = await fetch('/api/data');
    const json = await result.json();
    resolve(json);
  });
}
```

**After:**
```ts
async function loadData() {
  const result = await fetch('/api/data');
  return result.json();
}
```

**WHY:** An `async` function already returns a promise. Wrapping it in `new Promise()` adds an unnecessary layer, complicates error handling (rejections inside the callback are silently swallowed), and blocks the promise constructor anti-pattern detection.

---

### Replace .forEach() with for...of

**Before:**
```ts
items.forEach((item) => {
  if (item.isActive) {
    process(item);
  }
});
```

**After:**
```ts
for (const item of items) {
  if (item.isActive) {
    process(item);
  }
}
```

**WHY:** `for...of` supports `break`, `continue`, `return`, and `await` inside the loop body. `.forEach()` does not — control flow keywords inside the callback behave unexpectedly or cause lint errors. `for...of` is also faster and works with any iterable, not just arrays.

---

### Replace nested ternaries with if/else or switch

**Before:**
```ts
const label = count === 0 ? 'none'
  : count === 1 ? 'one'
  : count < 10 ? 'few'
  : count < 100 ? 'many'
  : 'too many';
```

**After:**
```ts
function getLabel(count: number): string {
  if (count === 0) return 'none';
  if (count === 1) return 'one';
  if (count < 10) return 'few';
  if (count < 100) return 'many';
  return 'too many';
}
```

**WHY:** Nested ternaries are terse but hard to debug, step through, or annotate with types. They also break under formatters that flatten them into a single unreadable line. Early-return if/else is equally concise and debuggable.

---

## Python

### Dict dispatch over if/elif/else chains

**Before:**
```python
def handle_command(cmd, payload):
    if cmd == "start":
        start_handler(payload)
    elif cmd == "stop":
        stop_handler(payload)
    elif cmd == "restart":
        restart_handler(payload)
    else:
        raise ValueError(f"Unknown command: {cmd}")
```

**After:**
```python
def handle_command(cmd, payload):
    handlers = {
        "start": start_handler,
        "stop": stop_handler,
        "restart": restart_handler,
    }
    handler = handlers.get(cmd)
    if handler is None:
        raise ValueError(f"Unknown command: {cmd}")
    handler(payload)
```

**WHY:** Dict dispatch decouples command registration from dispatch logic, making it trivial to add/remove commands without touching the function body. It also enables runtime registration and introspection.

---

### Walrus operator for repeated evaluation

**Before:**
```python
result = expensive_function()
if result is not None:
    process(result)
    log(result)
```

**After:**
```python
if (result := expensive_function()) is not None:
    process(result)
    log(result)
```

**WHY:** The walrus operator (`:=`) binds the value in the condition expression, eliminating the separate assignment line and preventing scope leak. The variable is only available inside the block, making the intent clearer.

---

### List comprehensions over filter+map

**Before:**
```python
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
squared = list(map(lambda x: x ** 2, evens))
```

**After:**
```python
numbers = [1, 2, 3, 4, 5, 6]
squared_evens = [x ** 2 for x in numbers if x % 2 == 0]
```

**WHY:** A single list comprehension reads left-to-right (transform, iteration, filter) and avoids lambda boilerplate. It's faster, more readable, and keeps the intermediate list from being materialized.

---

## Go

### Error-if chains to early returns

**Before:**
```go
func processFile(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return fmt.Errorf("read: %w", err)
    } else {
        parsed, err := parse(data)
        if err != nil {
            return fmt.Errorf("parse: %w", err)
        } else {
            result, err := transform(parsed)
            if err != nil {
                return fmt.Errorf("transform: %w", err)
            } else {
                return save(result)
            }
        }
    }
}
```

**After:**
```go
func processFile(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return fmt.Errorf("read: %w", err)
    }
    parsed, err := parse(data)
    if err != nil {
        return fmt.Errorf("parse: %w", err)
    }
    result, err := transform(parsed)
    if err != nil {
        return fmt.Errorf("transform: %w", err)
    }
    return save(result)
}
```

**WHY:** Go's `if err != nil` pattern is idiomatic, but nesting them creates a rightward drift that hides the happy path. Flat early returns keep the success path in a straight line down the left margin.

---

### Named functions over bool parameters

**Before:**
```go
func connect(timeout int, tls bool) (*Conn, error) {
    if tls {
        return tlsConnect(timeout)
    }
    return plainConnect(timeout)
}

// Call site
conn, err := connect(30, true)
```

**After:**
```go
func connect(timeout int) (*Conn, error) {
    return plainConnect(timeout)
}

func connectTLS(timeout int) (*Conn, error) {
    return tlsConnect(timeout)
}

// Call site
conn, err := connectTLS(30)
```

**WHY:** Boolean parameters hide meaning at the call site — `true` tells you nothing. Named functions make the caller's intent self-documenting and allow each variant to evolve independently with its own documentation and validation.

---

## Ruby

### Symbol-to-proc (&:method)

**Before:**
```ruby
names = users.map { |user| user.name }
total = numbers.reduce(0) { |sum, n| sum + n }
```

**After:**
```ruby
names = users.map(&:name)
total = numbers.reduce(0, &:+)
```

**WHY:** Symbol-to-proc eliminates the block boilerplate and signals a simple delegation. It's more idiomatic Ruby and makes the collection pipeline read like a declarative transformation.

---

### Safe navigation (&.) over nil checks

**Before:**
```ruby
if user && user.profile && user.profile.address
  city = user.profile.address.city
end
```

**After:**
```ruby
city = user&.profile&.address&.city
```

**WHY:** Safe navigation (`&.`) short-circuits on `nil` without nesting, making deep access chains readable in a single line. It expresses the same guard logic without the visual noise of intermediate checks.
