# Clippy and rustfmt Policy

Reference for per-project Clippy and rustfmt configuration. Read it before setting up the lint policy for a new Rust project.

## §1. Per-project `clippy.toml`

```toml
# Set MSRV for MSRV-aware lints — otherwise clippy will suggest features
# only available in newer Rust.
msrv = "1.81"

# Avoid suggestions that pull in heavy deps.
disallowed-types = [
    # { path = "std::sync::Mutex", reason = "use parking_lot::Mutex" },
]
```

## §2. Per-project `rustfmt.toml`

```toml
edition = "2024"            # match your Cargo.toml edition
max_width = 100
imports_granularity = "Crate"  # nightly-only; falls back gracefully on stable
```

## §3. Library-level pragmas (`src/lib.rs`)

```rust
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]
#![forbid(unsafe_code)]   # if you're a safe-Rust project
// DO NOT use #![deny(warnings)] — see §5
```

## §4. Lint group selection per use case

- **Binary project:** `cargo clippy -- -D warnings` (defaults only)
- **Library project:** `cargo clippy --all-targets -- -W clippy::pedantic -W clippy::nursery -A clippy::missing-errors-doc -D warnings`
- **Embedded / no_std:** also enable `#![warn(clippy::no_std)]` and the `clippy::cargo` group

## §5. The `#![deny(warnings)]` anti-pattern

**DO NOT** use `#![deny(warnings)]` in `lib.rs`. It makes your crate fail to compile when a transitive dep emits a new warning (which is outside your control). Use `RUSTFLAGS: "-D warnings"` in CI for your crate only.
