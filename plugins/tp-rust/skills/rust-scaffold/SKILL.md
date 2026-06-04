---
name: rust-scaffold
description: Scaffold a new Rust crate (lib, bin, or both) with modern defaults — edition 2024, MSRV 1.81, resolver 2, cargo-nextest-ready structure, doctests, MSRV-aware lints. Use when the user says "scaffold a Rust crate", "new Rust project", "init a Rust library/binary", "what edition/MSRV to use", "Cargo.toml metadata", "feature flags", "rustdoc conventions".
when_to_use: |
  - "Start a new Rust crate"
  - "What edition / MSRV should I pick?"
  - "Scaffold a Rust lib + bin"
  - "Set up feature flags for a new crate"
  - "How do I document a Rust API with rustdoc?"
---

# rust-scaffold

Initialize a new Rust project the right way. This skill handles single-crate
scaffolding — for multi-crate workspaces, use `rust-workspace` instead.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Scaffold a Rust crate / library / binary"
- "Set up a new Rust project"
- "What edition should I use?"
- "What MSRV should I pick?"
- "Init a Rust binary with subcommands"
- "Create a Rust library that's also usable as a binary"
- "Add doctests to my Rust crate"
- "Configure feature flags"
- "Set up rustdoc with Examples/Errors/Panics"

**DO NOT use this skill for:**
- "Cargo workspace" / "split a crate" / "share dependencies" → `rust-workspace`
- "clippy" / "rustfmt" / "tests are slow" / "set up CI" → `rust-quality`
- "publish" / "version bump" / "release-plz" → `rust-release`

---

## §2. Decision tree: lib-only / bin-only / lib+bin

```
What does the user want?
├─ Library consumed by others (or no clear binary need)
│  → lib-only: `cargo new --lib mycrate`
│
├─ Binary that may grow complex (CLI app, server, tool)
│  → lib+bin: `cargo new --bin mytool` + add src/lib.rs
│  (ripgrep, bat, fd pattern: logic in lib, thin main.rs)
│
└─ Pure single-file script or throwaway
   → bin-only: `cargo new --bin throwaway`
```

**Default recommendation: lib+bin** for anything that may grow. The cost of adding a lib.rs is one file; the cost of refactoring a main.rs into a lib later is much higher.

**Signal to go lib+bin:** the user mentions "test", "reuse", "library", or names subcommands.

---

## §3. Cargo.toml template — recommended variant

```toml
[package]
name = "mycrate"
version = "0.1.0"
edition = "2024"                          # default since Rust 1.85 (Feb 2025)
rust-version = "1.81"                     # MSRV — see §4
description = "One-line description for crates.io search"
license = "MIT OR Apache-2.0"
repository = "https://github.com/you/mycrate"
documentation = "https://docs.rs/mycrate"
readme = "README.md"
keywords = ["mycategory"]                # max 5, lowercase, alphanumeric
categories = ["development-tools"]        # max 5, must exist on crates.io
include = ["src/**/*", "Cargo.toml", "README.md", "LICENSE*"]
exclude = [".github/", "tests/fixtures/"]
publish = true                            # set false for internal-only crates

[lib]
name = "mycrate"                          # default; override if crate and lib name differ
path = "src/lib.rs"

[[bin]]
name = "mytool"
path = "src/main.rs"

[dependencies]
# minimal — add as needed

[dev-dependencies]
# test-only deps

[features]
default = []                              # see §5
# example-feature = ["dep:serde"]

[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"
```

`resolver = "2"` is implied for `edition = "2021"` and `edition = "2024"`. Only set it explicitly for a virtual workspace.

---

## §4. MSRV policy

**Default MSRV for new projects: `rust-version = "1.81"`** (Sept 2024 release). This unlocks:
- MSRV-aware dependency resolver (RFC 3537) — `cargo update` no longer picks newer-than-MSRV versions
- Edition 2024 features (when paired with `edition = "2024"`)
- `let-chains`, `if let` chains (stabilized in 1.88/1.85)
- Modern async, trait improvements

