# Workspace Decisions and Anatomy

Reference for the single-crate vs workspace decision, the three workspace templates (virtual, single-package, multi-workspace), and the workspace inheritance playbook. Read it before splitting a project into a workspace or restructuring an existing one.

## §1. Decision: single project vs workspace vs multi-workspace

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

## §2. Virtual workspace (recommended default)

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

## §3. Workspace inheritance playbook (1.64+)

Member crates inherit `[workspace.package]`, `[workspace.dependencies]`, and `[workspace.lints]` via the `field.workspace = true` syntax:

```toml
# crates/foo/Cargo.toml
[package]
name = "foo"
version.workspace = "true"
edition.workspace = "true"
license.workspace = "true"
repository.workspace = "true"

[dependencies]
serde = { workspace = "true" }
tokio = { workspace = true, features = ["macros"] }   # add features on top

[dev-dependencies]
# use warn for pedantic so the project still builds, but CI can deny it
```

**Inheritance rules:**
- `version.workspace = "true"` — inherits `version` from `[workspace.package]`
- `serde = { workspace = "true" }` — uses the workspace version spec
- `tokio = { workspace = true, features = [...] }` — adds features on top of the workspace spec
- `default-features = false` per member is fine, the workspace default is overridable
- A member that needs a different version pins explicitly: `serde = { version = "2" }`

**Cargo 1.84+ additive defaults:** since the `additive-defaults` pitfall, be careful when mixing `default-features = false` in a member with workspace-default features. Pin explicitly when in doubt.
