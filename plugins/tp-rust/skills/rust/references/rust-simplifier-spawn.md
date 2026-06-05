## rust-simplifier — spawn guidance

**When to spawn in SCAFFOLD mode:** after the user has finished writing a non-trivial chunk of code in the scaffolded lib+bin layout — typically after the initial `src/lib.rs` and `src/main.rs` are filled in with the first feature implementation, or after a borrow-checker fix that added `.clone()` calls and now needs cleanup. The Cargo.toml is already reviewed by `rust-cargo-reviewer`; `rust-simplifier` polishes the `.rs` code, not the manifest.

**When to spawn in QUALITY mode:** after the canonical 6-job CI is in place and the user has written substantive code that would benefit from a pre-commit polish pass. Spawn once per session per logical chunk, not after every line. Do not spawn if the user is mid-edit on a function — wait for a stable stopping point.

**What it does:** applies idiomatic Rust refactors to the current diff — clone elimination, `?` over nested `match`, iterator chains, `if let` / `let else` over single-arm match, `copied()` over `cloned()`, `&str` over `&String` in signatures. See the `rust-simplifier` agent definition for the full contract (P1–P6), the ordered operations, and the failure modes it defends against.

**Scope discipline:** `.rs` files in the current session diff only. Never touches `Cargo.toml` (that is `rust-cargo-reviewer`'s domain), never changes public API signatures, never introduces `unsafe`, never edits files outside the diff. If the user asks for a broader scope, the main agent should pass an explicit scope directive to the subagent.

**How to verify the spawn succeeded:** `rust-simplifier` returns a summary of files touched plus a `cargo check` and `cargo clippy` verdict. If either verdict is "compile failed" or "new lints", the subagent has already reverted the offending edit and reported the borrow-checker error to the user. The main agent should not commit the changes until it has reviewed the subagent's summary.

**Do not spawn when:** the user is still actively editing the file (the diff is in flux), the diff is empty, the only changes are in `Cargo.toml` or `Cargo.lock`, or the user has explicitly disabled simplification for this session.
