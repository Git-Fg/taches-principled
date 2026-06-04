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

## §2. GitHub Actions CI template (copy-pasteable)

`.github/workflows/ci.yml`:
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Cancel in-progress runs on PR branches (saves 20+ min/force-push on large codebases).
# Never cancel on main — every push there should complete.
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

env:
  CARGO_TERM_COLOR: always
  CARGO_INCREMENTAL: 0          # disable incremental in CI (faster, smaller cache)
  RUSTFLAGS: "-D warnings"      # deny warnings for your crate, not transitive deps

jobs:
  # Cheapest check first. Everything else depends on it.
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@nightly
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  # Cross-platform test matrix. Add windows-latest only if you claim cross-platform support.
  test:
    needs: format
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --all-features
      - run: cargo test --doc --locked

  # Lint (depends on format so we fail fast).
  lint:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo clippy --all-targets --locked -- -D warnings

  # Build docs (also catches broken intra-doc links).
  doc:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features --locked
        env:
          RUSTDOCFLAGS: "-D warnings"

  # Audit only on main — advisory DB changes shouldn't break PRs.
  audit:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: taiki-e/install-action@v2
        with:
          tool: cargo-deny
      - run: cargo deny check

  # MSRV check (run the same matrix's MSRV).
  msrv:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@1.81.0   # match your MSRV
      - uses: Swatinem/rust-cache@v2
      - run: cargo check --locked
```

**Alternative one-liner with `actions-rust-lang/setup-rust-toolchain`:**
```yaml
- uses: actions/checkout@v4
- uses: actions-rust-lang/setup-rust-toolchain@v1
  with:
    toolchain: stable
    cache: true                              # bundles Swatinem/rust-cache
    components: rustfmt, clippy
```

This is the canonical stack as of 2026: `dtolnay/rust-toolchain` (or `actions-rust-lang/setup-rust-toolchain` which bundles it) + `Swatinem/rust-cache@v2` + `taiki-e/install-action` for pre-built cargo subcommands. Source: rust-project-primer CI chapter.

**For Forgejo/Gitea:** same YAML, just replace `actions/checkout` with `actions/checkout@v4` and the cache action works on self-hosted runners using the native Gitea cache backend.

---

## §3. Clippy policy

### 3.1 Per-project `clippy.toml`
```toml
# Set MSRV for MSRV-aware lints — otherwise clippy will suggest features
# only available in newer Rust.
msrv = "1.81"

# Avoid suggestions that pull in heavy deps.
disallowed-types = [
    # { path = "std::sync::Mutex", reason = "use parking_lot::Mutex" },
]
```

### 3.2 Per-project `rustfmt.toml`
```toml
edition = "2024"            # match your Cargo.toml edition
max_width = 100
imports_granularity = "Crate"  # nightly-only; falls back gracefully on stable
```

### 3.3 Library-level pragmas (`src/lib.rs`)
```rust
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]
#![forbid(unsafe_code)]   # if you're a safe-Rust project
// DO NOT use #![deny(warnings)] — see §3.5
```

### 3.4 Lint group selection per use case
- **Binary project:** `cargo clippy -- -D warnings` (defaults only)
- **Library project:** `cargo clippy --all-targets -- -W clippy::pedantic -W clippy::nursery -A clippy::missing-errors-doc -D warnings`
- **Embedded / no_std:** also enable `#![warn(clippy::no_std)]` and the `clippy::cargo` group

### 3.5 The `#![deny(warnings)]` anti-pattern
**DO NOT** use `#![deny(warnings)]` in `lib.rs`. It makes your crate fail to compile when a transitive dep emits a new warning (which is outside your control). Use `RUSTFLAGS: "-D warnings"` in CI for your crate only.

---

## §4. Test runner: cargo-nextest

