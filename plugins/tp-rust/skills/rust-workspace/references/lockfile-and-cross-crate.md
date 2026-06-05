# Lockfile, MSRV Coordination, and Cross-Crate Patterns

Reference for `Cargo.lock` policy, MSRV coordination across members, and the cross-crate patterns (internal features, path dependencies, shared dev-dependencies, feature unification). Read it before publishing a workspace or adding a member crate.

## §1. Cargo.lock

- **Always commit `Cargo.lock` for applications and workspaces with binaries.**
- **Do NOT commit `Cargo.lock` for libraries distributed individually to crates.io** (every member publishes its own lock state).
- For a workspace with one library + one binary, commit the lock (the binary needs it).
- Use `--locked` in CI to catch forgotten lock updates.

## §2. MSRV coordination across members

- Set `rust-version` in `[workspace.package]` — all members inherit
- The most restrictive member's MSRV is the workspace's effective MSRV
- If member A needs Rust 1.85 and member B is fine with 1.70, the workspace is effectively 1.85
- Cargo's MSRV-aware resolver (1.81+) picks deps compatible with the WORKSPACE MSRV
- If one member really needs an older dep, it must override the workspace `rust-version` in its own `[package]` — but this triggers a warning

## §3. Internal features (`__` prefix)

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

## §4. Path dependencies (workspace members)

```toml
[dependencies]
my-shared-types = { path = "../shared-types" }
```

Auto-detected by Cargo for workspace members. Do NOT use `path` deps in published crates (breaks for downstream users who don't have the same filesystem layout).

## §5. Shared dev-dependencies

```toml
# workspace.dev-dependencies
pretty_assertions = "1"
insta = "1"
```

Members inherit these for tests without needing to redeclare.

## §6. Feature unification

When member A enables feature F and member B does not, the workspace compiles with F. This is a Cargo-wide behavior, not a workspace-specific one. Watch for:
- The "biggest feature wins" rule
- Surprising compilation time when one member enables a heavy feature
- Use `--no-default-features` on a specific member to debug

## §7. Workspace publishing

For workspaces with multiple published crates, set up the publishing policy in `release-plz.toml` or use Cargo 1.90+'s native `cargo publish --workspace` from the workspace root.

**Internal-only crates:** set `publish = false` in their `[package]` section. They build as part of the workspace but are never published to crates.io.

```toml
# workspace member, but excluded from `cargo publish --workspace`
[package]
name = "internal-types"
version = "0.1.0"
publish = false
```
