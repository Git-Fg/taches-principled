#!/usr/bin/env python3
"""Session start coaching + .principled directory awareness."""
import json
import os
import sys
from pathlib import Path


def build_tree(root_path: Path) -> str:
    """Build a tree-like representation of a directory."""
    lines = []
    if not root_path.exists():
        return ""

    entries = sorted(root_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        prefix = "└── " if is_last else "├── "
        lines.append(f"{prefix}{entry.name}")
        if entry.is_dir():
            subtree = build_subtree(entry, "    " if is_last else "│   ")
            lines.extend(subtree)
    return "\n".join(lines)


def build_subtree(dir_path: Path, indent: str) -> list:
    """Recursively build subtree lines with proper indentation."""
    lines = []
    try:
        entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{indent}{branch}{entry.name}")
            if entry.is_dir():
                next_indent = indent + ("    " if is_last else "│   ")
                lines.extend(build_subtree(entry, next_indent))
    except PermissionError:
        pass
    return lines


def extract_snippets(file_path: Path) -> str:
    """Extract first 5 + last 5 lines from a markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
    except (OSError, UnicodeDecodeError):
        return ""

    if not content:
        return ""

    first = content[:5]
    last = content[-5:] if len(content) > 5 else []

    snippet_parts = []
    snippet_parts.append("[start]")
    snippet_parts.extend(line.rstrip() for line in first)
    if len(content) > 10:
        snippet_parts.append("[...]")
    snippet_parts.extend(line.rstrip() for line in last)
    snippet_parts.append("[end]")

    return "\n".join(snippet_parts)


def scan_principled(principled_dir: Path) -> tuple[str, list]:
    """Scan .principled directory and return tree + file snippets."""
    tree = build_tree(principled_dir)
    snippets = []
    try:
        for md_file in sorted(principled_dir.rglob("*.md")):
            rel_path = md_file.relative_to(principled_dir)
            snippet = extract_snippets(md_file)
            if snippet:
                snippets.append(f"\n### {rel_path}\n```\n{snippet}\n```")
    except (OSError, PermissionError):
        pass
    return tree, snippets


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    # Base coaching message
    coaching = (
        "Before spawning subagents, verify three gates: "
        "(1) Is this task non-trivial? (2) Are parts independent and parallelizable? "
        "(3) Will delegation save total work, or just shift it? "
        "Skip delegation if any answer is no. "
        "Subagent fan-out is a cost-bearing decision, not a default."
    )

    # Dynamic .principled awareness
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        principled_path = Path(project_dir) / ".principled"
    else:
        principled_path = Path.cwd() / ".principled"

    if principled_path.exists():
        tree, snippets = scan_principled(principled_path)
        if tree:
            principled_section = f"\n\n## Project State (.principled)\n```\n{tree}\n```"
            if snippets:
                principled_section += "\n\n### File Previews" + "".join(snippets)
            coaching += principled_section

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": coaching
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
