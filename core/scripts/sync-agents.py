#!/usr/bin/env python3
"""Generate OpenCode V2 and VS Code agent files from a single source.

Source:  agents/<name>.md  (flat YAML frontmatter + Markdown body = prompt)
Outputs: .opencode/agents/<name>.md       (OpenCode V2 Markdown agent)
         .github/agents/<name>.agent.md   (VS Code custom agent)

Usage:   python3 scripts/sync-agents.py [--check] [--root DIR]
  --check  write nothing; exit 1 if any output is missing, stale or orphaned.

Repo-agnostic: copy this file verbatim into any repo. Standard library only.

Source frontmatter (flat, one `key: value` per line, no nesting):
  name               required; must equal the file name without .md
  description        required
  role               required; implementer | reviewer | planner | inspector | docs | orchestrator
  model              optional; OpenCode `provider/model[#variant]` (VS Code: omitted)
  mode               optional; subagent (default; orchestrator: primary) | primary | all
  extra_permissions  optional; OpenCode rules appended after the role rules,
                     `action|resource|effect` separated by `;`
                     e.g. `shell|make lint *|allow; edit|*.sql|ask`
"""
import argparse
import json
import pathlib
import sys

ROLES = ("implementer", "reviewer", "planner", "inspector", "docs", "orchestrator")
MODES = ("subagent", "primary", "all")
EFFECTS = ("allow", "ask", "deny")
KEYS = ("name", "description", "role", "model", "mode", "extra_permissions")

READ_ONLY_SHELL = (
    "git status *", "git diff *", "git log *", "git show *",
    "gh issue view *", "gh pr view *", "gh pr diff *",
)
ORCHESTRATOR_SHELL = READ_ONLY_SHELL + ("gh issue list *", "gh pr list *", "gh pr checks *")


def rule(action, resource, effect):
    return {"action": action, "resource": resource, "effect": effect}


def role_permissions(role):
    """OpenCode V2 ordered rules (last match wins); every role may ask the owner (`question`)."""
    return _role_rules(role) + [rule("question", "*", "allow")]


def _role_rules(role):
    if role in ("reviewer", "planner"):
        return [rule("edit", "*", "deny"), rule("shell", "*", "ask")] + [
            rule("shell", c, "allow") for c in READ_ONLY_SHELL
        ]
    if role == "inspector":
        return [rule("edit", "*", "deny"), rule("shell", "*", "ask")]
    if role == "orchestrator":  # docs-only edits, read-only shell, may launch every subagent
        return [
            rule("edit", "*", "deny"),
            rule("edit", "*.md", "allow"),
            rule("edit", "docs/*", "allow"),
            rule("shell", "*", "ask"),
        ] + [rule("shell", c, "allow") for c in ORCHESTRATOR_SHELL] + [rule("subagent", "*", "allow")]
    if role == "docs":
        return [
            rule("edit", "*", "deny"),
            rule("edit", "*.md", "allow"),
            rule("shell", "*", "ask"),
        ]
    return [rule("edit", "*", "allow")]  # implementer: full (global rules still apply)


def vscode_tools(role):
    """VS Code tool aliases; None = omit field (all enabled tools)."""
    tools = {
        "reviewer": ["read", "search"],
        "planner": ["read", "search", "web"],
        "inspector": ["read", "search", "execute"],
        "docs": ["read", "search", "edit", "todo"],
        "orchestrator": ["read", "search", "edit", "web", "todo", "agent"],
    }.get(role)
    # vscode/askQuestions: documented VS Code tool to ask the user structured questions
    return None if tools is None else tools + ["vscode/askQuestions"]


def default_mode(role):
    return "primary" if role == "orchestrator" else "subagent"


