#!/usr/bin/env python3
"""Generate OpenCode V2 and VS Code agent files from a single source.

Source:  agents/<name>.md  (flat YAML frontmatter + Markdown body = prompt)
Outputs: .opencode/agents/<name>.md       (OpenCode V2 Markdown agent)
         .github/agents/<name>.agent.md   (VS Code custom agent)

Usage:   python3 scripts/sync-agents.py [--check] [--root DIR]
  --check  write nothing; exit 1 if any output is missing, stale or orphaned, or if DENY_SHELL
           differs from the shell deny rules of an existing opencode.json (drift check).

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


# Hard shell denies: force pushes in every form (-f, --force*, incl. --force-with-lease, + refspec,
# also with options before `push` such as `git -C x push`) and repository deletion. Keep this tuple
# EQUAL to the shell deny rules of the global config (opencode.json); `--check` fails on drift.
# A role that re-asks `shell *` (inspector) re-appends them AFTER its ask (the last match wins).
DENY_SHELL = (
    "git push --force*", "git push -f *", "git push * --force*", "git push * -f", "git push * -f *",
    "git push +*", "git push * +*",
    "git * push --force*", "git * push -f *", "git * push * --force*", "git * push * -f",
    "git * push * -f *", "git * push +*", "git * push * +*",
    "gh repo delete *",
)

_GIT_FLOW = ("switch", "checkout", "add", "commit", "push")
_GIT_OTHER = ("merge", "rebase", "reset", "stash", "rm", "mv", "tag", "restore", "cherry-pick",
              "revert", "pull", "clean", "apply", "am")
_BRANCH_WRITE = ("-d", "-D", "-f", "-m", "-M", "-c", "-C", "--delete", "--force", "--move",
                 "--copy", "-u", "--set-upstream-to", "--unset-upstream", "--edit-description")
_BRANCH_READ_EXACT = ("", " -v", " -vv", " -a", " -r", " --show-current")  # no arguments: list only
_BRANCH_READ_PREFIX = ("--list*", "--contains *", "--merged *", "--no-merged *")
_HTTP_WRITES = ("POST", "PUT", "PATCH", "DELETE")
_GH_COMMON = ("gh pr merge*", "gh pr edit*", "gh pr close*", "gh pr review*", "gh issue *",
              "gh release *", "gh workflow *", "gh repo *", "gh secret *", "gh variable *", "gh label *")
_FILES = ("rm *", "mv *", "cp *", "tee *", "sed -i*", "sed * -i*", "sed --in-place*", "sed * --in-place*")


def _git_denies(subs):
    # Whole subcommand only (`git merge *`, which also matches bare `git merge`), so `git merge-base`
    # and `git diff -- tags.md` stay allowed. `git -C x <sub>` / `git -c k=v <sub>` are NOT covered:
    # a wildcard spanning arguments would also deny reads such as `git -C x log --grep merge`.
    return [f"git {sub} *" for sub in subs]


def _gh_api_denies():
    flags = ("-X", "--method")
    return ([f"gh api {f} {m}*" for f in flags for m in _HTTP_WRITES]
            + [f"gh api * {f} {m}*" for f in flags for m in _HTTP_WRITES] + ["gh api *--input*"])


def _deny(patterns):
    return [(c, "deny") for c in patterns]


# Read-only roles (reviewer, planner): appended LAST so these agent-level denies win over the global
# allow. Reads (gh pr diff/view, gh api GET, git show/log/diff, cat, grep, ls) stay allowed.
REVIEWER_SHELL_RULES = tuple(
    _deny(_git_denies(_GIT_FLOW + _GIT_OTHER))
    + _deny(["git branch *"])
    + [(f"git branch{f}", "allow") for f in _BRANCH_READ_EXACT]
    + [(f"git branch {f}", "allow") for f in _BRANCH_READ_PREFIX]
    + _deny(list(_GH_COMMON) + ["gh pr create*", "gh pr comment*"] + _gh_api_denies() + list(_FILES))
)

# docs role: still branches, commits, pushes, opens a PR, comments and merges the remote default
# branch into its own branch; everything else of the reviewer list stays denied (cp allowed).
DOCS_SHELL_RULES = tuple(
    _deny(_git_denies(_GIT_OTHER))
    + [("git merge origin/*", "allow"), ("git merge --no-edit origin/*", "allow")]
    + _deny([f"git branch {f}*" for f in _BRANCH_WRITE])
    + _deny(list(_GH_COMMON) + _gh_api_denies() + [f for f in _FILES if f != "cp *"])
)


def global_shell_denies(root):
    """Shell deny patterns of the repo's opencode.json, or None when there is no such file."""
    cfg_path = pathlib.Path(root) / "opencode.json"
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return [r["resource"] for r in cfg.get("permissions", [])
            if r.get("action") == "shell" and r.get("effect") == "deny"]


