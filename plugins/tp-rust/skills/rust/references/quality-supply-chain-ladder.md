# Supply-Chain Ladder for Rust

Reference for the 4-stage supply-chain ladder that takes a Rust crate from "no audits" to "fully monitored." Most projects stop at Stage 1. Read it before publishing a crate or hardening a security-critical project.

## §1. Stage 0 — Basic advisories (Day 1)

```bash
cargo install cargo-audit --locked
cargo audit
```

Catches known vulns from the RustSec advisory database. ~5s, no config.

## §2. Stage 1 — cargo-deny (recommended for production)

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

## §3. Stage 2 — cargo-vet (security-critical projects)

```bash
cargo install cargo-vet --locked
cargo vet init
cargo vet import mozilla    # bootstrap from Mozilla's audits
cargo vet import google     # bootstrap from Google's audits
cargo vet
```

Certifies that a human has reviewed every dep against criteria like "safe-to-deploy" or "safe-to-run". Audits are shareable, so most of your tree is already covered. Mozilla + Google both publish their crate audits.

## §4. Stage 3 — Always-on monitoring

- GitHub Dependabot for Rust: `version: 2, package-ecosystem: cargo, directory: /`
- Subscribe to https://rustsec.org/ RSS

## §5. SBOM (if required by enterprise)

`cargo-cyclonedx` generates a CycloneDX SBOM from `Cargo.lock`.
