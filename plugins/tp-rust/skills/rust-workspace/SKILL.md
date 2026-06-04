---
name: rust-workspace
description: Manage a Cargo workspace — decide when to split a single project, structure members, share dependencies via workspace inheritance (1.64+), coordinate MSRV across crates, and use cross-crate patterns like internal features. Use when the user says "split into a workspace", "add a member crate", "share dependencies across crates", "set up a Cargo workspace", "workspace inheritance", "internal types", "publish a subset of crates".
when_to_use: |
  - "Should I split this into a workspace?"
  - "Add a member crate to my workspace"
  - "Share dependencies across multiple crates"
  - "Set up workspace inheritance"
  - "How do I coordinate MSRV across a workspace?"
  - "Internal types / __internal feature pattern"
---

# rust-workspace

Multi-crate Rust workspace decisions. For single-crate scaffolding, use
`rust-scaffold` instead.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Split this project into a workspace"
- "Add a member crate to my workspace"
- "Share dependencies across multiple crates"
- "Set up a Cargo workspace"
- "Use workspace inheritance"
- "How do I publish a subset of crates?"
- "Coordinate MSRV across a workspace"
- "Internal types / `__internal` feature pattern"
- "Convert a single crate into a workspace"
- "Share dev-dependencies across the workspace"

## CONTRAST

- NOT for: scaffolding a single crate — use rust-scaffold
- NOT for: CI / clippy / test / audit setup — use rust-quality
- NOT for: publishing or version bumping (workspace lockstep versioning is a cross-skill handoff to rust-release) — use rust-release
- This skill is for multi-crate workspace structure; quality and release are separate skills

---

## §2. Decision: single project vs workspace vs multi-workspace

```
Are you a single binary with no reuse need?
├─ YES → single crate (use rust-scaffold)
└─ NO
   ├─ Do you have a binary + library split, OR multiple binaries, OR
   │  shared types used by 2+ crates, OR feature-flag complexity?
   │  → single Cargo workspace (this skill)
   │
   └─ Are you a monorepo with independent release cadences
      (e.g., compiler + std + tools that ship separately)?
      → multi-workspace (nested Cargo.toml roots)
```

