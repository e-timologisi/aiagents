#!/usr/bin/env python3
"""Validate the aiagents kit.

Usage: python3 scripts/check-kit.py

Checks:
  - every skill directory has SKILL.md with frontmatter name == directory and a description
  - every agent has an Access paragraph; the lead carries the conflict-prevention and access rules
  - every agent source parses with core/scripts/sync-agents.py rules
  - every {{PLACEHOLDER}} is declared in its scope (core/placeholders.yaml + type.yaml or pack.yaml)
  - type.yaml / pack.yaml names match their directory; repo types have the required files
  - VS Code prompt files are in sync with prompts/*.md
  - core/commands/*.md (the /setup command) parse and render for OpenCode and VS Code; /setup keeps
    its interview rules (one question at a time, no secrets, access summary); lean profile names exist
  - third-party attribution: every directory with UPSTREAM.md has LICENSE.upstream and is listed in
    THIRD-PARTY-NOTICES.md, which reproduces every upstream MIT license in full
  - process gates: handover-rules/autonomy/decision-log/retro templates, CI templates and scripts exist;
    new placeholders are used; handover-check.sh contains no mutating gh/git command; every workflow
    and CI template pins actions to a commit SHA
  - generated role permissions never contain a broad shell allow; only the inspector re-asks `shell *`
    and re-appends the shell denies after it; the recipe's shell denies equal DENY_SHELL (drift check)
  - no forbidden strings: built-in generic patterns (12-digit AWS account ids, ARNs, IPv4 addresses,
    GitHub tokens, Google OAuth secrets, private keys, password literals, home directory paths,
    hosted tracker sites) plus optional local regexes
    from the untracked `.kit-forbidden.txt` (one per line; put your own domains/org names there)
"""
import importlib.util
import re
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kitlib import (KIT, LEAN_AGENTS, LEAN_SKILLS, PLACEHOLDER, check_attribution, declared,  # noqa: E402
                    frontmatter, mutating_lines, parse_yaml, render_command, scan_forbidden)

REQUIRED_FILES = [
    "core/agents/lead.md", "core/agents/explorer.md", "core/agents/ticket-tracker.md",
    "core/docs-templates/access-and-conflicts.md.tmpl", "core/commands/setup.md",
    "core/docs-templates/handover-rules.md.tmpl", "core/docs-templates/autonomy-policy.md.tmpl",
    "core/docs-templates/decision-log.md.tmpl", "core/docs-templates/retro-template.md",
    "core/scripts/handover-check.sh", "core/scripts/check-pinned-actions.py",
    "core/ci-templates/agent-report.yml.tmpl", "core/ci-templates/pinned-actions.yml.tmpl",
    "core/ci-templates/ticket-key.yml.tmpl", "core/docs-templates/work-log.md", "core/docs-templates/interaction-standard.md.tmpl", "HOWTO.md", "prompts/00-start-here.md",
] + [f"core/skills/{s}/SKILL.md" for s in (
    "project-intake", "document-ingest", "requirements-register", "backlog-planning", "dispatch-tasks",
    "status-report", "project-state", "codebase-discovery", "project-setup", "release-checklist",
)] + [f"core/docs-templates/project/{t}" for t in (
    "project-brief.md.tmpl", "requirements-register.md.tmpl", "project-state.md.tmpl",
    "status-report.md.tmpl", "decision-brief.md.tmpl", "project-dossier.md.tmpl", "worked-examples.md",
)]
ONE_QUESTION_SKILLS = (
    "project-intake", "document-ingest", "requirements-register", "backlog-planning", "dispatch-tasks",
    "status-report", "project-state", "codebase-discovery", "task-intake", "project-setup",
)
SETUP_NEEDLES = ("one question at a time", "never ask for", "servers, databases and credentials are never",
                 ".aiagents/access.md", "--profile lean", "--detect", "local-<n>", "commit locally",
                 "handover gate", "pinned-actions guard", "autonomy policy")
NEW_PLACEHOLDERS = ("AGENT_REPORT_LABEL", "AGENT_REPORT_AUTHORS", "MAX_PARALLEL_AGENTS", "EXPECTED_CHECKS")
TYPE_FILES = ("type.yaml", "AGENTS.md.tmpl", "CONTRIBUTING.md.tmpl", "README.md.tmpl")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_sync():
    return load_module("sync_agents", KIT / "core" / "scripts" / "sync-agents.py")


def text_files(root):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix not in (".py", ".sh", ".pyc") and p.name != ".DS_Store":
            yield p


