---
name: rust-quality
description: Set up the Rust quality pipeline — CI with clippy, faster test runner (nextest), coverage reporting, dependency auditing, and the supply-chain ladder. Use when the user says "set up CI for Rust", "configure clippy", "speed up tests", "add coverage", "audit dependencies", "set up supply-chain", "add benchmarks", "lint as error in CI".
when_to_use: |
  - "Set up CI for my Rust project"
  - "Configure clippy for a library"
  - "My tests are slow — switch to nextest"
  - "Add code coverage to my Rust crate"
  - "Audit my Rust dependencies"
  - "Set up cargo-deny for licenses and advisories"
  - "Add benchmarks with criterion"
---

# rust-quality

The Rust quality pipeline: CI, linting, testing, coverage, audit, benchmarks,
and the supply-chain ladder. For project scaffolding, use `rust-scaffold`. For
release/publishing, use `rust-release`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Set up CI for my Rust project"
- "Configure clippy for a library"
- "Tests are slow — switch to nextest"
- "Add code coverage to my Rust project"
- "Audit my dependencies"
- "Set up cargo-deny for licenses and advisories"
- "Add a supply-chain audit to CI"
- "Cross-platform CI matrix for Rust"
- "Add benchmarks (criterion)"
- "Speed up CI build times"
- "Lint as error in CI"

**DO NOT use this skill for:**

## CONTRAST

- NOT for: scaffold / Cargo.toml / edition — use rust-scaffold
- NOT for: split into workspace / share deps — use rust-workspace
- NOT for: publish / version / changelog — use rust-release (the supply-chain ladder is a cross-skill handoff — quality sets it up, release maintains it)
- This skill covers CI / clippy / tests / coverage; release and scaffold are separate skills

---

## §2. Reference index

The mechanism content lives in references/. Read the right one before setting up the corresponding piece. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/ci-template.md` BEFORE writing `.github/workflows/ci.yml`. It teaches the canonical 6-job CI (format → test → lint → doc → audit → msrv), the concurrency cancel-in-progress rule (PR branches only, never main), the `RUSTFLAGS: "-D warnings"` discipline, the `actions-rust-lang/setup-rust-toolchain` alternative, and the Forgejo/Gitea compatibility note. Do not proceed without reading it.

You MUST read `references/clippy-and-fmt.md` BEFORE configuring per-project lint policy. It teaches the per-project `clippy.toml` (MSRV for MSRV-aware lints, `disallowed-types`), the `rustfmt.toml` configuration, the library-level pragmas (`#![warn(missing_docs)]`, `#![forbid(unsafe_code)]`), the lint group selection per use case (binary / library / embedded / no_std), and the `#![deny(warnings)]` anti-pattern. Do not proceed without reading it.

You MUST read `references/testing-and-coverage.md` BEFORE switching test runners or adding coverage. It teaches the cargo-nextest adoption criteria (>200 tests OR CI > 5 min), the `.config/nextest.toml` profile (default + ci), the cargo-hack feature matrix pattern, cargo-llvm-cov over cargo-tarpaulin, line vs branch coverage scope, and the Criterion/divan/iai-callgrind benchmark toolkit. Do not proceed without reading it.

You MUST read `references/supply-chain-ladder.md` BEFORE publishing a crate or hardening a security-critical project. It teaches the 4-stage ladder (cargo-audit → cargo-deny → cargo-vet → Dependabot/RSS), the verified 2026 `deny.toml` schema (with the 0.18+ removed-key callout), the cargo-vet bootstrap from Mozilla + Google audits, and the SBOM path. Do not proceed without reading it.

You MUST read `references/dev-experience.md` BEFORE optimizing local dev loops or adding more tooling. It teaches the bacon file-watcher, the `.cargo/config.toml` build-speed tweaks (mold, sccache), the `rust-toolchain.toml` pinning, the CI cache, and the consolidated tool matrix. Do not proceed without reading it.

## §3. Handoff to other skills

- **Initial setup of clippy/CI/deny/nextest** → this skill
- **Ongoing supply-chain maintenance + new audit policies** → `rust-release/references/supply-chain-maintenance.md`
- **Benchmarking over time + performance regression tracking** → `rust-release` (CI integration for `cargo bench` / bencher.dev)
- **Audit findings in a specific dependency** → `rust-release` (yank/upgrade/replace)

## §4. Anti-patterns

❌ `#![deny(warnings)]` in lib.rs — breaks on transitive-dep warnings
❌ Using `cargo-deny` schema from a 2024 or earlier tutorial — the `vulnerability` and `unlicensed` keys are REMOVED in 0.18+
❌ Running `cargo audit` and `cargo deny` redundantly — `cargo deny` subsumes `cargo audit`
❌ `--no-fail-fast` in nextest — defeats the point
❌ `cargo test --release` — slower build, no perf signal; use a benchmark harness instead
❌ `RUSTFLAGS=-D warnings` for workspace members — denies warnings in transitive deps too
❌ Coverage target on day 1 — measure first, set a target after 2-3 months of data
❌ Mutation testing on every PR — too slow; run weekly
❌ Pre-optimizing benchmarks — only add when you have a perf-sensitive path
❌ Skipping `cargo fmt --check` in CI — formatting drift is annoying but cheap to prevent

## §5. Key sources

- [1] cargo-nextest benchmarks (1.4-3.4× faster) — https://nexte.st/docs/benchmarks/
- [2] cargo-deny config (current 0.19+ schema) — https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- [3] cargo-deny template — https://github.com/EmbarkStudios/cargo-deny/blob/main/deny.template.toml
- [4] cargo-vet introduction — https://mozilla.github.io/cargo-vet/
- [5] cargo-vet audit criteria — https://mozilla.github.io/cargo-vet/audit-criteria.html
- [6] rust-project-primer CI chapter — https://rustprojectprimer.com/ci/github.html
- [7] rust-project-primer audit chapter — https://rustprojectprimer.com/checks/audit.html
- [8] Swatinem/rust-cache — https://github.com/Swatinem/rust-cache
- [9] dtolnay/rust-toolchain — https://github.com/dtolnay/rust-toolchain
- [10] actions-rust-lang/setup-rust-toolchain — https://github.com/actions-rust-lang/setup-rust-toolchain
- [11] Corrode blog "Tips for Faster Rust CI Builds" — https://corrode.dev/blog/tips-for-faster-ci-builds/
- [12] Mozilla supply-chain audits — https://github.com/mozilla/supply-chain
- [13] Google open-sourcing their Rust crate audits (2023) — https://opensource.googleblog.com/2023/05/open-sourcing-our-rust-crate-audits.html
- [14] JetBrains "Faster Rust Tests With cargo-nextest" (2026-05) — https://blog.jetbrains.com/rust/2026/05/01/faster-rust-tests-with-cargo-nextest/
- [15] Criterion.rs — https://github.com/bheisler/criterion.rs
