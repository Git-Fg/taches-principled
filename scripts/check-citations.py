#!/usr/bin/env python3
"""
Audit subagent citation patterns across the marketplace.

Three classes of audit, all run together for a single verdict:

  1. Cross-skill citation violations
     An agent body cites a `references/FILENAME.md` from a skill it has NOT
     loaded. Forbidden by CLAUDE.md Rule 4 (skill-scope only). The agent
     cannot resolve the citation without template resolution it doesn't have.

  2. Missing-skill preload violations
     An agent's `skills:` frontmatter lists a skill that does not exist
     anywhere in the marketplace. Either a typo, a deleted skill, or an
     aspirational preload. Either way: the agent gets nothing from that
     preload slot, and any reference it cites from that "skill" is
     guaranteed unresolved.

  3. Broken reference citations
     An agent body cites a `references/FILENAME.md` that does not exist in
     ANY plugin's references/ directory. Either the file was deleted, the
     citation is wrong, or the file was never shipped.

When to run:
  - After authoring or modifying any agent definition
  - After splitting a skill into hub + references/
  - After deleting or renaming a reference file
  - Before committing any change that touches agents/ or skills/

How to verify clean:
  python3 scripts/check-citations.py
  exit code 0 = no findings; exit code 1 = at least one finding

CI: a workflow can run this script on every PR touching plugins/.

Output format:
  - Grouped by class
  - File:line of the agent (line is the skills: array line)
  - The offending skill name or reference path
  - A one-line explanation

This script complements the marketplace jq schema checks in
regenerate-marketplace.py and the CHANGELOG/commit conventions in CLAUDE.md.
"""

import os
import re
import sys
import pathlib
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
PLUGINS_DIR = REPO_ROOT / "plugins"


def parse_frontmatter(path: pathlib.Path) -> dict:
    """Return the YAML frontmatter dict, or {} if no frontmatter."""
    text = path.read_text()
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def find_skill_locations() -> dict:
    """Map skill name → list of plugin directories that ship it."""
    locs = defaultdict(list)
    for skill_md in PLUGINS_DIR.glob("*/skills/*/SKILL.md"):
        skill_name = skill_md.parent.name
        plugin_dir = skill_md.parents[1]
        locs[skill_name].append(plugin_dir)
    return dict(locs)


def find_reference_locations() -> dict:
    """Map reference filename (basename) → list of absolute paths."""
    locs = defaultdict(list)
    for ref in PLUGINS_DIR.glob("*/skills/*/references/*.md"):
        locs[ref.name].append(ref)
    return dict(locs)


def get_cited_references(agent_path: pathlib.Path) -> set:
    """Return set of `references/FILENAME.md` strings cited in an agent body."""
    text = agent_path.read_text()
    return set(re.findall(r'`references/([a-zA-Z0-9_-]+\.md)`', text))


def get_preloaded_skills(agent_path: pathlib.Path) -> list:
    """Return the list of skills in an agent's `skills:` frontmatter."""
    return parse_frontmatter(agent_path).get("skills") or []


def audit() -> int:
    skill_locs = find_skill_locations()
    ref_locs = find_reference_locations()

    class1_cross_skill = []  # (agent, cited_ref, preloaded_skills)
    class2_missing_skill = []  # (agent, missing_skill)
    class3_broken_ref = []  # (agent, cited_ref)

    for agent_path in sorted(PLUGINS_DIR.glob("*/agents/*.md")):
        preloaded = get_preloaded_skills(agent_path)
        cited = get_cited_references(agent_path)

        # Class 2: missing skill preload
        for skill in preloaded:
            if skill not in skill_locs:
                class2_missing_skill.append((agent_path, skill))

        # Class 1: cross-skill citation (cited ref not reachable from preloaded skills)
        for ref_basename in cited:
            if ref_basename not in ref_locs:
                # Class 3: cited ref doesn't exist anywhere
                class3_broken_ref.append((agent_path, f"references/{ref_basename}"))
                continue
            # Is this ref reachable from at least one preloaded skill?
            reachable = False
            for s in preloaded:
                for sdir in skill_locs.get(s, []):
                    for r in ref_locs[ref_basename]:
                        if str(r).startswith(str(sdir)):
                            reachable = True
                            break
                    if reachable:
                        break
                if reachable:
                    break
            if not reachable:
                class1_cross_skill.append((
                    agent_path,
                    f"references/{ref_basename}",
                    preloaded,
                    [str(p) for p in ref_locs[ref_basename]],
                ))

    # Report
    has_findings = bool(class1_cross_skill or class2_missing_skill or class3_broken_ref)

    if not has_findings:
        print("PASS: no citation violations, no missing preloads, no broken references")
        return 0

    if class2_missing_skill:
        print(f"\n[2] MISSING-SKILL PRELOADS ({len(class2_missing_skill)} found)")
        print("    Agent declares a skill in `skills:` that does not exist anywhere.")
        print("    Either a typo, a deleted skill, or an aspirational preload.")
        for agent, skill in class2_missing_skill:
            rel = agent.relative_to(REPO_ROOT)
            print(f"    - {rel}: skills: [{skill!r}] (skill not found in marketplace)")

    if class3_broken_ref:
        print(f"\n[3] BROKEN REFERENCE CITATIONS ({len(class3_broken_ref)} found)")
        print("    Agent body cites a references/ file that does not exist in any plugin.")
        for agent, ref in class3_broken_ref:
            rel = agent.relative_to(REPO_ROOT)
            print(f"    - {rel}: cites `{ref}` (file does not exist)")

    if class1_cross_skill:
        print(f"\n[1] CROSS-SKILL CITATION VIOLATIONS ({len(class1_cross_skill)} found)")
        print("    Agent cites a references/ file from a skill it has NOT preloaded.")
        print("    Per CLAUDE.md Rule 4, only preloaded skills may be cited from a subagent body.")
        for agent, ref, preloaded, ref_paths in class1_cross_skill:
            rel = agent.relative_to(REPO_ROOT)
            print(f"    - {rel}: cites `{ref}`")
            print(f"        preloaded: {preloaded}")
            print(f"        ref lives in: {[os.path.relpath(p, REPO_ROOT) for p in ref_paths]}")

    print(f"\nFAIL: {len(class1_cross_skill)} cross-skill + {len(class2_missing_skill)} missing-skill + {len(class3_broken_ref)} broken-ref findings")
    return 1


if __name__ == "__main__":
    sys.exit(audit())