**MSRV policy template:**
1. **Pick N-2 stable** as your MSRV (the version before last + the one before that). E.g., if current stable is 1.88, MSRV is 1.85.
2. **Document the policy** in README and a top-level MSRV comment in Cargo.toml.
3. **CI-test the MSRV** with a separate job using `dtolnay/rust-toolchain@1.81` (see `rust-quality` §2).
4. **MSRV bumps are breaking** if downstream users compile against you. Treat them as a minor-version bump at minimum; many projects (RustCrypto, rust-bitcoin) treat MSRV bumps as major. Ask the user.

**Tools:**
- `cargo +1.81 check` — local MSRV test
- `cargo-msrv find` — automated MSRV detection from your dep tree
- CI matrix (see `rust-quality` §2)

**Important historical note:** the `rust-version` field was added in **Cargo 1.56 (Oct 21, 2021)** as *advisory only*. The MSRV-aware resolver that actually *enforces* MSRV came in **Rust 1.81 (Sept 5, 2024)**. Older advice that says "rust-version is enforced since 1.56" is wrong.

---

## §5. Feature flag playbook

**The rule (per Cargo Reference):** features *should* be additive — they add code, never remove it. Cargo Reference uses the soft "should", not "MUST". The mutual-exclusion escape hatch is documented in Cargo Reference §"Mutually exclusive features" — it is rare but valid when guarded by `compile_error!`.

**5 rules for feature flags:**
1. **Naming:** short, lowercase, no underscores if possible (`serde`, `tls`, `jemalloc`).
2. **Defaults:** keep `default = []` minimal. Users who want a feature should opt in.
3. **Additive only** (with documented mutual-exclusion escape hatch).
4. **Public features ≠ internal features** — use `__internal` prefix (double underscore) for testing-only features that are NOT public API. See reqwest's `__rustls`/`__native-tls` pattern.
5. **Test with the feature matrix:** use `cargo-hack` in CI to test all feature combinations.

**Example internal-feature pattern (from reqwest):**
```rust
// in Cargo.toml
[features]
default = ["default-tls"]
default-tls = ["__native-tls"]
rustls-tls = ["__rustls"]
__rustls = ["dep:rustls", "dep:rustls-pemfile", "dep:rustls-webpki-roots"]
__native-tls = ["dep:openssl"]

// in src/lib.rs
#[cfg(feature = "__rustls")]
pub(crate) mod rustls_impl;
```

