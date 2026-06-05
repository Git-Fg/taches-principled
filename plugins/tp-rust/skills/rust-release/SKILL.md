---
name: rust-release
description: Version, changelog, publish, and maintain a Rust crate — Cargo semver (including the contested MSRV policy), changelog tooling (git-cliff, release-please, hand-curated), the cargo publish playbook, the supply-chain maintenance (cargo-vet, Dependabot, RUSTSEC), and feature deprecation. Use when the user says "publish my Rust crate", "version my crate", "set up release-plz", "deprecate a feature", "bump MSRV", "set up cargo-vet".
when_to_use: |
  - "Publish my Rust crate to crates.io"
  - "Set up release-plz for my project"
  - "Bump the version on my crate"
  - "Set up a changelog workflow"
  - "Set up cargo-vet for supply-chain audits"
  - "Deprecate a feature in my 1.x crate"
  - "Bump MSRV safely"
  - "Replace a dependency with a fork"
---

# rust-release

The release/publishing pipeline for a Rust crate: Cargo semver (with the contested
MSRV policy), changelog tooling, the cargo publish playbook, supply-chain
maintenance (cargo-vet, Dependabot, RUSTSEC), and feature deprecation. For the
initial CI/clippy/deny/nextest setup, use `rust-quality`. For project scaffolding,
use `rust-scaffold`. For workspace concerns, use `rust-workspace`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Publish my Rust crate to crates.io"
- "Set up release-plz / cargo-release / smart-release"
- "Bump the version on my crate"
- "Set up a changelog workflow"
- "Set up cargo-vet for supply-chain audits"
- "Deprecate a feature in my 1.x crate"
- "Bump MSRV safely"
- "Replace a dependency with a fork"
- "Set up Dependabot for Rust"
- "Yank a bad release from crates.io"

**DO NOT use this skill for:**

## CONTRAST

- NOT for: scaffold / Cargo.toml / edition / feature design — use rust-scaffold
- NOT for: workspace / member coordination / Cargo.toml inheritance — use rust-workspace
- NOT for: initial CI / clippy / nextest / deny setup — use rust-quality (this skill is the ongoing maintenance side of the supply-chain ladder)
- This skill covers the publish/ongoing-maintenance side; quality and scaffold are the initial-setup side

---

## §2. Reference index

The mechanism content lives in references/. Read the right one before making the corresponding decision. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/versioning-and-changelog.md` BEFORE tagging a release or choosing a changelog generator. It teaches the Cargo semver rules for pre-1.0 vs 1.0+, the SemVer trick for 1.0.0 development, the contested MSRV policy (api-guidelines vs RustCrypto camps, and the 2026 MSRV-aware resolver that obsoletes BurntSushi's 2023 workaround), the workspace lockstep versioning pattern, and the changelog tooling decision tree (git-cliff vs release-please vs hand-curated). Do not proceed without reading it.

You MUST read `references/publishing-and-deps.md` BEFORE your first `cargo publish` and before changing your dependency policy. It teaches the first-publish playbook (build → test → clippy → dry-run → login → publish), the Cargo 1.90+ native workspace publishing, the yank-not-delete rule, the MSRV-aware resolver configuration (`incompatible-rust-versions = "fallback"`), and the vendoring decision. Do not proceed without reading it.

You MUST read `references/supply-chain-maintenance.md` BEFORE changing a dep policy or deprecating a feature. It teaches the cargo-vet certification workflow, the Dependabot config, the RUSTSEC monitoring channels, the bump-vs-replace-vs-live-with decision, the 3-step feature deprecation cycle (post-1.0), the `#[deprecated]` syntax, the pre-1.0 vs post-1.0 discipline, the rustc unstable-feature pattern, and the ADD-vs-REMOVE decision for features. Do not proceed without reading it.

## §3. Handoff to other skills

- **MSRV coordination across a workspace** → `rust-workspace` §5
- **Workspace lockstep versioning** → `rust-workspace` §8
- **Initial cargo-deny / cargo-vet setup** → `rust-quality/references/supply-chain-ladder.md`
- **Initial CI template for cargo publish** → `rust-quality/references/ci-template.md`
- **Feature flag design (additive rules, naming, internal features)** → `rust-scaffold` §5

## §4. Anti-patterns

❌ **Publishing without `--dry-run` first** — always do a dry-run
❌ **Deleting a version from CI history hoping it disappears** — versions are permanent; only yank
❌ **Treating MSRV bumps as always-minor** without asking the user — api-guidelines and RustCrypto disagree
❌ **Using `cargo-release` to publish a workspace without testing the order first** — members publish sequentially, and a mid-publish failure can leave the workspace in a bad state
❌ **Yanking a version because of a "minor" bug fix** — yank is for security/critical issues; for bugs, publish a new patch
❌ **Removing a feature in the same release that deprecates it** — warn → deprecated → removed, not deprecated → removed
❌ **`cargo publish --allow-dirty` without a `--dry-run` first** — `--allow-dirty` lets you publish with uncommitted changes, which is dangerous
❌ **Adding a feature to a 1.x crate without versioning it as a minor bump** — silent feature additions break SemVer
❌ **Forgetting to commit `Cargo.lock` after a security fix** — `--locked` in CI catches this, but only if you commit
❌ **Long-lived crates.io API tokens** — use OIDC trusted publishing when possible

## §5. Key sources

- [1] Cargo Reference — Specifying Dependencies (semver) — https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- [2] Cargo Reference — Publishing on crates.io — https://doc.rust-lang.org/cargo/reference/publishing.html
- [3] API Guidelines (MSRV section) — https://rust-lang.github.io/api-guidelines/
- [4] RFC 3537 (MSRV-aware resolver) — https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- [5] release-plz docs — https://release-plz.dev/docs/
- [6] git-cliff docs — https://git-cliff.org/docs/
- [7] cargo-vet — https://mozilla.github.io/cargo-vet/
- [8] cargo-deny — https://embarkstudios.github.io/cargo-deny/
- [9] cargo-semver-checks — https://github.com/obi1kenobi/cargo-semver-checks
- [10] Mozilla supply-chain audits — https://github.com/mozilla/supply-chain
- [11] Real-world: serde, tokio, axum, cargo, release-plz, cargo-smart-release, gtk-rs, fuel-core
