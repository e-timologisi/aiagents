#!/usr/bin/env python3
"""Generate VS Code prompt files (prompts/vscode/*.prompt.md) from prompts/NN-*.md.

Usage: python3 scripts/build-prompts.py [--check]

Source format: first line `<!-- vscode: agent=<agent>; hint=<argument hint> -->`, a `# NN — Title`
heading, a `**When to use:** ...` line and a `## Prompt` section with one ````text fenced block.
Output frontmatter uses only documented fields (name, description, argument-hint, agent):
https://code.visualstudio.com/docs/agent-customization/prompt-files
`<UPPER_SNAKE>` placeholders become `${input:lower_snake}` input variables.
"""
import argparse
import pathlib
import re
import sys

KIT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = KIT / "prompts", KIT / "prompts" / "vscode"
META = re.compile(r"<!--\s*vscode:\s*agent=([\w-]+);\s*hint=(.*?)\s*-->")
VAR = re.compile(r"<([A-Z][A-Z0-9_]*)>")


def q(s):
    return "'" + s.replace("'", "''") + "'"


def build(path):
    text = path.read_text(encoding="utf-8")
    meta = META.search(text.splitlines()[0])
    title = re.search(r"^# \d+ — (.+)$", text, re.M)
    when = re.search(r"^\*\*When to use:\*\* (.+)$", text, re.M)
    body = re.search(r"^## Prompt\s*\n+````text\n(.*?)\n````", text, re.M | re.S)
    if not (meta and title and when and body):
        raise ValueError(f"{path}: needs vscode comment, title, 'When to use' and a ````text prompt block")
    name = re.sub(r"^\d+-", "", path.stem)
    prompt = VAR.sub(lambda m: "${input:" + m.group(1).lower() + "}", body.group(1))
    return name, "\n".join([
        "---",
        f"name: {name}",
        f"description: {q(title.group(1) + ' — ' + when.group(1))}",
        f"argument-hint: {q(meta.group(2))}",
        f"agent: {meta.group(1)}",
        "---",
        f"<!-- GENERATED from prompts/{path.name} by scripts/build-prompts.py -->",
        prompt,
        "",
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    wanted = {}
    try:
        for p in sorted(SRC.glob("[0-9][0-9]-*.md")):
            name, content = build(p)
            wanted[OUT / f"{name}.prompt.md"] = content
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    existing = set(OUT.glob("*.prompt.md"))
    stale = [p for p, c in wanted.items() if not p.exists() or p.read_text(encoding="utf-8") != c]
    orphans = sorted(existing - set(wanted))
    if args.check:
        for p in stale + orphans:
            print(f"out of date: {p.relative_to(KIT)}", file=sys.stderr)
        if stale or orphans:
            return 1
        print(f"ok: {len(wanted)} VS Code prompt files in sync")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for p in stale:
        p.write_text(wanted[p], encoding="utf-8")
        print(f"wrote {p.relative_to(KIT)}")
    for p in orphans:
        p.unlink()
        print(f"removed {p.relative_to(KIT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
