#!/usr/bin/env python3
"""
Marketplace discipline audit.

Walks a Claude Code marketplace and emits findings on 5 rule categories:
  R1. Agent roster discipline        — count cap, tools: exceptions, Ground truth sections
  R2. Spawn discipline                — every spawn tp-critic/explorer/researcher has lens/scope/question
  R3. Fork-skill discipline           — every context: fork skill has references/fork-rationale.md
  R4. Description quality             — ≤1536 chars, verb-led first 200, CONTRAST vs adjacent
  R5. Catalog discipline              — plugin.json version matches marketplace, description mentions roster

Usage:
  python3 scripts/audit.py [MARKETPLACE_ROOT] [--ci] [--config CONFIG.json]

  MARKETPLACE_ROOT   defaults to the git repo root (parent of this script's plugins/ dir).
  --ci               machine-readable JSON output for CI consumption (exit 1 on BLOCKER).
  --config CONFIG    path to a discipline config JSON (see DEFAULT_CONFIG).

Exit code:
  0 — no BLOCKER findings (warnings/nudges allowed)
  1 — one or more BLOCKER findings
  2 — audit itself crashed

The audit is intentionally a boundary checker, not a quality checker: it tests
presence and format, not wording. The tp-roster-auditor agent uses judgment when
the script's regex flags false positives.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


# ─── Severity ──────────────────────────────────────────────────────────────────

BLOCKER = "BLOCKER"
WARNING = "WARNING"
NUDGE = "NUDGE"


# ─── Config ────────────────────────────────────────────────────────────────────

# The canonical taches-principled config. Other marketplaces pass --config.
DEFAULT_CONFIG = {
    # R1: agent roster
    "agent_roster_cap": 7,  # 6 keepers + 1 read-only exception (wiki-searcher). CI BLOCKER when exceeded.
    "allowed_tools_locks": ["wiki-searcher", "tp-roster-auditor"],  # tp-roster-auditor is read-only with shell; wiki-searcher is read-only without
    # R1 + R4: required agent body section
    "required_agent_section": "Ground truth",
    # R2: spawn discipline
    "spawn_targets": ["tp-critic", "tp-explorer", "tp-researcher"],
    "spawn_arg_window_chars": 400,  # how far ahead to look for lens:/scope:/question:
    # R3: fork skills
    "required_fork_reference": "references/fork-rationale.md",
    # R4: description quality
    "description_max_chars": 1536,
    "verb_led_first_n_chars": 200,
}


# ─── Finding ───────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    rule: str
    severity: str
    file: str
    line: Optional[int]
    detail: str
    fix: str

    def as_dict(self) -> dict:
        d = asdict(self)
        d["file"] = str(self.file)
        return d


# ─── Frontmatter parsing ───────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Frontmatter values are best-effort scalar extraction."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end():]
    fm: dict = {}
    # Simple line-based extraction for scalar fields. Block scalars (|, >) are captured as their joined block.
    lines = fm_raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        mm = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if not mm:
            i += 1
            continue
        key, val = mm.group(1), mm.group(2).strip()
        if val in ("|", ">"):
            # block scalar: capture indented continuation
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                block.append(lines[i])
                i += 1
            fm[key] = "\n".join(b.strip() for b in block if b.strip()).strip()
        elif val == "":
            # could be inline list or empty; try inline list on next lines
            list_items = []
            j = i + 1
            while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
                list_items.append(re.sub(r"^\s+-\s+", "", lines[j]).strip())
                j += 1
            if list_items:
                fm[key] = list_items
                i = j
                continue
            fm[key] = ""
            i += 1
        else:
            # strip quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val
            i += 1
    return fm, body


# ─── R1: Agent roster discipline ───────────────────────────────────────────────

def audit_agents(repo_root: Path, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    agents_dir = repo_root / "plugins"
    agent_files = sorted(agents_dir.rglob("agents/*.md"))
    if not agent_files:
        return findings  # nothing to audit

    # R1a: count cap
    cap = config["agent_roster_cap"]
    if len(agent_files) > cap:
        findings.append(Finding(
            rule="R1a-roster-cap",
            severity=BLOCKER,
            file="plugins/*/agents/",
            line=None,
            detail=f"{len(agent_files)} agent files exceed the roster cap of {cap}",
            fix=f"Reduce to ≤{cap} named agents, OR bump `agent_roster_cap` in discipline config with a CHANGELOG entry justifying the new specialist",
        ))

    for af in agent_files:
        rel = af.relative_to(repo_root)
        text = af.read_text()
        fm, body = parse_frontmatter(text)
        name = str(fm.get("name", af.stem))

        # R1b: tools: lock exceptions
        if "tools" in fm:
            if name not in config["allowed_tools_locks"]:
                findings.append(Finding(
                    rule="R1b-tools-lock",
                    severity=BLOCKER,
                    file=str(rel),
                    line=None,
                    detail=f"agent `{name}` has a `tools:` allowlist but is not in the allowed list {config['allowed_tools_locks']}",
                    fix="Either remove the `tools:` field (let the agent inherit) or add the agent to `allowed_tools_locks` in the discipline config with a justification",
                ))

        # R1c: model lock forbidden
        if "model" in fm:
            findings.append(Finding(
                rule="R1c-model-lock",
                severity=BLOCKER,
                file=str(rel),
                line=None,
                detail=f"agent `{name}` has a `model:` field — agents must inherit the orchestrator's model",
                fix="Remove the `model:` field; agents inherit the orchestrator's model by default",
            ))

        # R1d: Ground truth section
        if not re.search(r"^##\s+Ground truth", body, re.MULTILINE):
            findings.append(Finding(
                rule="R1d-ground-truth",
                severity=WARNING,
                file=str(rel),
                line=None,
                detail=f"agent `{name}` is missing a `## Ground truth` section",
                fix=f"Add a `## Ground truth` (or `## Ground truth (P6)`) section stating the agent must Read/Grep files before asserting facts",
            ))

    return findings


# ─── R2: Spawn discipline ──────────────────────────────────────────────────────

SPAWN_RE = re.compile(
    r"\bspawn\s+(?:a\s+|an\s+|the\s+|parallel\s+|one\s+|2-3\s+|3\s+|N\s+|fresh\s+|category-specific\s+)?"
    r"[`\"]?(tp-critic|tp-explorer|tp-researcher)\b",
    re.IGNORECASE,
)
ARG_RE = re.compile(
    r"\b(?:lens|scope|question)\b\s*[:=]?\s*[\"'`]",
    re.IGNORECASE,
)
W_LENS_RE = re.compile(r"\bw/\s*(?:a\s+|an\s+|distinct\s+|specific\s+)?(?:lens|scope|question)\b", re.IGNORECASE)


def audit_spawns(repo_root: Path, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    window = config["spawn_arg_window_chars"]
    plugins = repo_root / "plugins"

    for path in plugins.rglob("*.md"):
        if "/agents/" in str(path):
            continue  # agents don't spawn (the topology constraint)
        text = path.read_text()
        rel = path.relative_to(repo_root)
        for m in SPAWN_RE.finditer(text):
            # find the line number
            line_no = text.count("\n", 0, m.start()) + 1
            ahead = text[m.end():m.end() + window]
            if ARG_RE.search(ahead) or W_LENS_RE.search(ahead):
                continue  # argument present
            findings.append(Finding(
                rule="R2-spawn-arg",
                severity=WARNING,
                file=str(rel),
                line=line_no,
                detail=f"`spawn {m.group(1)}` without a lens/scope/question argument within {window} chars",
                fix=f"Add `(lens: \"...\")` / `(scope: \"...\")` / `(question: \"...\")` or `with lens \"...\"` next to the spawn directive",
            ))
    return findings


# ─── R3: Fork-skill discipline ─────────────────────────────────────────────────

def audit_fork_skills(repo_root: Path, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    required = config["required_fork_reference"]
    plugins = repo_root / "plugins"

    for skill_md in plugins.rglob("skills/*/SKILL.md"):
        text = skill_md.read_text()
        fm, _ = parse_frontmatter(text)
        if "context" not in fm:
            continue
        if str(fm["context"]).strip().lower() != "fork":
            continue
        skill_dir = skill_md.parent
        rationale = skill_dir / required
        if not rationale.exists():
            rel = skill_md.relative_to(repo_root)
            findings.append(Finding(
                rule="R3-fork-rationale",
                severity=WARNING,
                file=str(rel),
                line=None,
                detail=f"`context: fork` skill is missing `{required}`",
                fix=f"Add `{skill_md.parent.name}/{required}` citing what isolation value the fork provides (the noisy multi-step work it absorbs from the user's session)",
            ))
    return findings


# ─── R4: Description quality ───────────────────────────────────────────────────

VERB_RE = re.compile(
    r"^(Design|Build|Find|Search|Look|Manage|Test|Analyze|Analyse|Evaluate|Score|Review|Add|Run|Apply|"
    r"Investigate|Resolve|Optimize|Optimise|Refactor|Drive|Solve|Reason|Plan|Archive|Handle|Update|Verify|"
    r"Generate|Create|Compare|Spawn|Extract|Restructure|Read|Listen|Decompose|Implement|Explore|Use|Audit|Walk|Map|Locate|Discover|Scan|Simplify|Polish|Validate)",
    re.IGNORECASE,
)
CONTRAST_RE = re.compile(r"\b(?:NOT for|CONTRAST)\b", re.IGNORECASE)


def audit_descriptions(repo_root: Path, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    max_chars = config["description_max_chars"]
    first_n = config["verb_led_first_n_chars"]
    plugins = repo_root / "plugins"

    targets = list(plugins.rglob("skills/*/SKILL.md")) + list(plugins.rglob("agents/*.md")) + list(plugins.rglob("commands/*.md"))

    for path in targets:
        text = path.read_text()
        fm, body = parse_frontmatter(text)
        desc = str(fm.get("description", "")).strip()
        rel = path.relative_to(repo_root)
        if not desc:
            findings.append(Finding(
                rule="R4a-description-present",
                severity=BLOCKER,
                file=str(rel),
                line=None,
                detail=f"`{path.name}` is missing a `description:` field",
                fix="Add a `description:` field with user-vocabulary trigger phrases in the first 200 chars",
            ))
            continue
        if len(desc) > max_chars:
            findings.append(Finding(
                rule="R4b-description-length",
                severity=WARNING,
                file=str(rel),
                line=None,
                detail=f"`description` is {len(desc)} chars (cap {max_chars})",
                fix=f"Trim to ≤{max_chars} chars total (description + when_to_use combined)",
            ))
        if not VERB_RE.match(desc[:first_n]):
            findings.append(Finding(
                rule="R4c-description-verb-led",
                severity=NUDGE,
                file=str(rel),
                line=None,
                detail=f"`description` does not start with an action verb in the first {first_n} chars: {desc[:80]!r}",
                fix=f"Lead the description with an action verb (Design, Find, Build, Audit, ...)",
            ))
        # CONTRAST required for SKILL.md only (agents/commands are short).
        # The CONTRAST signal may live in the body (preferred) or in a when_to_use field (acceptable fallback).
        if path.name == "SKILL.md":
            in_body = CONTRAST_RE.search(body) is not None
            in_frontmatter = CONTRAST_RE.search(str(fm.get("when_to_use", ""))) is not None
            if not (in_body or in_frontmatter):
                findings.append(Finding(
                    rule="R4d-contrast",
                    severity=NUDGE,
                    file=str(rel),
                    line=None,
                    detail="SKILL.md has no CONTRAST section or 'NOT for' clause (in body or when_to_use)",
                    fix="Add a CONTRAST section listing adjacent-domain skills this one does NOT cover",
                ))
    return findings


# ─── R5: Catalog discipline ────────────────────────────────────────────────────

def audit_catalog(repo_root: Path, config: dict) -> list[Finding]:
    findings: list[Finding] = []
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.exists():
        return findings
    marketplace = json.loads(marketplace_path.read_text())
    by_name = {p["name"]: p for p in marketplace.get("plugins", [])}

    for plugin_dir in sorted((repo_root / "plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.exists():
            continue
        plugin = json.loads(manifest.read_text())
        name = plugin.get("name", plugin_dir.name)
        rel = str(manifest.relative_to(repo_root))

        # R5a: version matches marketplace entry
        catalog = by_name.get(name)
        if catalog is None:
            findings.append(Finding(
                rule="R5a-catalog-present",
                severity=BLOCKER,
                file=str(marketplace_path.relative_to(repo_root)),
                line=None,
                detail=f"plugin `{name}` has a plugin.json but is not in marketplace.json",
                fix="Run `python3 scripts/regenerate-marketplace.py` to add the plugin to the catalog",
            ))
        elif catalog.get("version") != plugin.get("version"):
            findings.append(Finding(
                rule="R5a-version-match",
                severity=BLOCKER,
                file=str(marketplace_path.relative_to(repo_root)),
                line=None,
                detail=f"plugin `{name}` version mismatch: plugin.json={plugin.get('version')} marketplace.json={catalog.get('version')}",
                fix="Run `python3 scripts/regenerate-marketplace.py` to sync versions",
            ))

        # R5b: description mentions agent roster
        desc = str(plugin.get("description", "")).lower()
        agents_dir = plugin_dir / "agents"
        agent_count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
        roster_threshold = config.get("roster_mention_threshold", 1)
        if agent_count == 0 and not re.search(r"\b(no specialist|0 specialist|tp-critic|inline|no named)\b", desc):
            findings.append(Finding(
                rule="R5b-roster-mention",
                severity=NUDGE,
                file=rel,
                line=None,
                detail=f"plugin `{name}` has 0 specialist agents (threshold {roster_threshold}) but its description doesn't say so",
                fix="Mention the agent roster in the description (e.g., 'reviews via tp-critic w/ lens') or the absence (e.g., 'no specialist agents')",
            ))
    return findings


# ─── Orchestration ─────────────────────────────────────────────────────────────

def run_audit(repo_root: Path, config: dict, strict: bool = False) -> list[Finding]:
    """Run the marketplace discipline audit.

    Default tier (structural): R1 agent roster, R3 fork-skill rationale, R5 catalog sync.
    Strict tier (--strict flag): also runs R2 spawn-lens contract and R4 description quality.
    The stylistic checks (R2, R4) are noisy — they produce false positives on multi-line
    directives and subjective verb choices. They belong behind an opt-in flag for maintainers
    who want to enforce writing style, not in the default CI gate.
    """
    findings: list[Finding] = []
    findings += audit_agents(repo_root, config)
    if strict:
        findings += audit_spawns(repo_root, config)
        findings += audit_descriptions(repo_root, config)
    findings += audit_fork_skills(repo_root, config)
    findings += audit_catalog(repo_root, config)
    return findings


def severity_rank(s: str) -> int:
    return {BLOCKER: 0, WARNING: 1, NUDGE: 2}.get(s, 3)


def render_markdown(repo_root: Path, findings: list[Finding]) -> str:
    if not findings:
        return f"# Discipline Audit Report\n\n**Marketplace:** `{repo_root}`\n**Verdict:** PASS — no findings\n"
    blockers = [f for f in findings if f.severity == BLOCKER]
    warnings = [f for f in findings if f.severity == WARNING]
    nudges = [f for f in findings if f.severity == NUDGE]
    verdict = "FAIL" if blockers else ("WARN" if warnings else "PASS")
    out = [
        f"# Discipline Audit Report",
        "",
        f"**Marketplace:** `{repo_root}`",
        f"**Verdict:** {verdict}  ({len(blockers)} blocker, {len(warnings)} warning, {len(nudges)} nudge)",
        "",
    ]
    for sev in (BLOCKER, WARNING, NUDGE):
        bucket = [f for f in findings if f.severity == sev]
        if not bucket:
            continue
        out.append(f"## {sev}")
        out.append("")
        for f in sorted(bucket, key=lambda x: (x.rule, str(x.file), x.line or 0)):
            loc = f"`{f.file}`" + (f":{f.line}" if f.line else "")
            out.append(f"- **{f.rule}** @ {loc} — {f.detail}")
            out.append(f"  - fix: {f.fix}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Marketplace discipline audit")
    parser.add_argument("marketplace_root", nargs="?", default=None,
                        help="Path to the marketplace repo root (default: git repo root)")
    parser.add_argument("--ci", action="store_true",
                        help="Machine-readable JSON output for CI; exit 1 on BLOCKER")
    parser.add_argument("--strict", action="store_true",
                        help="Also run stylistic checks (R2 spawn-lens, R4 description quality). "
                             "Default omits these because they produce false positives on multi-line "
                             "directives and subjective verb choices. Use --strict to enforce writing style.")
    parser.add_argument("--config", default=None,
                        help="Path to a discipline config JSON")
    args = parser.parse_args()

    repo_root = Path(args.marketplace_root).resolve() if args.marketplace_root else Path(__file__).resolve().parent.parent
    config = dict(DEFAULT_CONFIG)
    if args.config:
        config.update(json.loads(Path(args.config).read_text()))

    try:
        findings = run_audit(repo_root, config, strict=args.strict)
    except Exception as e:  # noqa: BLE001
        if args.ci:
            print(json.dumps({"status": "crashed", "error": str(e)}))
        else:
            print(f"AUDIT CRASHED: {e}", file=sys.stderr)
        return 2

    if args.ci:
        payload = {
            "status": "complete",
            "marketplace": str(repo_root),
            "verdict": "FAIL" if any(f.severity == BLOCKER for f in findings) else "PASS",
            "findings": [f.as_dict() for f in findings],
            "summary": {
                "blocker": sum(1 for f in findings if f.severity == BLOCKER),
                "warning": sum(1 for f in findings if f.severity == WARNING),
                "nudge": sum(1 for f in findings if f.severity == NUDGE),
            },
        }
        print(json.dumps(payload, indent=2))
        return 1 if payload["verdict"] == "FAIL" else 0

    print(render_markdown(repo_root, findings))
    return 1 if any(f.severity == BLOCKER for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())