The `__` prefix signals "internal, not part of public API, may disappear at any time" (reqwest's documented comment).

**Deprecation cycle:** when removing a feature post-1.0: `warn` in 1.x, `#[deprecated]` in 1.x+1, remove in 1.x+2. Use `#[cfg_attr(feature = "old-feature", deprecated = "use new-feature instead")]` for items.

---

## §6. Lib vs bin design

**Pattern (ripgrep, bat, fd, cargo):** put the work in `src/lib.rs`, keep `src/main.rs` thin.

```rust
// src/main.rs (~30 lines)
use mycrate::{run, Config};
use clap::Parser;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config::parse();
    run(config)
}
```

**Why:** lib code is testable (you can `use mycrate::...` from `tests/`), reusable (downstream users get it), and refactorable (binary code isn't).

**Crate feature gating the binary:** if you want library users to be able to disable the CLI entirely, use a feature:
```toml
[features]
default = ["application"]
application = []
```
Then in `src/main.rs`: `#[cfg(feature = "application")] fn main() { ... }`. bat uses this pattern.

---

## §7. rustdoc conventions

**Every public item gets doc comments.** Use the standard sections:
```rust
/// One-line summary.
///
/// Longer description with motivation, examples, edge cases.
///
/// # Examples
///
/// ```
/// use mycrate::foo;
/// assert_eq!(foo(2), 4);
/// ```
///
/// # Errors
///
/// Returns `Err(MyError::Invalid)` if the input is out of range.
///
/// # Panics
///
/// Panics if `n == 0` (division by zero).
pub fn foo(n: u32) -> Result<u32, MyError> { ... }
```

**Section order:** `# Examples` first, then `# Errors`, `# Panics`, `# Safety` (for `unsafe`).

**Module-level docs** use `//!`:
```rust
//! This crate provides utilities for parsing X.
//!
//! # Quick start
//!
//! ```
//! use mycrate::Parser;
//! let p = Parser::new("input");
//! ```
```

**Deny missing docs in libraries:**
```rust
// src/lib.rs
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]
#![forbid(unsafe_code)]   # if you're safe-Rust
```

**DO NOT use `#![deny(warnings)]`** — it breaks on transitive-dep warnings and you cannot opt out. Use `RUSTFLAGS="-D warnings"` in CI for your crate only (see `rust-quality`).

---

## §8. Examples & tests directory

**Layout:**
```
src/
  lib.rs           # public API
  main.rs          # thin wrapper (if bin)
tests/
  basic.rs         # integration tests (each file = separate test binary)
  errors.rs
examples/
  simple.rs        # runnable with `cargo run --example simple`
benches/           # optional, see rust-quality §8
  parse_bench.rs
```

**Doctests count as tests** — `cargo test` runs them automatically. Use them for the `# Examples` section.

**Snapshot testing with `insta`** for output-heavy functions:
```rust
use insta::assert_snapshot;
assert_snapshot!(render(input));
```
Run `cargo insta review` to accept/reject snapshots.

---

## §9. Edition migration (when working with an existing 2021 crate)

If migrating from edition 2021 to 2024:
1. Run `cargo fix --edition`
2. Bump `edition = "2024"` in Cargo.toml
3. Update rust-version: `rust-version = "1.85"` (edition 2024 requires Rust 1.85+)
4. Run `cargo build` and `cargo test` — address any new lints
5. Read the [Edition Guide for 2024](https://doc.rust-lang.org/edition-guide/rust-2024/index.html) for behavioral changes (RPIT, `gen` blocks, `if let` chains, prelude changes, `unsafe extern` requirements)

**Edition 2024 requires `unsafe extern` blocks** for FFI — `extern "C" { ... }` no longer works inside safe code; must be `unsafe extern "C" { ... }`.

---

## §10. Anti-patterns

❌ **`#![deny(warnings)]` in lib.rs** — breaks on transitive-dep warnings
❌ **Defaulting to edition 2015** (the implicit fallback) — always be explicit
❌ **Treating features as "non-negotiable additive"** — Cargo Reference says "should be additive", mutual exclusion is a documented escape hatch
❌ **Implementation in `src/main.rs`** — kills testability
❌ **Picking a new MSRV with no CI matrix to test it**
❌ **Setting `publish = true` (the default) on a `crates.io`-incompatible prototype** — explicitly set `publish = false`
❌ **Missing `[package].description`** — crates.io search ranks by description; without it, you rank zero
❌ **Wildcard `*` version in dependencies** — break reproducibility
❌ **`unsafe` in library code without `#![forbid(unsafe_code)]` or a clear unsafe policy**

---

## §11. Handoff

After scaffolding, the user typically wants to:
- Add tests → stay in this skill (§7-8) or move to `rust-quality` for nextest
- Add CI → `rust-quality` skill
- Set up linting → `rust-quality` skill
- Split into workspace → `rust-workspace` skill
- Publish → `rust-release` skill

Ask the user which they want next.

---

## §12. Key sources

- [1] Rust 1.85 release (edition 2024) — https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- [2] Cargo Book, `[package]` section — https://doc.rust-lang.org/cargo/reference/manifest.html
- [3] Edition Guide for Rust 2024 — https://doc.rust-lang.org/edition-guide/rust-2024/index.html
- [4] Rust 1.81 release (MSRV-aware resolver) — https://blog.rust-lang.org/2024/09/05/Rust-1.81.0/
- [5] Rust 1.56 release (rust-version field, advisory) — https://releases.rs/docs/1.56.0/
- [6] API Guidelines (MSRV section) — https://rust-lang.github.io/api-guidelines/
- [7] Cargo Reference, Features (the "should be additive" wording) — https://doc.rust-lang.org/cargo/reference/features.html
- [8] rustdoc How-to — https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html
- [9] Real-world patterns: ripgrep (https://github.com/BurntSushi/ripgrep), bat (https://github.com/sharkdp/bat), fd (https://github.com/sharkdp/fd), reqwest (https://github.com/seanmonstar/reqwest)
