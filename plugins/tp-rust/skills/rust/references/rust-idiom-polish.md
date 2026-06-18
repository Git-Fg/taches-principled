## Rust idiomatic-polish — inline checklist

**When to apply in SCAFFOLD mode:** after writing a non-trivial chunk of code in the scaffolded lib+bin layout — typically after the initial `src/lib.rs` and `src/main.rs` are filled in with the first feature implementation, or after a borrow-checker fix that added `.clone()` calls and now needs cleanup. The Cargo.toml is already reviewed by `tp-critic` with the "audit Cargo.toml" lens; this checklist polishes the `.rs` code, not the manifest.

**When to apply in QUALITY mode:** after the canonical 6-job CI is in place and the code has substantive logic that would benefit from a pre-commit polish pass. Apply once per session per logical chunk, not after every line. Do not apply if the file is mid-edit on a function — wait for a stable stopping point.

**What it does (apply in order):**
1. Clone elimination — replace `.clone()` with borrowing where ownership isn't actually needed.
2. `?` over nested `match` — flatten `match`/`if let Err` chains on `Result`/`Option` into `?` and `let else`.
3. Iterator chains — convert manual loops into `iter()`/`map()`/`filter()`/`collect()` chains where it improves readability.
4. `if let` / `let else` — replace single-arm `match` with the lighter construct.
5. `.copied()` over `.cloned()` for `Copy` types.
6. `&str` over `&String` in function signatures.

**Scope discipline:** `.rs` files in the current session diff only. Never touches `Cargo.toml` (that is `tp-critic` "audit Cargo.toml" territory), never changes public API signatures, never introduces `unsafe`, never edits files outside the diff. If the user asks for a broader scope, do not silently expand it — confirm first.

**How to verify:** run `cargo check` and `cargo clippy`. If either fails, revert the offending edit and report the borrow-checker error to the user. Do not commit until both pass.

**Do not apply when:** the file is still actively being edited (the diff is in flux), the diff is empty, the only changes are in `Cargo.toml` or `Cargo.lock`, or the user has explicitly disabled simplification for this session.