---
name: rust-release
description: Manage the Rust release lifecycle — semver and MSRV policy, changelog generation, publishing to crates.io (including yank and ownership transfer), and supply-chain hardening with vet and dependabot. Use when the user says "publish to crates.io", "bump version", "set up release-plz", "yank a version", "deprecate a feature", "add a changelog", "transfer crate ownership".
when_to_use: |
  - "Publish my crate to crates.io"
  - "Bump the version / set up release-plz"
  - "Add a changelog"
  - "Yank a version"
  - "Deprecate a feature"
  - "Set up cargo-vet for supply chain"
  - "Transfer crate ownership"
---

# rust-release

The Rust release lifecycle: version policy, changelog generation, publishing,
and supply-chain maintenance. For initial project setup, use `rust-scaffold` or
`rust-quality`. This skill covers the *ongoing* part of shipping a crate.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Publish my crate to crates.io"
- "Bump the version / set up release-plz"
- "Add a changelog"
- "Yank a version"
- "Deprecate a feature"
- "Set up cargo-vet for supply chain"
- "How do I handle MSRV bumps?"
- "Generate a release PR"
- "Transfer crate ownership"
- "Override a transitive dependency with `[patch.crates-io]`"
- "How do I publish a workspace?"

**DO NOT use this skill for:**

## CONTRAST

- NOT for: scaffold / Cargo.toml / feature flags — use rust-scaffold
- NOT for: split into workspace / MSRV coordination — use rust-workspace
- NOT for: initial CI / cargo-deny setup — use rust-quality (this skill covers ongoing maintenance, not setup)
- This skill is the release lifecycle; scaffolding, structure, and quality are upstream

---

## §2. Versioning playbook (Cargo semver)

### 2.1 Pre-1.0 vs 1.0+

| Aspect | `0.x.y` | `1.x.y` and above |
|---|---|---|
| API stability | "Anything MAY change at any time" (semver.org) | Hard commitment: major bump required for breaking change |
| Cargo compat rule | `^0.x` accepts `>=0.x.0, <0.(x+1).0` — so `^0.3.5` means `>=0.3.5, <0.4.0` | Standard semver: `^1.2.3` means `>=1.2.3, <2.0.0` |
| When to commit to 1.0 | When you have a stable, documented API that the ecosystem has come to depend on | N/A |
| Adding a feature | Bump minor (`0.3.5` → `0.4.0`) | Bump minor |
| Bug fix | Bump patch (always safe) | Bump patch |
| Breaking change | Bump minor (`0.x` → `0.(x+1)`) | Bump major |

**Practical decision rule:** If your crate is `0.0.x`, change anything any time, stay there until API is roughly stable. If `0.x.y` (x ≥ 1), you've made a soft commitment to `0.x` API stability — breakages bump `0.x → 0.(x+1)`. Commit to 1.0 when *you* are tired of eating the breaking-change cost AND downstream users would feel the churn.

### 2.2 The `SemVer trick` (1.0.0 development)
If you want 1.0 signaling (semver commitment) before your API is truly stable:
```toml
# in Cargo.toml
[dependencies]
mycrate = "~1.0.0"     # means exactly 1.0.x; pre-1.1
```

Use this when you want downstream users to commit to your crate but you still want patch-level flexibility. Rare in practice; pre-1.0 with the `0.x` stability signal is usually enough.

### 2.3 MSRV policy (THE contested decision)
**There is no Rust community consensus.** Two camps:

| Camp | Position | Examples |
|---|---|---|
| **api-guidelines (advisory)** | MSRV bumps are *not* breaking → minor bump post-1.0, patch bump pre-1.0 | The official Rust API Guidelines recommendation |
| **Cornerstone crates (breaking)** | MSRV bumps ARE breaking → major bump post-1.0 | RustCrypto, rust-bitcoin, several large dependency-heavy projects |

**Why it matters now (2026):** Rust 1.84 (Jan 2025) shipped the **MSRV-aware resolver** (RFC 3537) + `incompatible-rust-versions = "fallback"` resolver mode. This makes MSRV enforcement much cheaper than in 2023 — the old "manual Cargo.lock" workaround (BurntSushi 2023) is no longer needed.

**The skill must ask the user which camp they're in.** Don't assume.

**Tools:**
- Document MSRV in `[package].rust-version` (advisory, but consumers respect it)
- CI-test the MSRV (see `rust-quality` §2)
- Use `cargo +1.81 update` (or whatever your MSRV is) to ensure dep tree stays MSRV-compatible

