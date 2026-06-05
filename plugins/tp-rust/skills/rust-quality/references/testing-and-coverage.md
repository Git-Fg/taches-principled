# Test Runner and Coverage for Rust

Reference for `cargo-nextest`, coverage tooling, and feature matrix testing. Read it before adopting a faster test runner or adding coverage to a Rust project.

## §1. Why cargo-nextest

- Process-per-test execution (true parallelism, no shared state)
- 1.4-3.4× faster than `cargo test` on real-world projects (see [nexte.st/docs/benchmarks](https://nexte.st/docs/benchmarks/))
- Built-in retries (`--retries 2`)
- Per-test timeouts (`--test-timeout 60s`)
- JUnit XML output for CI (`--message-format junit`)
- No `--no-fail-fast` needed (default)

## §2. `.config/nextest.toml` profile

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

## §3. When to adopt nextest

- Test suite > 200 tests, OR
- CI test job > 5 min, OR
- You need per-test timeouts, retries, or JUnit XML output

## §4. cargo-hack for feature matrix testing

```yaml
- name: Feature matrix
  run: cargo hack check --feature-powerset --no-default-features
```

Use when you have ≥3 features to ensure every combination compiles.

## §5. cargo-llvm-cov (preferred for Linux/macOS)

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

## §6. cargo-tarpaulin (cross-platform, less accurate)

Use only when you need Windows support and cargo-llvm-cov won't work.

## §7. Coverage scope

Start with line coverage. Add branch coverage when you have a coverage target:
```bash
cargo llvm-cov nextest --branch
```

## §8. Benchmarking (when needed)

**Criterion (default):**
```rust
// benches/parse_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_parse(c: mut Criterion) {
    c.bench_function("parse small input", |b| {
        b.iter(|| mycrate::parse(black_box("input")))
    });
}

criterion_group!(benches, bench_parse);
criterion_main!(benches);
```

Run: `cargo bench`. For CI, use `bencher.dev` or `criterion-cycles` to track regressions.

**divan** (rising alternative): faster, simpler, smaller ecosystem. Use when Criterion's stat-sig machinery is overkill.

**iai-callgrind** (deterministic): use when you need deterministic benchmarks (no flakiness from system noise).

**When to add benchmarks:**
- You have a perf-sensitive hot path
- CI shows build-time regression and you want to track it
- You want to detect perf regressions before users do

DO NOT add benchmarks preemptively. Each one is a maintenance cost.