**Signals you should split (even if you don't think you need to):**
- Your `src/main.rs` is >500 lines and does more than wire-up
- Two binaries in `src/bin/` are sharing logic by copy-paste
- You want to test internal modules in isolation but they pull in heavy CLI deps
- Build time is dominated by transitive deps you don't need everywhere
- You have `#[cfg(feature = "...")]` complexity that's hard to reason about

**Signals you should NOT split:**
- You have one binary and no library users
- Your "shared code" is <100 lines
- You have <3 member candidates

Premature workspace split doubles CI cost and slows incremental builds. Wait for the signal.

---

## §3. Workspace anatomy — three templates

### 3.1 Virtual workspace (recommended default)

Root `Cargo.toml`:
```toml
[workspace]
resolver = "2"                            # always explicit in virtual workspaces
members = [
    "crates/foo",
    "crates/bar",
    # OR use glob:
    # members = ["crates/*"]
]

[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.81"
license = "MIT OR Apache-2.0"
repository = "https://github.com/you/myworkspace"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
anyhow = "1"
tracing = "0.1"
# see §4 for inheritance rules

[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
# use warn for pedantic so the project still builds, but CI can deny it
```

**No `[package]` in the root.** This is the cleanest pattern — the root is a pure coordination layer.

### 3.2 Single-package-with-members (root is also a crate)

Use when your root is itself a publishable crate (e.g., cargo itself does this):
```toml
[package]
name = "myroot"
version.workspace = "0.1.0"
edition.workspace = "2024"

[dependencies]
serde = { workspace = true }

[workspace]
members = ["crates/*"]
```

### 3.3 Hybrid (root is virtual but shares its own lib)

Less common. Just declare a package at root AND a workspace:
```toml
[package]
name = "root"
version = "0.1.0"
edition = "2024"

[lib]
path = "src/lib.rs"

[dependencies]
# ...

[workspace]
members = ["crates/*"]
```

---

## §4. Workspace inheritance playbook (1.64+)

The `workspace.dependencies` and `workspace.package` blocks centralize metadata so each member inherits from the root.

### 4.1 Member-side syntax
```toml
# crates/foo/Cargo.toml
[package]
name = "foo"
version.workspace = "true"          # inherits workspace.package.version
edition.workspace = "true"          # inherits workspace.package.edition
license.workspace = "true"

[dependencies]
serde = { workspace = true }         # inherits workspace.dependencies.serde
tokio = { workspace = true, features = ["macros"] }  # can override features
```

### 4.2 What CAN be inherited (as of Rust 1.84+)
- `[package]`: `version`, `edition`, `rust-version`, `authors`, `description`,
  `documentation`, `homepage`, `repository`, `license`, `license-file`, `keywords`,
  `categories`, `publish`, `include`, `exclude`
- `[dependencies]` and `[dev-dependencies]` (full version+features)
- `[features]` entries can reference `workspace` features
- `[lints]` (since 1.74)

### 4.3 What CANNOT be inherited
- `[package].name` (must be unique per crate)
- Per-feature dependencies that diverge from the workspace dep
- `[bin]`, `[[example]]`, `[[bench]]` (member-specific)

### 4.4 The additive-defaults pitfall (cargo #12162)

**Unfixed as of 2026-06.** When a workspace dep has `default-features = true` and a member wants `default-features = false`, inheritance doesn't work cleanly. Workaround: declare the dep with a feature wrapper in workspace, then members toggle the wrapper:

```toml
# workspace.dependencies
serde = { version = "1", default-features = false }    # global default = no features

# member Cargo.toml — wants default features
[dependencies]
serde = { workspace = true, features = ["std", "derive"] }
```

Or vice versa: declare the dep in the member directly instead of inheriting. Don't try to override `default-features` on a workspace-inherited dep.

### 4.5 Migration steps
1. Add `[workspace.package]` and `[workspace.dependencies]` blocks
2. In each member, replace version literals with `version.workspace = "true"`
3. Replace dep version specs with `{ workspace = true }`
4. Run `cargo check --workspace` and `cargo test --workspace`
5. CI-test each member independently after the migration

---

## §5. Lockfile & MSRV coordination

### 5.1 Cargo.lock
- **Always commit `Cargo.lock` for applications and workspaces with binaries.**
- **Do NOT commit `Cargo.lock` for libraries distributed individually to crates.io** (every member publishes its own lock state).
- For a workspace with one library + one binary, commit the lock (the binary needs it).
- Use `--locked` in CI to catch forgotten lock updates.

### 5.2 MSRV coordination across members
- Set `rust-version` in `[workspace.package]` — all members inherit
- The most restrictive member's MSRV is the workspace's effective MSRV
- If member A needs Rust 1.85 and member B is fine with 1.70, the workspace is effectively 1.85
- Cargo's MSRV-aware resolver (1.81+) picks deps compatible with the WORKSPACE MSRV
- If one member really needs an older dep, it must override the workspace `rust-version` in its own `[package]` — but this triggers a warning

---

## §6. Cross-crate patterns

### 6.1 Internal features (`__` prefix)
For code shared between public features but not part of the public API:
```toml
# reqwest's pattern
[features]
default = ["default-tls"]
default-tls = ["__native-tls"]
rustls-tls = ["__rustls"]
__rustls = ["dep:rustls", "dep:rustls-pemfile", "dep:rustls-webpki-roots"]
__native-tls = ["dep:openssl"]
```

The `__` prefix signals "internal, may disappear at any time, not part of public API".

### 6.2 Path dependencies (workspace members)
```toml
[dependencies]
my-shared-types = { path = "../shared-types" }
```
Auto-detected by Cargo for workspace members. Do NOT use `path` deps in published crates (breaks for downstream users who don't have the same filesystem layout).

### 6.3 Shared dev-dependencies
```toml
# workspace.dev-dependencies
pretty_assertions = "1"
insta = "1"
```
Members inherit these for tests without needing to redeclare.

### 6.4 Feature unification
When member A enables feature F and member B does not, the workspace compiles with F. This is a Cargo-wide behavior, not a workspace-specific one. Watch for:
- Optional deps in member A that are pulled in because member B enables a feature
- Compile-time bloat from features you didn't ask for in this binary

To isolate: build a specific member with `cargo build -p mymember` (uses only that member's features) or `cargo build -p mymember --no-default-features`.

### 6.5 Proc-macro strategy
Put proc-macro crates in a sibling workspace member with `proc-macro = true`:
```toml
# crates/my-derive/Cargo.toml
[package]
name = "my-derive"
version.workspace = "true"
edition.workspace = "true"

[lib]
proc-macro = true
```
The `proc-macro = true` line (in `[lib]`, not `[package]`) makes it build as a proc-macro crate. Then downstream members depend on it normally.

---

## §7. Real-world workspace patterns

| Repo | Layout | Members | Inheritance | Notable trick | Source |
|---|---|---|---|---|---|
| tokio | flat | 6+ (tokio, tokio-util, tokio-stream, etc.) | yes | workspace.lints centralized, separate `loom` member for concurrency tests | github.com/tokio-rs/tokio |
| axum | flat | a few | yes | macros in separate member, versioned lockstep | github.com/tokio-rs/axum |
| ripgrep | flat (per matklad) | 9 (crates/core, crates/grep, etc.) | partial | lib+bin in each member, `pcre2 = ["grep/pcre2"]` feature unblock | github.com/BurntSushi/ripgrep |
| serde | n/a (single-crate) | n/a | n/a | uses serde_derive as a separate proc-macro crate on crates.io | github.com/serde-rs/serde |
| cargo | nested workspaces | many (resolver, test, etc.) | yes | multiple sub-workspaces, hand-rolled publish.py | github.com/rust-lang/cargo |
| rust-analyzer | flat (per matklad's recommendation) | many | yes | single Cargo.toml at root, all crates in subdirs | github.com/rust-lang/rust-analyzer |
| deno | flat | 50+ (cli, core, ext/*, runtime) | yes | massive workspace, conditional feature flags | github.com/denoland/deno |

**Layout debate:** matklad argues for "flat" (one root Cargo.toml, all crates in subdirs) over "nested" (Cargo.toml in every subdir). Both work; flat is easier to grep.

---

## §8. Workspace publishing

### 8.1 Cargo 1.90 native workspace publishing (Sept 2025)
New `cargo workspace publish` command. Limited real-world adoption as of 2026-06. Use it for greenfield projects; existing projects should stick with release-plz.

### 8.2 release-plz (recommended for new projects)
```toml
# release-plz.toml
[workspace]
semver_check = true
publish_allow_dirty = false
tag_name = "v{{version}}"
```

release-plz subsumes cargo-release + git-cliff + cargo-semver-checks. It's the strongest default for new workspaces. See `rust-release` for the full playbook.

### 8.3 Internal crates (publish = false)
For crates that should never be published:
```toml
[package]
name = "internal-types"
publish = false
# workspace member, but excluded from `cargo publish --workspace`
```

---

## §9. Handoff to other skills

- **MSRV coordination** is workspace concern → covered here
- **Workspace lockstep versioning** (`workspace.package.version = "0.1.0"`, all members bump together) → `rust-release` §6
- **Workspace CI matrix** → `rust-quality` §2
- **Workspace lints** (centralized `workspace.lints`) → `rust-quality` §3

---

## §10. Anti-patterns

❌ **Premature workspace split** — wait for a real signal (binary+lib, multi-bin, shared types >100 lines)
❌ **Using `path = "..."` in a published crate** — breaks for downstream users
❌ **Sharing `dev-dependencies` at workspace level when members are heterogeneous** (one bin, one lib) — the binary's test deps pollute the lib's tests
❌ **Putting business logic in the workspace root's `src/lib.rs`** instead of a proper member
❌ **Ignoring feature unification warnings** — they often indicate real coupling problems
❌ **Overriding `default-features = false` on a workspace-inherited dep** — the additive-defaults pitfall (cargo #12162). Use the feature-wrapper pattern from §4.4
❌ **Committing `Cargo.lock` for a workspace of pure libraries** — let each lib consumer resolve independently
❌ **Nested workspace dirs when flat would do** — adds boilerplate without benefit unless you have genuinely independent release cadences

---

## §11. Key sources

- [1] Cargo Book — Workspaces — https://doc.rust-lang.org/cargo/reference/workspaces.html
- [2] Cargo Book — `[workspace]` section — https://doc.rust-lang.org/cargo/reference/manifest.html#the-workspace-section
- [3] matklad "Large Rust Workspaces" — https://matklad.github.io/2022/09/26/large-rust-workspaces.html
- [4] Cargo #12162 (additive-defaults pitfall) — https://github.com/rust-lang/cargo/issues/12162
- [5] RFC 2282 (workspace inheritance) — https://rust-lang.github.io/rfcs/2282-workspace-inheritance.html
- [6] Real-world: tokio, axum, ripgrep, cargo, rust-analyzer, deno (see §7 table)
- [7] Tweag "Workspace Publishing" — https://www.tweag.io/blog/2024-03-07-workspace-publishing/