def main():
    errors = []
    sync = load_sync()
    core_names = declared(parse_yaml(KIT / "core" / "placeholders.yaml")) | {"TARGET_DIR_NAME"}
    scopes = [(KIT / "core", core_names), (KIT / "prompts", set())]

    for d in sorted((KIT / "repo-types").iterdir()):
        if not d.is_dir():
            continue
        for f in TYPE_FILES:
            if not (d / f).exists():
                errors.append(f"repo-types/{d.name}: missing {f}")
        if (d / "type.yaml").exists():
            spec = parse_yaml(d / "type.yaml")
            if spec.get("name") != d.name:
                errors.append(f"repo-types/{d.name}/type.yaml: name must be {d.name!r}")
            scopes.append((d, core_names | declared(spec)))
    for d in sorted((KIT / "packs").iterdir()):
        if not d.is_dir():
            continue
        for f in ("pack.yaml", "README.md"):
            if not (d / f).exists():
                errors.append(f"packs/{d.name}: missing {f}")
        if (d / "pack.yaml").exists():
            spec = parse_yaml(d / "pack.yaml")
            if spec.get("name") != d.name:
                errors.append(f"packs/{d.name}/pack.yaml: name must be {d.name!r}")
            scopes.append((d, core_names | declared(spec)))

    skills = agents = 0
    for base, _ in scopes:
        for sdir in sorted((base / "skills").glob("*")) if (base / "skills").is_dir() else []:
            skills += 1
            meta = frontmatter(sdir / "SKILL.md") if (sdir / "SKILL.md").exists() else None
            rel = sdir.relative_to(KIT)
            if meta is None:
                errors.append(f"{rel}: missing SKILL.md or frontmatter")
            elif meta.get("name") != sdir.name:
                errors.append(f"{rel}/SKILL.md: name {meta.get('name')!r} must equal {sdir.name!r}")
            elif not meta.get("description"):
                errors.append(f"{rel}/SKILL.md: missing description")
        for a in sorted((base / "agents").glob("*.md")) if (base / "agents").is_dir() else []:
            agents += 1
            try:
                meta, _ = sync.parse(a)
                rules = sync.role_permissions(meta["role"]) + sync.extra_rules(meta, a)
                for problem in sync.shell_rule_problems(rules, meta["role"]):
                    errors.append(f"{a.relative_to(KIT)}: permissions: {problem}")
            except ValueError as err:
                errors.append(str(err).replace(str(KIT) + "/", ""))
            lines = len(a.read_text(encoding="utf-8").splitlines())
            limit = 95 if (frontmatter(a) or {}).get("role") == "orchestrator" else 65
            if lines > limit:
                errors.append(f"{a.relative_to(KIT)}: {lines} lines (limit {limit})")

    for rel in REQUIRED_FILES:
        if not (KIT / rel).exists():
            errors.append(f"missing required kit file: {rel}")
    roles = getattr(sync, "ROLES", ())
    if "orchestrator" not in roles:
        errors.append("core/scripts/sync-agents.py: role 'orchestrator' missing")
    else:
        lead = sync.parse(KIT / "core" / "agents" / "lead.md")
        vs = sync.render_vscode(*lead)
        if "'agent'" not in vs or "agents: ['*']" not in vs:
            errors.append("lead: VS Code output must include the 'agent' tool and agents: ['*']")
        oc = sync.render_opencode(lead[0], lead[1], KIT / "core" / "agents" / "lead.md")
        if "mode: primary" not in oc or "action: subagent" not in oc:
            errors.append("lead: OpenCode output must be mode primary with a subagent rule")

    marker = "Interaction standard (`docs/agents/interaction-standard.md`)"
    for base, _ in scopes:
        for a in sorted((base / "agents").glob("*.md")) if (base / "agents").is_dir() else []:
            if marker not in a.read_text(encoding="utf-8"):
                errors.append(f"{a.relative_to(KIT)}: missing interaction-standard line in Rules")
    for base, _ in scopes:
        for a in sorted((base / "agents").glob("*.md")) if (base / "agents").is_dir() else []:
            if "\n## Access\n" not in a.read_text(encoding="utf-8"):
                errors.append(f"{a.relative_to(KIT)}: missing '## Access' paragraph")
    lead_text = (KIT / "core" / "agents" / "lead.md").read_text(encoding="utf-8")
    for needle in ("by CONTENT", "`Access:` line", "merge order", "mergeStateStatus", ".aiagents/access.md",
                   "AGENT-REPORT tip=", "handover-check.sh", "review bot", "RESUMING", "own worktree",
                   "autonomy-policy.md", "Infrastructure outage", "PENDING", "UNSTABLE",
                   "touched by others", "reserved"):
        if needle not in lead_text:
            errors.append(f"core/agents/lead.md: missing conflict/access rule ({needle})")
    for sk in ONE_QUESTION_SKILLS:
        p = KIT / "core" / "skills" / sk / "SKILL.md"
        if p.exists() and "one question at a time" not in p.read_text(encoding="utf-8").lower():
            errors.append(f"core/skills/{sk}/SKILL.md: must state 'one question at a time'")
    vs_lead = sync.render_vscode(*sync.parse(KIT / "core" / "agents" / "lead.md"))
    if "'vscode/askQuestions'" not in vs_lead:
        errors.append("lead: VS Code tools must include 'vscode/askQuestions'")

    for cmd in sorted((KIT / "core" / "commands").glob("*.md")):
        try:
            outputs = render_command(cmd)
        except ValueError as err:
            errors.append(str(err).replace(str(KIT) + "/", ""))
            continue
        if "$ARGUMENTS" not in outputs["opencode"][1]:
            errors.append(f"{cmd.relative_to(KIT)}: OpenCode output lacks $ARGUMENTS")
    setup = KIT / "core" / "commands" / "setup.md"
    if setup.exists():
        low = setup.read_text(encoding="utf-8").lower()
        for needle in SETUP_NEEDLES:
            if needle not in low:
                errors.append(f"core/commands/setup.md: missing rule text {needle!r}")
    for a in LEAN_AGENTS:
        if not (KIT / "core" / "agents" / f"{a}.md").exists():
            errors.append(f"kitlib.LEAN_AGENTS: no core agent {a!r}")
    for sk in LEAN_SKILLS:
        if not (KIT / "core" / "skills" / sk / "SKILL.md").exists():
            errors.append(f"kitlib.LEAN_SKILLS: no core skill {sk!r}")

    placeholders = set()
    for base, allowed in scopes:
        for p in text_files(base):
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for name in PLACEHOLDER.findall(line):
                    placeholders.add(name)
                    if name not in allowed:
                        errors.append(f"{p.relative_to(KIT)}:{n}: undeclared placeholder {{{{{name}}}}}")

    for name in NEW_PLACEHOLDERS:
        if name not in placeholders:
            errors.append(f"core/placeholders.yaml: {name} declared but not used by any template")
    recipe = (KIT / "core" / "docs-templates" / "autonomy-policy.md.tmpl").read_text(encoding="utf-8")
    recipe_denies = re.findall(r'"action": "shell", "resource": "([^"]+)", "effect": "deny"', recipe)
    if recipe_denies != list(sync.DENY_SHELL):
        errors.append("autonomy-policy.md.tmpl: shell deny rules of the recipe drift from DENY_SHELL in "
                      "core/scripts/sync-agents.py (keep both equal, same order)")
    gate = KIT / "core" / "scripts" / "handover-check.sh"
    if gate.exists():
        for n, line in mutating_lines(gate.read_text(encoding="utf-8")):
            errors.append(f"core/scripts/handover-check.sh:{n}: must stay read-only: {line.strip()}")
    lesson_files = {
        "core/docs-templates/how-to-use-agents.md.tmpl": ("lessons feed the agents", "Lessons learned"),
        "core/docs-templates/AGENTS.md.tmpl": ("Lessons feed the agents", "Lessons learned are written"),
        "core/docs-templates/handover-rules.md.tmpl": ("never a clean review", "never treat a missing", "version number only",
                                                       "update branch", "never guess"),
        "core/agents/developer.md": ("never a clean review", "ALL open PRs", "never edit an applied migration"),
        "core/agents/security-reviewer.md": ("did NOT read or run", "two security reviews"),
    }
    for rel, needles in lesson_files.items():
        low = (KIT / rel).read_text(encoding="utf-8").lower()
        for needle in needles:
            if needle.lower() not in low:
                errors.append(f"{rel}: missing lesson text {needle!r}")
    ci_rules = (("agent-report.yml.tmpl", ("name: agent-report", "AGENT-REPORT tip=", "rerun-on-report",
                                           "permissions: {}", "NOT a required check")),
                ("pinned-actions.yml.tmpl", ("name: pinned-actions", "check-pinned-actions.py")),
                ("ticket-key.yml.tmpl", ("placeholder-key", "[1-9][0-9]*")))
    for fname, needles in ci_rules:
        p = KIT / "core" / "ci-templates" / fname
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        for needle in needles:
            if needle not in text:
                errors.append(f"core/ci-templates/{fname}: missing {needle!r}")
        if "actions/checkout" in text and "persist-credentials: false" not in text:
            errors.append(f"core/ci-templates/{fname}: checkout must not persist credentials")
    pin = load_module("check_pinned", KIT / "core" / "scripts" / "check-pinned-actions.py")
    for wf in sorted((KIT / "core").rglob("*.yml*")) + sorted((KIT / ".github").rglob("*.yml")):
        for n, ref in pin.check_text(wf.read_text(encoding="utf-8")):
            errors.append(f"{wf.relative_to(KIT)}:{n}: action not pinned to a commit SHA: {ref}")

    res = subprocess.run([sys.executable, str(KIT / "scripts" / "build-prompts.py"), "--check"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        errors.append("VS Code prompts out of date: run python3 scripts/build-prompts.py\n" + res.stderr.strip())

    errors += [f"attribution: {e}" for e in check_attribution(KIT)]

    forbidden = scan_forbidden(KIT)
    errors += [f"forbidden: {h}" for h in forbidden]

    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    print(f"checked {skills} skills, {agents} agents, {len(placeholders)} placeholders in use, "
          f"forbidden-string hits: {len(forbidden)}")
    if errors:
        print(f"FAILED: {len(errors)} problem(s)", file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
