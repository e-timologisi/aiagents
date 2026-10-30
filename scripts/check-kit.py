#!/usr/bin/env python3
"""Validate the aiagents kit.

Usage: python3 scripts/check-kit.py

Checks:
  - every skill directory has SKILL.md with frontmatter name == directory and a description
  - every agent source parses with core/scripts/sync-agents.py rules
  - every {{PLACEHOLDER}} is declared in its scope (core/placeholders.yaml + type.yaml or pack.yaml)
  - type.yaml / pack.yaml names match their directory; repo types have the required files
  - VS Code prompt files are in sync with prompts/*.md
  - no forbidden strings: built-in generic patterns (12-digit AWS account ids, ARNs, IPv4 addresses,
    GitHub tokens, Google OAuth secrets, private keys, password literals) plus optional local regexes
    from the untracked `.kit-forbidden.txt` (one per line; put your own domains/org names there)
"""
import importlib.util
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kitlib import KIT, PLACEHOLDER, declared, frontmatter, parse_yaml, scan_forbidden  # noqa: E402

REQUIRED_FILES = [
    "core/agents/lead.md", "core/agents/explorer.md", "core/docs-templates/interaction-standard.md.tmpl", "HOWTO.md", "prompts/00-start-here.md",
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
TYPE_FILES = ("type.yaml", "AGENTS.md.tmpl", "CONTRIBUTING.md.tmpl", "README.md.tmpl")


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_agents", KIT / "core" / "scripts" / "sync-agents.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
                sync.parse(a)
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
    for sk in ONE_QUESTION_SKILLS:
        p = KIT / "core" / "skills" / sk / "SKILL.md"
        if p.exists() and "one question at a time" not in p.read_text(encoding="utf-8").lower():
            errors.append(f"core/skills/{sk}/SKILL.md: must state 'one question at a time'")
    vs_lead = sync.render_vscode(*sync.parse(KIT / "core" / "agents" / "lead.md"))
    if "'vscode/askQuestions'" not in vs_lead:
        errors.append("lead: VS Code tools must include 'vscode/askQuestions'")

    placeholders = set()
    for base, allowed in scopes:
        for p in text_files(base):
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for name in PLACEHOLDER.findall(line):
                    placeholders.add(name)
                    if name not in allowed:
                        errors.append(f"{p.relative_to(KIT)}:{n}: undeclared placeholder {{{{{name}}}}}")

    res = subprocess.run([sys.executable, str(KIT / "scripts" / "build-prompts.py"), "--check"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        errors.append("VS Code prompts out of date: run python3 scripts/build-prompts.py\n" + res.stderr.strip())

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