def parse(path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")
    meta, end = {}, None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError(f"{path}:{i + 1}: frontmatter must be flat `key: value`")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key not in KEYS:
            raise ValueError(f"{path}:{i + 1}: unknown key {key!r} (allowed: {', '.join(KEYS)})")
        meta[key] = value
    if end is None:
        raise ValueError(f"{path}: unterminated frontmatter")
    for key in ("name", "description", "role"):
        if not meta.get(key):
            raise ValueError(f"{path}: missing required key {key!r}")
    if meta["name"] != path.stem:
        raise ValueError(f"{path}: name {meta['name']!r} must equal file name {path.stem!r}")
    if meta["role"] not in ROLES:
        raise ValueError(f"{path}: role must be one of {ROLES}")
    if meta.get("mode", default_mode(meta["role"])) not in MODES:
        raise ValueError(f"{path}: mode must be one of {MODES}")
    body = "\n".join(lines[end + 1:]).strip() + "\n"
    return meta, body


def extra_rules(meta, path):
    out = []
    for chunk in filter(None, (c.strip() for c in meta.get("extra_permissions", "").split(";"))):
        parts = [p.strip() for p in chunk.split("|")]
        if len(parts) != 3 or parts[2] not in EFFECTS:
            raise ValueError(f"{path}: bad extra_permissions entry {chunk!r}")
        out.append(rule(*parts))
    return out


def q(value):
    return json.dumps(value, ensure_ascii=False)  # JSON string == valid YAML scalar


def header(name):
    return f"# GENERATED from agents/{name}.md — edit the source, then run python3 scripts/sync-agents.py"


def render_opencode(meta, body, path):
    out = ["---", header(meta["name"]), f"description: {q(meta['description'])}",
           f"mode: {meta.get('mode', default_mode(meta['role']))}"]
    if meta.get("model"):
        out.append(f"model: {meta['model']}")
    out.append("permissions:")
    for r in role_permissions(meta["role"]) + extra_rules(meta, path):
        out += [f"  - action: {r['action']}", f"    resource: {q(r['resource'])}",
                f"    effect: {r['effect']}"]
    out.append("---")
    return "\n".join(out) + "\n" + body


def render_vscode(meta, body):
    out = ["---", header(meta["name"]), f"name: {meta['name']}",
           f"description: {q(meta['description'])}"]
    tools = vscode_tools(meta["role"])
    if tools is not None:
        out.append("tools: [" + ", ".join(f"'{t}'" for t in tools) + "]")
    if meta["role"] == "orchestrator":
        out.append("agents: ['*']")  # VS Code Local: may run every custom agent as a subagent
    out.append("---")
    return "\n".join(out) + "\n" + body


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    src_dir = root / "agents"
    oc_dir, vs_dir = root / ".opencode" / "agents", root / ".github" / "agents"
    sources = sorted(src_dir.glob("*.md"))
    if not sources:
        print(f"no sources in {src_dir}", file=sys.stderr)
        return 1
    wanted = {}
    try:
        for path in sources:
            meta, body = parse(path)
            wanted[oc_dir / f"{path.stem}.md"] = render_opencode(meta, body, path)
            wanted[vs_dir / f"{path.stem}.agent.md"] = render_vscode(meta, body)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    existing = set(oc_dir.glob("*.md")) | set(vs_dir.glob("*.agent.md"))
    orphans = sorted(existing - set(wanted))
    stale = [p for p, c in wanted.items()
             if not p.exists() or p.read_text(encoding="utf-8") != c]
    if args.check:
        for p in stale:
            print(f"stale: {p.relative_to(root)}", file=sys.stderr)
        for p in orphans:
            print(f"orphan: {p.relative_to(root)}", file=sys.stderr)
        if stale or orphans:
            print("run: python3 scripts/sync-agents.py", file=sys.stderr)
            return 1
        print(f"ok: {len(sources)} agents in sync")
        return 0
    oc_dir.mkdir(parents=True, exist_ok=True)
    vs_dir.mkdir(parents=True, exist_ok=True)
    for p in stale:
        p.write_text(wanted[p], encoding="utf-8")
        print(f"wrote {p.relative_to(root)}")
    for p in orphans:
        p.unlink()
        print(f"removed {p.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