### 2.4 Workspace lockstep versioning
When all members of a workspace share a version (the cargo, tokio, axum pattern):
```toml
# workspace Cargo.toml
[workspace.package]
version = "0.5.0"   # all members inherit via version.workspace = "true"
```

Bump one number; all members publish together. The release tool (`release-plz`, `cargo-release`) coordinates the version bump + tag + publish across all members. See `rust-workspace` §8 for the full workspace pattern.

---

## §3. Changelog tooling decision

Three archetypes; pick by workflow, not feature list.

### 3.1 git-cliff (Rust binary, git-driven)
- **Best for:** "I want git history to drive my changelog"
- **Pros:** Super fast (Rust binary), Tera templates, conventional commits parsing, no network
- **Cons:** Git history can be noisy; you need disciplined commit messages
- **Install:** `cargo install git-cliff`
- **Config:** `cliff.toml` at repo root

### 3.2 release-please (Node, Google-built)
- **Best for:** "I want a Release PR workflow that the entire team understands"
- **Pros:** Multi-language, GitHub-native (creates a PR that you review + merge → publish), conventional commits
- **Cons:** Requires Node, less Rust-idiomatic
- **Install:** GitHub Action: `googleapis/release-please-action@v4`

### 3.3 Hand-curated (what serde, tokio, cargo do)
- **Best for:** "Mature project with curated user-facing changelog"
- **Pros:** Polished, user-focused, no noise
- **Cons:** Manual work; reviewer burden; easy to forget

**Decision tree:**
- Greenfield project? → **git-cliff** (or release-please if your team is JS/TS-heavy)
- Want a Release PR workflow? → **release-please**
- Mature Rust project with curated changelog? → hand-written, keep doing it

---

## §4. Publishing playbook

### 4.1 First publish
```bash
# 1. Make sure metadata is set (see rust-scaffold §3)
# 2. Verify it builds clean
cargo build --release
cargo test --all-features --locked
cargo clippy --all-targets --locked -- -D warnings

# 3. Dry run first — ALWAYS
cargo publish --dry-run --allow-dirty
# Inspect the .crate file that gets packaged

# 4. Real publish
cargo login              # paste API token from https://crates.io/me
cargo publish
```

### 4.2 CI publish workflow
Use **trusted publishing** (OIDC) when possible — no long-lived API tokens:
- GitHub: Configure in crates.io → "Trusted Publishers" → add your repo + workflow file
- Forgejo/Gitea: Similar, depends on the registry

**With release-plz (recommended for new projects):**
- release-plz opens a release PR on every push to main
- You review the version bump + changelog + lockfile changes
- Merge → release-plz publishes to crates.io and creates the GitHub release
- Config in `release-plz.toml`

**With cargo-release (alternative):**
- `cargo release --workspace --execute` runs locally or in CI
- More manual, but less GitHub-coupled

### 4.3 The 3 hard rules (novices always miss these)

1. **A version can NEVER be overwritten or deleted.** Only yanked. If you publish `0.1.0` with a bug, you publish `0.1.1` and yank `0.1.0`.
2. **Yanking does not delete code, it only removes the version from index resolution.** Existing `Cargo.lock` files still work. Downstream users who pinned to `0.1.0` keep their builds.
3. **`cargo yank` is the *only* mitigation for accidentally-leaked secrets in published crates** — but it does NOT stop the spread of those secrets if they were already cloned by someone. **Credential rotation is mandatory** in addition to yanking.

### 4.4 Yank a version
```bash
cargo yank --version 0.1.0 --reason "leaked API token in README"
# Undo (within reason):
cargo unyank --version 0.1.0
```

### 4.5 Publishing a subset (workspaces)
```bash
# Cargo 1.90+ (Sept 2025) — native workspace publishing
cargo workspace publish

# Older: with release-plz, just set `publish = false` on internal crates
# and publish only the public ones
```

**For internal-only members:**
```toml
[package]
name = "internal-types"
publish = false
```
Excluded from `cargo workspace publish`.

### 4.6 Crate ownership transfer
1. Current owner adds the new owner via `cargo owner --add <username>`
2. New owner accepts via email confirmation
3. After confirmation, both owners can publish. Original owner can then remove themselves with `cargo owner --remove <username>`

---

## §5. Dependency management

### 5.1 Update cadence
- **Patch updates:** automate with Dependabot (Rust ecosystem: `version: 2, package-ecosystem: cargo`)
- **Minor updates:** weekly, manual review of changelog
- **Major updates:** quarterly, dedicated upgrade cycle

### 5.2 MSRV-aware updates
```bash
# Ensures all picked deps support your MSRV (since Rust 1.81)
cargo +1.81 update --workspace
```

