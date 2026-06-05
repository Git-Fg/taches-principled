---
name: rust-scaffold
description: Scaffold a new Rust project — lib/bin/lib+bin decision tree, the recommended Cargo.toml template (edition 2024, MSRV, metadata, profile.release), MSRV policy, the 5-rule feature flag playbook, the lib+bin code layout pattern, rustdoc conventions, examples & tests directory, and edition-2021-to-2024 migration. Use when the user says "new Rust project", "scaffold a crate", "Cargo.toml template", "lib + bin", "feature flag design", "edition 2024 migration".
when_to_use: |
  - "Scaffold a new Rust project"
  - "Cargo.toml template"
  - "lib + bin project layout"
  - "Feature flag design"
  - "Pick an MSRV for a new project"
  - "Migrate to edition 2024"
  - "Write rustdoc for my crate"
---

# rust-scaffold

The project-init layer for Rust: scaffolding a new crate, the lib/bin decision,
the Cargo.toml template, MSRV policy, feature flag design, the lib+bin code
layout, rustdoc conventions, and edition migration. For CI/lint/testing setup,
use `rust-quality`. For workspace structure, use `rust-workspace`. For
publishing, use `rust-release`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Scaffold a new Rust project"
- "Cargo.toml template"
- "lib + bin project layout"
- "Feature flag design"
- "Pick an MSRV for a new project"
- "Migrate to edition 2024"
- "Write rustdoc for my crate"
- "Add an example to my crate"

**DO NOT use this skill for:**

## CONTRAST

- NOT for: CI / clippy / nextest / deny — use rust-quality
- NOT for: workspace / member coordination — use rust-workspace
- NOT for: version / publish / deprecation — use rust-release
- This skill is the project-init layer; the others are for ongoing concerns

---

## §2. Reference index

The mechanism content lives in references/. Read the right one before scaffolding the corresponding piece. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/cargo-and-features.md` BEFORE writing a new Cargo.toml or designing features. It teaches the lib-only / bin-only / lib+bin decision tree (with the "default to lib+bin" rule for anything that may grow), the recommended Cargo.toml template (edition 2024, MSRV `1.81`, all the metadata fields, the release profile), the MSRV policy (N-2 stable, the advisory vs enforced distinction with the 1.81 MSRV-aware resolver as the enforcement cutover), and the 5-rule feature flag playbook (additive only, `__internal` prefix, the reqwest pattern, the deprecation cycle). Do not proceed without reading it.

You MUST read `references/lib-bin-rustdoc.md` BEFORE designing the code layout or writing rustdoc. It teaches the lib+bin pattern (logic in `src/lib.rs`, thin `src/main.rs`, with the ripgrep/bat/fd/cargo precedent), the feature-gated binary pattern (bat's `application` feature), the rustdoc conventions (section order: Examples → Errors → Panics → Safety, module-level `//!`, `#![warn(missing_docs)]`), the examples-vs-tests-vs-unit-tests directory structure, and the edition-2021-to-2024 migration playbook (`cargo fix --edition` + the sharp edges: `gen` keyword, `expr_2021`, lifetime capture rules). Do not proceed without reading it.

## §3. Handoff

After scaffolding, the user typically wants to:
- Add tests → stay in this skill (rustdoc reference) or move to `rust-quality` for nextest
- Add CI → `rust-quality` skill
- Set up linting → `rust-quality` skill
- Split into workspace → `rust-workspace` skill
- Publish → `rust-release` skill

Ask the user which they want next.

## §4. Anti-patterns

❌ **`#![deny(warnings)]` in lib.rs** — breaks on transitive-dep warnings
❌ **Defaulting to edition 2015** (the implicit fallback) — always be explicit
❌ **Treating features as "non-negotiable additive"** — Cargo Reference says "should be additive", mutual exclusion is a documented escape hatch
❌ **Implementation in `src/main.rs`** — kills testability
❌ **Picking a new MSRV with no CI matrix to test it**
❌ **Setting `publish = true` (the default) on a `crates.io`-incompatible prototype** — explicitly set `publish = false`
❌ **Missing `[package].description`** — crates.io search ranks by description; without it, you rank zero
❌ **Wildcard `*` version in dependencies** — break reproducibility
❌ **`unsafe` in library code without `#![forbid(unsafe_code)]` or a clear unsafe policy**

## §5. Key sources

- [1] Rust 1.85 release (edition 2024) — https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- [2] Cargo Reference — Specifying Dependencies — https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- [3] Cargo Reference — Features (additive, mutual exclusion) — https://doc.rust-lang.org/cargo/reference/features.html
- [4] API Guidelines — https://rust-lang.github.io/api-guidelines/
- [5] RFC 2055 (edition 2021) — https://rust-lang.github.io/rfcs/2055-isolating-deprecated-lints.html
- [6] RFC 2102 (edition 2024) — https://rust-lang.github.io/rfcs/2102-tool-dependencies.html
- [7] RFC 3537 (MSRV-aware resolver) — https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