def rule(action, resource, effect):
    return {"action": action, "resource": resource, "effect": effect}


def role_permissions(role):
    """OpenCode V2 ordered rules (last match wins); every role may ask the owner (`question`).

    Agent rules are appended AFTER the global rules, so a broad agent-level rule overrides global
    exceptions. Roles therefore never carry a broad `shell *` allow, and only the inspector carries a
    broad `shell *` ask (followed by DENY_SHELL); reviewer/planner get REVIEWER_SHELL_RULES and docs
    DOCS_SHELL_RULES appended last; other roles rely on the global shell rules.
    """
    return _role_rules(role) + [rule("question", "*", "allow")]


def _role_rules(role):
    if role in ("reviewer", "planner"):
        return ([rule("edit", "*", "deny")] + [rule("shell", c, "allow") for c in READ_ONLY_SHELL]
                + [rule("shell", c, e) for c, e in REVIEWER_SHELL_RULES])
    if role == "inspector":  # keeps `shell ask` on purpose: every remote/read command is approved
        return [rule("edit", "*", "deny"), rule("shell", "*", "ask")] + [
            rule("shell", c, "deny") for c in DENY_SHELL
        ]
    if role == "orchestrator":  # docs-only edits, read-only shell allows, may launch every subagent
        return [
            rule("edit", "*", "deny"),
            rule("edit", "*.md", "allow"),
            rule("edit", "docs/*", "allow"),
        ] + [rule("shell", c, "allow") for c in ORCHESTRATOR_SHELL] + [rule("subagent", "*", "allow")]
    if role == "docs":
        return ([rule("edit", "*", "deny"), rule("edit", "*.md", "allow")]
                + [rule("shell", c, e) for c, e in DOCS_SHELL_RULES])
    return [rule("edit", "*", "allow")]  # implementer: full edit (global shell rules still apply)


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


def shell_rule_problems(rules, role):
    """Problems in an agent's generated rules: broad shell allow, stray broad ask, missing re-denies."""
    problems, asked = [], False
    for i, r in enumerate(rules):
        if r["action"] != "shell" or r["resource"] not in ("*", "**"):
            continue
        if r["effect"] == "allow":
            problems.append("broad `shell *` allow (would override every global ask/deny)")
        elif r["effect"] == "ask":
            if role != "inspector":
                problems.append("broad `shell *` ask outside the inspector role (global rules apply)")
            later = {x["resource"] for x in rules[i + 1:] if x["action"] == "shell" and x["effect"] == "deny"}
            missing = [d for d in DENY_SHELL if d not in later]
            if missing:
                problems.append("`shell *` ask not followed by the shell denies: " + ", ".join(missing))
            asked = True
    if role == "inspector" and not asked:
        problems.append("inspector must keep `shell *` ask")
    return problems


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
        denies = global_shell_denies(root)
        if denies is not None and denies != list(DENY_SHELL):
            print("error: DENY_SHELL differs from the shell deny rules in opencode.json "
                  "(keep both equal, in the same order)", file=sys.stderr)
            return 1
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
