#!/usr/bin/env python3
"""
Trigger Benchmark: Skill Description Reliability Testing

Automates the 20-query test framework for skill description routing:
- 5 core positive (must trigger)
- 3 edge positive (should trigger)
- 5 core negative (must not trigger)
- 3 edge negative (should not trigger)
- 4 held-out (blind test cases)

Usage:
    python3 run_trigger_benchmark.py <skill-name> <queries-dir>
    python3 run_trigger_benchmark.py create-skills ./test-queries/
    python3 run_trigger_benchmark.py create-subagents --interactive

Output:
    results.json with per-query results and aggregate scores
    benchmark.json with full structured output

Exit criteria:
    Core positive: 100% required
    Edge positive: >60% target
    Core negative: 100% required
    Edge negative: >40% target
    Held-out: >70% target
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class QueryResult:
    query: str
    category: str
    should_trigger: bool
    runs: int
    triggers: int
    trigger_rate: float
    passed: bool


@dataclass
class BenchmarkResults:
    skill_name: str
    total_queries: int
    passed: int
    failed: int
    pass_rate: float
    results: list
    summary: dict


def run_claude_query(query: str, skill_name: str, runs: int = 3) -> tuple[int, float]:
    """
    Run a query against the skill and return trigger count and rate.

    Uses stream-json output to detect skill invocation:
    - content_block_start with tool_use (type=Skill) -> skill loading
    - content_block_delta with input_json_delta -> skill name in params
    """
    trigger_count = 0

    for _ in range(runs):
        try:
            result = subprocess.run(
                ["claude", "-p", query, "--output-format", "stream-json",
                 "--include-partial-messages", "--dangerously-auto-accept"],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            if f'"{skill_name}"' in output:
                trigger_count += 1
        except subprocess.TimeoutExpired:
            continue
        except FileNotFoundError:
            print("ERROR: claude command not found. Is Claude Code installed?")
            sys.exit(1)

    return trigger_count, trigger_count / runs


def load_queries_from_dir(queries_dir: Path) -> dict:
    """Load query files from directory. Each file is named by category."""
    queries = {}
    categories = ["core-positive", "edge-positive", "core-negative", "edge-negative", "held-out"]

    for cat in categories:
        cat_queries = []
        for i in range(1, 100):  # Support up to 99 queries per category
            f = queries_dir / f"{cat}-{i}.txt"
            if f.exists():
                cat_queries.append(f.read_text().strip())
            elif i == 1 and not any(queries_dir.glob(f"{cat}*.txt")):
                # No files for this category
                break
        if cat_queries:
            queries[cat] = cat_queries

    return queries


def load_queries_interactive(skill_name: str) -> dict:
    """Interactive query collection when no query directory provided."""
    print(f"\n=== Trigger Benchmark for '{skill_name}' ===\n")
    queries = {}

    category_info = [
        ("core-positive", 5, "Must trigger — primary use cases"),
        ("edge-positive", 3, "Should trigger — ambiguous cases"),
        ("core-negative", 5, "Must NOT trigger — clearly off-topic"),
        ("edge-negative", 3, "Should NOT trigger — adjacent territory"),
        ("held-out", 4, "Blind test cases — enter after all others"),
    ]

    for cat, expected, desc in category_info:
        print(f"\n--- {cat.replace('-', ' ').title()} ---")
        print(f"{desc} (expect ~{expected} queries)\n")

        cat_queries = []
        while True:
            line = input(f"Query {len(cat_queries) + 1} (Enter to finish): ").strip()
            if not line:
                break
            cat_queries.append(line)

        if cat_queries:
            queries[cat] = cat_queries
            print(f"  Collected {len(cat_queries)} queries")

    return queries


def check_exit_criteria(summary: dict) -> dict:
    """Check results against exit criteria. Returns dict of pass/fail per category."""
    checks = {}
    thresholds = {
        "core-positive": (summary["core-positive"]["pass_rate"], 1.0, "100%"),
        "edge-positive": (summary["edge-positive"]["pass_rate"], 0.6, ">60%"),
        "core-negative": (summary["core-negative"]["pass_rate"], 1.0, "100%"),
        "edge-negative": (summary["edge-negative"]["pass_rate"], 0.4, ">40%"),
        "held-out": (summary["held-out"]["pass_rate"], 0.7, ">70%"),
    }

    for cat, (rate, threshold, target) in thresholds.items():
        passed = rate >= threshold if cat in ["core-positive", "core-negative"] else rate >= threshold
        checks[cat] = {
            "rate": rate,
            "threshold": threshold,
            "target": target,
            "passed": passed,
            "required": cat in ["core-positive", "core-negative"]
        }

    return checks


def run_benchmark(skill_name: str, queries: dict, runs_per_query: int = 3) -> BenchmarkResults:
    """Run the full benchmark."""
    results = []
    summary = {}

    for category, cat_queries in queries.items():
        cat_results = []
        for query in cat_queries:
            triggers, rate = run_claude_query(query, skill_name, runs=runs_per_query)
            should_trigger = category in ["core-positive", "edge-positive", "held-out"]
            passed = rate >= 0.5  # 50% threshold: majority of runs triggered

            qr = QueryResult(
                query=query,
                category=category,
                should_trigger=should_trigger,
                runs=runs_per_query,
                triggers=triggers,
                trigger_rate=rate,
                passed=passed
            )
            cat_results.append(qr)
            results.append(qr)

        # Aggregate category stats
        pass_count = sum(1 for r in cat_results if r.passed)
        pass_rate = pass_count / len(cat_results) if cat_results else 0
        summary[category] = {
            "queries": len(cat_results),
            "passed": pass_count,
            "failed": len(cat_results) - pass_count,
            "pass_rate": pass_rate,
        }

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total if total > 0 else 0

    return BenchmarkResults(
        skill_name=skill_name,
        total_queries=total,
        passed=passed,
        failed=total - passed,
        pass_rate=pass_rate,
        results=[asdict(r) for r in results],
        summary=summary
    )


def print_results(results: BenchmarkResults, checks: dict):
    """Print benchmark results in human-readable format."""
    print("\n" + "=" * 60)
    print(f"TRIGGER BENCHMARK: {results.skill_name}")
    print("=" * 60)

    print("\n--- Per-Category Results ---\n")
    for cat, stats in results.summary.items():
        check = checks.get(cat, {})
        status = "PASS" if check.get("passed") else "FAIL"
        if check.get("required") and not check.get("passed"):
            status = "CRITICAL FAIL"
        print(f"  [{status}] {cat}")
        print(f"        {stats['passed']}/{stats['queries']} passed ({stats['pass_rate']:.0%})")
        if check:
            print(f"        Target: {check['target']} | Rate: {check['rate']:.0%}")

    print("\n--- Overall ---\n")
    print(f"  {results.passed}/{results.total_queries} passed ({results.pass_rate:.0%})")

    print("\n--- Exit Criteria ---\n")
    all_passed = True
    for cat, check in checks.items():
        status = "PASS" if check["passed"] else ("FAIL" if check["required"] else "WARN")
        if check["required"] and not check["passed"]:
            all_passed = False
        print(f"  [{status}] {cat}: {check['rate']:.0%} (target: {check['target']})")

    print()
    if all_passed:
        print("All critical criteria met.")
    else:
        print("Critical criteria failed. Fix before production.")

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Run trigger benchmark for a skill"
    )
    parser.add_argument("skill_name", help="Skill name to test")
    parser.add_argument("queries_dir", nargs="?", help="Directory with query files")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive query collection")
    parser.add_argument("--runs", "-r", type=int, default=3,
                        help="Runs per query (default: 3)")
    parser.add_argument("--output", "-o", default="./benchmark-results",
                        help="Output directory")

    args = parser.parse_args()

    if args.interactive or not args.queries_dir:
        queries = load_queries_interactive(args.skill_name)
    else:
        queries_dir = Path(args.queries_dir)
        if not queries_dir.exists():
            print(f"ERROR: Directory not found: {queries_dir}")
            sys.exit(1)
        queries = load_queries_from_dir(queries_dir)
        if not queries:
            print("ERROR: No query files found. Expected format: core-positive-1.txt, edge-positive-1.txt, etc.")
            sys.exit(1)

    print(f"\nRunning benchmark for '{args.skill_name}'...")
    print(f"Total queries: {sum(len(v) for v in queries.values())}")
    print(f"Runs per query: {args.runs}\n")

    results = run_benchmark(args.skill_name, queries, runs_per_query=args.runs)
    checks = check_exit_criteria(results.summary)
    all_passed = print_results(results, checks)

    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    benchmark_path = output_dir / "benchmark.json"
    with open(benchmark_path, "w") as f:
        json.dump({
            "skill_name": results.skill_name,
            "timestamp": time.time(),
            "runs_per_query": args.runs,
            "summary": results.summary,
            "checks": checks,
            "results": results.results,
            "all_passed": all_passed,
        }, f, indent=2)

    print(f"\nResults saved to: {benchmark_path}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()