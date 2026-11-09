#!/usr/bin/env python3
"""Apply the aiagents kit to a target repository.

Usage:
  python3 scripts/apply-kit.py --type backend-go|frontend-nextjs|serverless-sam|docs-hub \
      --target <repo dir> --set PROJECT_NAME=Acme --set ORG=acme --set DOCS_REPO=acme-docs \
      [--pack multi-tenant-saas --pack ...] [--standalone] [--profile lean|full] [--agent NAME ...] [--dry-run]
  python3 scripts/apply-kit.py --target <repo dir> --update [--set KEY=VALUE ...] [--pack P] [--agent A] [--dry-run]
  python3 scripts/apply-kit.py --target <repo dir> --bootstrap [--dry-run]   # only the /setup command
  python3 scripts/apply-kit.py --target <repo dir> --detect                 # read-only guesses (JSON)
  python3 scripts/apply-kit.py --stack <id> --target <repo dir> --set ... [--pack conversational-start ...]
  python3 scripts/apply-kit.py --list-stacks | --stack-info <id> [--os windows|macos]   # read-only (stacks/README.md)

Copies core + repo type + packs into the target (agents/, .agents/skills/, .github/,
docs/agents/, AGENTS.md, CONTRIBUTING.md, README.md ...), substitutes {{PLACEHOLDERS}} and
never overwrites existing files. Writes .aiagents-manifest.json (kit version, choices,
values, file hashes) and runs scripts/sync-agents.py in the target.

--update refreshes kit-managed files whose content still matches the manifest hash;
files the user modified are reported as conflicts and left untouched.
Never pass secrets with --set: values are stored in the manifest.

--profile full (default, unchanged behaviour) installs everything. --profile lean (what /setup uses)
installs lead, explorer, a small core skill set, AGENTS.md, interaction standard, access-and-conflicts,
work-log template, handover rules + handover-check.sh, autonomy policy, decision-log and retro
templates, opt-in CI templates under docs/ci-templates/ (never auto-enabled), the /setup command and the chosen packs; --agent adds further agents.
--update keeps the stored profile, packs and agents and adds new --pack/--agent choices.
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from stacks import (describe, load_stack, pack_commands, stack_base, stack_ids)  # noqa: E402
from kitlib import (KIT, LEAN_AGENTS, PLACEHOLDER, PROFILES, detect, lean_keep,  # noqa: E402
                    parse_yaml, render_command, sha256)

MANIFEST = ".aiagents-manifest.json"
REPO_MARK = "<!-- aiagents:repo-section -->"
PACK_MARK = "<!-- aiagents:pack-sections -->"
PR_MARK = "<!-- aiagents:pr-additions -->"
RAW_SUFFIXES = {".py", ".sh"}  # copied verbatim, never rendered


def kit_version():
    return (KIT / "VERSION").read_text(encoding="utf-8").strip()


def types():
    return sorted(p.name for p in (KIT / "repo-types").iterdir() if (p / "type.yaml").exists())


def packs():
    return sorted(p.name for p in (KIT / "packs").iterdir() if (p / "pack.yaml").exists())


def read(path):
    return path.read_text(encoding="utf-8")


def add_tree(plan, src_dir, dest_prefix, origin):
    if not src_dir.is_dir():
        return
    for p in sorted(src_dir.rglob("*")):
        if p.is_file():
            plan_put(plan, f"{dest_prefix}/{p.relative_to(src_dir).as_posix()}", p, origin)


def plan_put(plan, dest, src, origin, text=None):
    prev = plan.get(dest)
    plan[dest] = {"src": src, "text": text, "origin": origin,
                  "overrides": (prev["origin"] if prev else None)}


def agent_names(type_name, pack_names, type_dir=None):
    dirs = [KIT / "core" / "agents", (type_dir or KIT / "repo-types" / type_name) / "agents"]
    dirs += [KIT / "packs" / p / "agents" for p in pack_names]
    return sorted({a.stem for d in dirs if d.is_dir() for a in d.glob("*.md")})


def add_commands(plan):
    for src in sorted((KIT / "core" / "commands").glob("*.md")):
        for dest, text in render_command(src).values():
            plan_put(plan, dest, None, "core", text)


def bootstrap_plan():
    plan = {}
    add_commands(plan)
    return plan


def build_plan(type_name, pack_names, standalone, type_spec, profile="full", agents=(), type_dir=None):
    plan = {}
    core, tdir = KIT / "core", type_dir or KIT / "repo-types" / type_name
    pdirs = [KIT / "packs" / p for p in pack_names]

    add_tree(plan, core / "agents", "agents", "core")
    add_tree(plan, tdir / "agents", "agents", f"type:{type_name}")
    for pd in pdirs:
        add_tree(plan, pd / "agents", "agents", f"pack:{pd.name}")

    for base, origin in [(core, "core"), (tdir, f"type:{type_name}")] + [(pd, f"pack:{pd.name}") for pd in pdirs]:
        add_tree(plan, base / "skills", ".agents/skills", origin)
    for pd in pdirs:
        add_tree(plan, pd / "rules", "docs/rules", f"pack:{pd.name}")

    plan_put(plan, "scripts/sync-agents.py", core / "scripts" / "sync-agents.py", "core")
    gh = core / "github"
    add_tree(plan, gh / "ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE", "core")
    plan_put(plan, ".github/CODEOWNERS", gh / "CODEOWNERS", "core")
    plan_put(plan, ".github/workflows/agents-sync.yml", gh / "workflows" / "agents-sync.yml", "core")
    plan_put(plan, "docs/agents/ci-skeleton.yml", gh / "workflows" / "ci-skeleton.yml", "core")

    pr = read(gh / "pull_request_template.md")
    add = tdir / "pull_request_template.additions.md"
    pr = pr.replace(PR_MARK, read(add).rstrip("\n") if add.exists() else "").rstrip("\n") + "\n"
    plan_put(plan, ".github/pull_request_template.md", None, "core+type", pr)

    dt = core / "docs-templates"
    agents_md = read(dt / "AGENTS.md.tmpl")
    agents_md = agents_md.replace(REPO_MARK, read(tdir / "AGENTS.md.tmpl").rstrip("\n"))
    sections = [read(pd / "AGENTS.section.md").rstrip("\n") for pd in pdirs if (pd / "AGENTS.section.md").exists()]
    agents_md = agents_md.replace(PACK_MARK + "\n\n", ("\n\n".join(sections) + "\n\n") if sections else "")
    plan_put(plan, "AGENTS.md", None, "core+type+packs", agents_md)

    for name in ("ticket-standard.md", "release-checklist.md", "security-review-checklist.md",
                 "domain.md", "issue-tracker.md", "triage-labels.md"):
        plan_put(plan, f"docs/agents/{name}", dt / name, "core")
    plan_put(plan, "docs/agents/how-to-use-agents.md", dt / "how-to-use-agents.md.tmpl", "core")
    plan_put(plan, "docs/agents/interaction-standard.md", dt / "interaction-standard.md.tmpl", "core")
    plan_put(plan, "docs/agents/access-and-conflicts.md", dt / "access-and-conflicts.md.tmpl", "core")
    plan_put(plan, "docs/agents/templates/work-log.md", dt / "work-log.md", "core")
    plan_put(plan, "docs/agents/handover-rules.md", dt / "handover-rules.md.tmpl", "core")
    plan_put(plan, "docs/agents/autonomy-policy.md", dt / "autonomy-policy.md.tmpl", "core")
    plan_put(plan, "docs/agents/templates/decision-log.md", dt / "decision-log.md.tmpl", "core")
    plan_put(plan, "docs/agents/templates/retro-template.md", dt / "retro-template.md", "core")
    for script in ("handover-check.sh", "check-pinned-actions.py"):
        plan_put(plan, f"scripts/{script}", core / "scripts" / script, "core")
    # Opt-in copies only: the project owner reads them and copies them into .github/workflows/.
    for tmpl in sorted((core / "ci-templates").glob("*.yml.tmpl")):
        plan_put(plan, f"docs/ci-templates/{tmpl.name[:-len('.tmpl')]}", tmpl, "core")
    add_tree(plan, dt / "project", "docs/agents/templates", "core")
    if type_spec.get("docs_hub") == "true" or standalone:
        plan_put(plan, "docs/architecture/service-map.md", dt / "service-map.md.tmpl", "core")
        plan_put(plan, "docs/onboarding.md", dt / "onboarding.md.tmpl", "core")
        plan_put(plan, "docs/adr/template.md", dt / "adr-template.md", "core")
        plan_put(plan, "GLOSSARY.md", dt / "GLOSSARY.md.tmpl", "core")

    plan_put(plan, "CONTRIBUTING.md", tdir / "CONTRIBUTING.md.tmpl", f"type:{type_name}")
    plan_put(plan, "README.md", tdir / "README.md.tmpl", f"type:{type_name}")

    if profile == "lean":
        keep = set(LEAN_AGENTS) | set(agents)
        plan = {d: e for d, e in plan.items() if lean_keep(d, e["origin"], keep)}
    add_commands(plan)
    if any(d.endswith("/LICENSE.upstream") for d in plan):
        plan_put(plan, "docs/agents/THIRD-PARTY-NOTICES.md", KIT / "THIRD-PARTY-NOTICES.md", "kit")
    if profile == "lean":
        return plan
    add_tree(plan, KIT / "prompts", "docs/agents/prompts", "prompts")
    for dest in [d for d in plan if d.startswith("docs/agents/prompts/vscode/")]:
        entry = plan.pop(dest)
        plan[".github/prompts/" + dest.rsplit("/", 1)[1]] = entry
    return plan


def resolve_values(specs, manifest_values, cli_values, target):
    values, required = {"TARGET_DIR_NAME": target.name}, set()
    for spec in specs:
        values.update(spec.get("defaults") or {})
        required |= set(spec.get("required") or [])
    values.update(manifest_values)
    values.update(cli_values)
    for _ in range(10):
        changed = False
        for k, v in values.items():
            nv = PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), v)
            if nv != v:
                values[k], changed = nv, True
        if not changed:
            break
    missing = sorted(k for k in required if not values.get(k))
    return values, missing


def render(text, values):
    return PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), text)


def write_bootstrap(target, dry_run):
    """Install only the /setup command files; never touches existing files or the manifest."""
    prefix = "[dry-run] " if dry_run else ""
    print(f"{prefix}aiagents {kit_version()} → {target} (bootstrap: /setup command only)")
    for dest, e in sorted(bootstrap_plan().items()):
        path = target / dest
        if path.exists():
            print(f"  skipped (exists): {dest}")
            continue
        print(f"  created: {dest}")
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(e["text"], encoding="utf-8")
    local = target / ".aiagents" / "kit.local"
    print(f"  kit path for /setup: {local.relative_to(target)} (git-ignored via .aiagents/.gitignore)")
    if not dry_run:
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(str(KIT) + "\n", encoding="utf-8")
        ignore = local.parent / ".gitignore"
        if not ignore.exists():
            ignore.write_text("kit.local\n", encoding="utf-8")
    print("  next: open this repo in OpenCode or VS Code (Copilot agent mode) and run /setup")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Apply the aiagents kit to a target repository.")
    ap.add_argument("--type", choices=types())
    ap.add_argument("--target")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--pack", action="append", default=[], choices=packs())
    ap.add_argument("--standalone", action="store_true",
                    help="single-repo project: also install service map, ADR template, glossary, onboarding")
    ap.add_argument("--update", action="store_true", help="refresh unmodified kit-managed files")
    ap.add_argument("--profile", choices=PROFILES,
                    help="full (default for new installs) or lean (core minimum + chosen packs/agents)")
    ap.add_argument("--agent", action="append", default=[], metavar="NAME",
                    help="extra agent for the lean profile (repeatable)")
    ap.add_argument("--stack", metavar="ID", help="stack profile from stacks/ (alternative to --type)")
    ap.add_argument("--list-stacks", action="store_true", help="print the stack catalogue and exit")
    ap.add_argument("--stack-info", metavar="ID", help="print one stack (toolchain, limits) as JSON and exit")
    ap.add_argument("--os", choices=("windows", "macos"), help="with --stack-info: only this OS's install commands")
    ap.add_argument("--bootstrap", action="store_true", help="install only the /setup command files")
    ap.add_argument("--detect", action="store_true", help="print read-only guesses for /setup as JSON")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.list_stacks or args.stack_info:
        try:
            if args.list_stacks:
                for sid in stack_ids():
                    s = load_stack(sid)
                    print(f"{sid}\t{s.get('status', 'stable')}\t{s.get('title')}")
            else:
                print(json.dumps(describe(args.stack_info, load_stack(args.stack_info), args.os), indent=2))
        except ValueError as err:
            print(f"error: {err}", file=sys.stderr)
            return 2
        return 0
    if not args.target:
        ap.error("--target is required")
    if args.stack and args.type:
        print("error: use either --type or --stack, not both", file=sys.stderr)
        return 2
    target = pathlib.Path(args.target).resolve()
    if not target.is_dir():
        print(f"error: target {target} is not a directory", file=sys.stderr)
        return 2
    if args.detect:
        print(json.dumps(detect(target), indent=2))
        return 0
    if args.bootstrap:
        return write_bootstrap(target, args.dry_run)
    mpath = target / MANIFEST
    manifest = json.loads(read(mpath)) if mpath.exists() else {}
    if args.update and not manifest:
        print(f"error: --update needs {MANIFEST} in the target (apply the kit first)", file=sys.stderr)
        return 2

    stack_id = args.stack or manifest.get("stack")
    type_dir = own_spec = None
    if stack_id:
        try:
            type_name, type_dir, own_spec = stack_base(load_stack(stack_id), stack_id)
        except ValueError as err:
            print(f"error: {err}", file=sys.stderr)
            return 2
    else:
        type_name = args.type or manifest.get("type")
    if not type_name:
        print("error: --type or --stack is required", file=sys.stderr)
        return 2
    pack_names = list(dict.fromkeys((manifest.get("packs") or []) + args.pack)) if args.update else args.pack
    standalone = args.standalone or bool(manifest.get("standalone"))
    profile = args.profile or manifest.get("profile") or "full"
    extra_agents = list(dict.fromkeys((manifest.get("agents") or []) + args.agent))
    unknown = sorted(set(extra_agents) - set(agent_names(type_name, pack_names, type_dir)))
    if unknown:
        print("error: unknown --agent: " + ", ".join(unknown), file=sys.stderr)
        return 2

    cli = {}
    for item in args.set:
        if "=" not in item:
            print(f"error: --set {item!r} must be KEY=VALUE", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        cli[k.strip()] = v

    type_spec = own_spec or parse_yaml((type_dir or KIT / "repo-types" / type_name) / "type.yaml")
    specs = [parse_yaml(KIT / "core" / "placeholders.yaml"), type_spec]
    specs += [parse_yaml(KIT / "packs" / p / "pack.yaml") for p in pack_names]
    if type_spec.get("docs_hub") == "true" or standalone:
        specs.append({"defaults": {"DOCS_REPO": "{{REPO_NAME}}"}})
    values, missing = resolve_values(specs, manifest.get("values", {}), cli, target)
    if missing:
        print("error: missing required placeholders (use --set KEY=VALUE): " + ", ".join(missing), file=sys.stderr)
        return 1

    plan = build_plan(type_name, pack_names, standalone, type_spec, profile, extra_agents, type_dir)
    for dest, (text, origin) in pack_commands(pack_names).items():
        plan_put(plan, dest, None, origin, text)
    rendered, unresolved = {}, []
    for dest, e in sorted(plan.items()):
        src = e["src"]
        if e["text"] is None and src.suffix in RAW_SUFFIXES:
            rendered[dest] = read(src)
            continue
        text = render(e["text"] if e["text"] is not None else read(src), values)
        rendered[dest] = text
        unresolved += [f"{dest}: {{{{{m}}}}}" for m in sorted(set(PLACEHOLDER.findall(text)))]
    if unresolved:
        print("error: unresolved placeholders:\n  " + "\n  ".join(unresolved), file=sys.stderr)
        return 1

    files = dict(manifest.get("files", {}))
    report = {k: [] for k in ("created", "updated", "unchanged", "skipped", "conflict")}
    for dest, text in rendered.items():
        path, new_hash = target / dest, sha256(text)
        if not path.exists():
            action = "created"
        elif sha256(read(path)) == new_hash:
            action = "unchanged"  # identical content (e.g. from --bootstrap) is adopted
        elif not args.update or dest not in files:
            action = "skipped"
        elif sha256(read(path)) == files[dest]:
            action = "updated"
        else:
            action = "conflict"
        note = f" (overrides {plan[dest]['overrides']})" if plan[dest]["overrides"] else ""
        report[action].append(dest + note)
        if action in ("created", "updated"):
            files[dest] = new_hash
            if not args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                if path.suffix in RAW_SUFFIXES:
                    path.chmod(0o755)
        elif action == "unchanged":
            files[dest] = new_hash
    obsolete = sorted(set(files) - set(rendered))

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"{prefix}aiagents {kit_version()} → {target} (type {type_name}; profile {profile}; "
          f"packs: {', '.join(pack_names) or 'none'}; extra agents: {', '.join(extra_agents) or 'none'})")
    for action, label in (("created", "created"), ("updated", "updated"), ("unchanged", "unchanged"),
                          ("skipped", "skipped (exists, not overwritten)"), ("conflict", "conflict (modified locally, not updated)")):
        print(f"  {label}: {len(report[action])}")
        if action != "unchanged":
            for d in report[action]:
                print(f"    {d}")
    if obsolete:
        print("  obsolete (no longer in kit, kept): " + ", ".join(obsolete))
    if args.dry_run:
        return 0

    stored = {k: v for k, v in {**manifest.get("values", {}), **cli}.items()}
    new_manifest = {
        "kit": "aiagents", "version": kit_version(), "type": type_name, "packs": pack_names,
        "standalone": standalone, "profile": profile, "agents": extra_agents, "values": stored, "files": dict(sorted(files.items())),
    }
    if stack_id:  # written only with --stack; manifests made with --type stay as before
        new_manifest["stack"] = stack_id
    mpath.write_text(json.dumps(new_manifest, indent=2) + "\n", encoding="utf-8")
    sync = target / "scripts" / "sync-agents.py"
    for extra in ([], ["--check"]):
        res = subprocess.run([sys.executable, str(sync), "--root", str(target)] + extra,
                             capture_output=True, text=True)
        out = (res.stdout + res.stderr).strip()
        print(f"  sync-agents {' '.join(extra) or '(generate)'}: {'ok' if res.returncode == 0 else 'FAILED'}"
              + (f" — {out.splitlines()[-1]}" if out else ""))
        if res.returncode != 0:
            print(out, file=sys.stderr)
            return 1
    return 1 if report["conflict"] else 0


if __name__ == "__main__":
    sys.exit(main())