### 4.1 Why nextest
- Process-per-test execution (true parallelism, no shared state)
- 1.4-3.4× faster than `cargo test` on real-world projects (see [nexte.st/docs/benchmarks](https://nexte.st/docs/benchmarks/))
- Built-in retries (`--retries 2`)
- Per-test timeouts (`--test-timeout 60s`)
- JUnit XML output for CI (`--message-format junit`)
- No `--no-fail-fast` needed (default)

### 4.2 `.config/nextest.toml` profile
```toml
# Default profile for local dev
[profile.default]
retries = 0
test-threads = "num-cpus"
slow-timeout = { period = "30s", terminate-after = 2 }

# CI profile (used in GitHub Actions)
[profile.ci]
retries = 2
fail-fast = false
test-timeout = "120s"
```

Activate in CI:
```yaml
- run: cargo nextest run --profile ci --message-format junit > results.xml
```

### 4.3 When to adopt nextest
- Test suite > 200 tests, OR
- CI test job > 5 min, OR
- You need per-test timeouts, retries, or JUnit XML output

### 4.4 cargo-hack for feature matrix testing
```yaml
- name: Feature matrix
  run: cargo hack check --feature-powerset --no-default-features
```

Use when you have ≥3 features to ensure every combination compiles.

---

## §5. Coverage

### 5.1 cargo-llvm-cov (preferred for Linux/macOS)
```bash
cargo install cargo-llvm-cov
cargo llvm-cov nextest --html
# open target/llvm-cov/html/index.html
```

In CI:
```yaml
- name: Coverage
  run: cargo llvm-cov nextest --lcov --output-path lcov.info
- uses: codecov/codecov-action@v4
  with:
    files: lcov.info
```

### 5.2 cargo-tarpaulin (cross-platform, less accurate)
Use only when you need Windows support and cargo-llvm-cov won't work.

### 5.3 Coverage scope
Start with line coverage. Add branch coverage when you have a coverage target:
```bash
cargo llvm-cov nextest --branch
```

---

## §6. Supply-chain ladder

A 4-stage ladder; most projects stop at Stage 1.

### Stage 0 — Basic advisories (Day 1 of any published crate)
```bash
cargo install cargo-audit --locked
cargo audit
```
Catches known vulns from the RustSec advisory database. ~5s, no config.

### Stage 1 — cargo-deny (add ~2 hours, recommended for production)
```bash
cargo install cargo-deny --locked
cargo deny init    # creates deny.toml with comments
cargo deny check
```

**Minimal `deny.toml` for a 2026 project (verified against cargo-deny 0.19+):**
```toml
# Verified against cargo-deny 0.19.8 — REMOVED keys (`vulnerability`, `unlicensed`)
# from 0.18+ are NOT used here. See cargo-deny config docs for the current schema.

[graph]
targets = [
    "x86_64-unknown-linux-gnu",
    "aarch64-apple-darwin",
    "x86_64-pc-windows-msvc",
]

[advisories]
version = 2
yanked = "warn"
ignore = []                          # add {id, reason} entries for accepted risks

[licenses]
version = 2
allow = [
    "MIT", "MIT-0", "Apache-2.0", "Apache-2.0 WITH LLVM-exception",
    "BSD-2-Clause", "BSD-3-Clause", "ISC", "Zlib", "Unicode-3.0",
    "CC0-1.0", "MPL-2.0",
]
confidence-threshold = 0.8

[bans]
multiple-versions = "warn"
wildcards = "deny"
deny = []

[sources]
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
```

**Removed keys (cargo-deny 0.18+, per PR #611):**
- `vulnerability` → moved into `[advisories]`
- `unlicensed` → moved into `[licenses]`
- `unmaintained` now takes `all|workspace|transitive|none`, not a lint level

**NOTE:** If you copy a `deny.toml` from a 2024 or earlier tutorial, it WILL fail to parse. Always verify against the current schema: https://embarkstudios.github.io/cargo-deny/checks/cfg.html

### Stage 2 — cargo-vet (add ~1 day, for security-critical projects)
```bash
cargo install cargo-vet --locked
cargo vet init
cargo vet import mozilla    # bootstrap from Mozilla's audits
cargo vet import google     # bootstrap from Google's audits
cargo vet
```
Certifies that a human has reviewed every dep against criteria like "safe-to-deploy" or "safe-to-run". Audits are shareable, so most of your tree is already covered. Mozilla + Google both publish their crate audits.

### Stage 3 — Always-on monitoring
- GitHub Dependabot for Rust: `version: 2, package-ecosystem: cargo, directory: /`
- Subscribe to https://rustsec.org/ RSS

### SBOM (if required by enterprise)
`cargo-cyclonedx` generates a CycloneDX SBOM from `Cargo.lock`.

---

## §7. Developer experience (local)

### 7.1 `bacon` for file-watching
```bash
cargo install bacon --locked
bacon test       # auto-runs nextest on file change
bacon clippy     # auto-runs clippy on file change
```

### 7.2 `.cargo/config.toml` for build speed
```toml
# Use a faster linker (2-10x faster linking on Linux)
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

# Use sccache if available
[build]
rustc-wrapper = "/path/to/sccache"
```

### 7.3 Toolchain pinning (`rust-toolchain.toml`)
```toml
[toolchain]
channel = "1.85.0"                       # pin to a specific version
components = ["rustfmt", "clippy", "rust-analyzer"]
profile = "minimal"                      # skip docs, faster install
```

### 7.4 CI cache
`Swatinem/rust-cache@v2` is the standard. Caches Cargo registry + build artifacts. Cuts CI time 30-70%.

---

## §8. Benchmarking

### 8.1 Criterion (default)
```rust
// benches/parse_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_parse(c: &mut Criterion) {
    c.bench_function("parse small input", |b| {
        b.iter(|| mycrate::parse(black_box("input")))
    });
}

criterion_group!(benches, bench_parse);
criterion_main!(benches);
```

Run: `cargo bench`. For CI, use `bencher.dev` or `criterion-cycles` to track regressions.

### 8.2 divan (rising alternative)
Faster, simpler, smaller ecosystem. Use when Criterion's stat-sig machinery is overkill.

### 8.3 iai-callgrind (deterministic)
Use when you need deterministic benchmarks (no flakiness from system noise).

### 8.4 When to add benchmarks
- You have a perf-sensitive hot path
- CI shows build-time regression and you want to track it
- You want to detect perf regressions before users do

DO NOT add benchmarks preemptively. Each one is a maintenance cost.

---

## §9. Tool matrix (quick reference)

| Tool | Purpose | When to adopt |
|---|---|---|
| `rustfmt` | Formatting | Day 1 (non-negotiable) |
| `clippy` | Lints | Day 1; pedantic for libs |
| `cargo-nextest` | Fast test runner | Test suite > 200 OR CI > 5 min |
| `cargo-hack` | Feature matrix testing | ≥3 features |
| `cargo-deny` | License + advisory + ban + source | Day 1 of published crate |
| `cargo-audit` | RUSTSEC check (subsumed by deny) | Standalone if you don't want deny |
| `cargo-vet` | Supply-chain audits | Stage 2+ (security-critical) |
| `cargo-machete` | Unused dependencies | Weekly in CI |
| `cargo-outdated` | Out-of-date deps | Weekly, not in PR CI |
| `criterion` / `divan` | Benchmarking | When you have perf-sensitive code |
| `cargo-llvm-cov` | Coverage | When you have a coverage target |
| `cargo-mutants` | Mutation testing | Mature, high-stakes code (weekly) |
| `bacon` / `cargo-watch` | Local dev file-watcher | Day 1 |
| `sccache` | Shared compilation cache | CI > 10 min |
| `mold` / `lld` / `wild` | Fast linker | When link time > 5s |
| `rust-analyzer` | LSP | Day 1 |
| `dtolnay/rust-toolchain` | GH Action: toolchain | Day 1 on GH |
| `Swatinem/rust-cache@v2` | GH Action: cache | Day 1 on GH |
| `taiki-e/install-action` | GH Action: pre-built cargo subcommands | When you use nextest/hack/audit |

---

## §10. Handoff to other skills

- **Initial setup of clippy/CI/deny/nextest** → this skill
- **Ongoing supply-chain maintenance + new audit policies** → `rust-release` §6
- **Benchmarking over time + performance regression tracking** → `rust-release` (CI integration for `cargo bench` / bencher.dev)
- **Audit findings in a specific dependency** → `rust-release` (yank/upgrade/replace)

---

## §11. Anti-patterns

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

---

## §12. Key sources

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