### 5.3 Security response
1. `cargo audit` (or `cargo deny check advisories`) flags it
2. Check if the dep has a patched version
3. If yes, bump + test + release
4. If no patched version, consider: fork + `[patch.crates-io]`, replace the dep, or live with the risk (document the decision)

### 5.4 `[patch.crates-io]` for fork overrides
```toml
# Cargo.toml
[patch.crates-io]
serde = { git = "https://github.com/you/serde-fork", branch = "fix-branch" }
```
Use for temporary forks (waiting on upstream PR) or permanent replacements. Document the reason in a comment in Cargo.toml.

### 5.5 Vendoring
```bash
cargo vendor
# Then in .cargo/config.toml:
# [source.crates-io]
# replace-with = "vendored-sources"
```
Use for air-gapped builds or supply-chain hardening. Increases repo size significantly.

---

## §6. Supply-chain ongoing maintenance

(This section is the *ongoing* part of the supply-chain ladder. For the initial setup, see `rust-quality` §6.)

### 6.1 cargo-vet maintenance
```bash
# When a new dep is added:
cargo vet            # fails on unaudited deps
cargo vet certify --accept-all -p new-dep    # after human review
# OR
cargo vet suggest --all    # adds it to exemptions (trust-based, no review)
```

### 6.2 Dependabot setup
`.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      rust-dependencies:
        patterns: ["*"]
    labels:
      - "dependencies"
```

### 6.3 RUSTSEC monitoring
- Subscribe to https://rustsec.org/ RSS
- Watch the rustsec/advisory-db GitHub repo
- `cargo audit` will catch it locally

### 6.4 When to bump a dep vs replace it
- Bump: dep is maintained, has a fix, fix is compatible
- Replace: dep is unmaintained, fix is hostile to your use case, or you want to drop the surface area
- Live with: dep has a known issue but no fix, and the risk is acceptable for your threat model — document the decision in your security policy

---

## §7. Feature deprecation playbook

### 7.1 The 3-step cycle (post-1.0)
```
1.x.0  — add new-feature, keep old-feature working
1.x+1  — old-feature marked deprecated (warns)
1.x+2  — old-feature removed
```

Minimum 2 minor versions of deprecation window. For widely-used crates, consider 3+.

### 7.2 Deprecation syntax
For an entire feature flag:
```toml
# Cargo.toml — just remove the entry, but warn users first via changelog
```

For an item that's gated by a feature:
```rust
#[cfg_attr(feature = "old-feature", deprecated = "use new-feature instead")]
pub fn old_api() { ... }
```

For a feature itself (warning at compile time):
```rust
#![cfg_attr(feature = "deprecated-foo", deprecated = "use bar instead")]
```

### 7.3 Pre-1.0 vs post-1.0
- **Pre-1.0:** churn freely. Document in changelog. No deprecation window.
- **Post-1.0:** follow the 3-step cycle. Use `#[deprecated]` liberally. Write the deprecation in `#[doc(hidden)]` notes so it shows in rustdoc.

### 7.4 Unstable features (the rustc pattern)
For features that may be removed or changed:
```rust
#![feature(unstable_feature)]   // nightly only

#[unstable(feature = "my_unstable", issue = "1234")]
pub fn experimental_api() { ... }
```

Use this when you want a feature to be visible in docs but signal "this is unstable, may change". Stable features don't need this.

### 7.5 When to ADD a feature vs REMOVE one
- ADD when: 2+ users ask for it, the abstraction is real, the dep is acceptable
- REMOVE when: zero users for 2 minor versions, the abstraction can be done in user code
- Never remove during a 1.x series without a deprecation cycle

---

## §8. Handoff to other skills

- **MSRV coordination across a workspace** → `rust-workspace` §5
- **Workspace lockstep versioning** → `rust-workspace` §8
- **Initial cargo-deny / cargo-vet setup** → `rust-quality` §6
- **Initial CI template for cargo publish** → `rust-quality` §2
- **Feature flag design (additive rules, naming, internal features)** → `rust-scaffold` §5

---

## §9. Anti-patterns

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

---

## §10. Key sources

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
- [11] Real-world: serde, tokio, axum, cargo, release-plz, cargo-smart-release, gtk-rs, fuel-core (see `references/real-world-release-patterns.md` if shipped)
- [12] BurntSushi on MSRV + manual Cargo.lock (now obsolete post-1.84) — https://blog.burntsushi.net/cargo-msrv-2023/
- [13] Cargo #12162 (workspace inheritance additive-defaults pitfall) — https://github.com/rust-lang/cargo/issues/12162
