---
name: rust-workspace
description: Decide on and structure a Rust workspace — single-crate vs workspace vs multi-workspace decision tree, virtual workspace template, the workspace inheritance playbook (1.64+), Cargo.lock policy, MSRV coordination across members, cross-crate patterns (internal features, path deps, shared dev-deps, feature unification), and workspace publishing. Use when the user says "set up a Cargo workspace", "split into a workspace", "share deps across crates", "workspace inheritance", "coordinate MSRV across members", "publish a workspace".
when_to_use: |
  - "Set up a Cargo workspace"
  - "Split my project into a workspace"
  - "Share dependencies across crates"
  - "Use workspace inheritance"
  - "Coordinate MSRV across workspace members"
  - "Publish a workspace to crates.io"
  - "Set up internal feature flags"
---

# rust-workspace

The workspace structure layer: when to split into a workspace, the templates
(virtual / single-package / multi-workspace), workspace inheritance, the
`Cargo.lock` policy, MSRV coordination, cross-crate patterns, and workspace
publishing. For project scaffolding, use `rust-scaffold`. For CI/lint/quality
setup, use `rust-quality`. For release/publishing pipeline, use `rust-release`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Set up a Cargo workspace"
- "Split my project into a workspace"
- "Share dependencies across crates"
- "Use workspace inheritance"
- "Coordinate MSRV across workspace members"
- "Publish a workspace to crates.io"
- "Add an internal feature flag pattern"
- "Should I split my project into a workspace?"

**DO NOT use this skill for:**

## CONTRAST

- NOT for: scaffold a single project / Cargo.toml layout / edition — use rust-scaffold
- NOT for: CI / clippy / lints / testing — use rust-quality
- NOT for: version / publish / deprecation — use rust-release
- This skill is the workspace structure layer; the others are per-crate concerns

---

## §2. Reference index

The mechanism content lives in references/. Read the right one before making the corresponding decision. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/workspace-decisions.md` BEFORE splitting a project into a workspace or restructuring an existing one. It teaches the single-crate vs workspace vs multi-workspace decision tree (with the "should you NOT split" anti-signals), the virtual workspace template (the recommended default — no `[package]` in the root, `[workspace.package]` for shared metadata, `[workspace.dependencies]` for shared deps, `[workspace.lints]` for centralized lints), and the workspace inheritance playbook (1.64+) including the `additive-defaults` pitfall (cargo #12162). Do not proceed without reading it.

You MUST read `references/lockfile-and-cross-crate.md` BEFORE publishing a workspace or adding a member crate. It teaches the `Cargo.lock` commit policy (commit for apps/binaries, don't commit for pure libraries), the MSRV coordination across members (workspace MSRV = most restrictive member's MSRV, with the override warning), the internal features pattern (`__` prefix, the reqwest pattern), the path-dependency auto-detection, the shared dev-dependencies inheritance, the feature unification behavior, and the workspace publishing policy (Cargo 1.90+ native `cargo publish --workspace`, internal-only crates with `publish = false`). Do not proceed without reading it.

## §3. Handoff to other skills

- **MSRV coordination** is workspace concern → covered here
- **Workspace lockstep versioning** (`workspace.package.version = "0.1.0"`, all members bump together) → `rust-release/references/versioning-and-changelog.md`
- **Workspace CI matrix** → `rust-quality/references/ci-template.md`
- **Workspace lints** (centralized `workspace.lints`) → `rust-quality/references/clippy-and-fmt.md`

## §4. Anti-patterns

❌ **Premature workspace split** — wait for a real signal (binary+lib, multi-bin, shared types >100 lines)
❌ **Using `path = "..."` in a published crate** — breaks for downstream users
❌ **Sharing `dev-dependencies` at workspace level when members are heterogeneous** (one bin, one lib) — the binary's test deps pollute the lib's tests
❌ **Putting business logic in the workspace root's `src/lib.rs`** instead of a proper member
❌ **Ignoring feature unification warnings** — they often indicate real coupling problems
❌ **Overriding `default-features = false` on a workspace-inherited dep** — the additive-defaults pitfall (cargo #12162). Use the feature-wrapper pattern from §4 of the inheritance reference.
❌ **Committing `Cargo.lock` for a workspace of pure libraries** — let each lib consumer resolve independently
❌ **Nested workspace dirs when flat would do** — adds boilerplate without benefit unless you have genuinely independent release cadences

## §5. Key sources

- [1] Cargo Book — Workspaces — https://doc.rust-lang.org/cargo/reference/workspaces.html
- [2] Cargo Book — `[workspace]` section — https://doc.rust-lang.org/cargo/reference/manifest.html#the-workspace-section
- [3] matklad "Large Rust Workspaces" — https://matklad.github.io/2022/09/26/large-rust-workspaces.html
- [4] Cargo #12162 (additive-defaults pitfall) — https://github.com/rust-lang/cargo/issues/12162
- [5] RFC 2282 (workspace inheritance) — https://rust-lang.github.io/rfcs/2282-workspace-inheritance.html
- [6] Real-world: tokio, axum, ripgrep, cargo, rust-analyzer, deno
