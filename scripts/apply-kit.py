#!/usr/bin/env python3
"""Apply the aiagents kit to a target repository.

Usage:
  python3 scripts/apply-kit.py --type backend-go|frontend-nextjs|serverless-sam|docs-hub \
      --target <repo dir> --set PROJECT_NAME=Acme --set ORG=acme --set DOCS_REPO=acme-docs \
      [--pack multi-tenant-saas --pack ...] [--standalone] [--dry-run]
  python3 scripts/apply-kit.py --target <repo dir> --update [--set KEY=VALUE ...] [--dry-run]

Copies core + repo type + packs into the target (agents/, .agents/skills/, .github/,
docs/agents/, AGENTS.md, CONTRIBUTING.md, README.md ...), substitutes {{PLACEHOLDERS}} and
never overwrites existing files. Writes .aiagents-manifest.json (kit version, choices,
values, file hashes) and runs scripts/sync-agents.py in the target.

--update refreshes kit-managed files whose content still matches the manifest hash;
files the user modified are reported as conflicts and left untouched.
Never pass secrets with --set: values are stored in the manifest.
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kitlib import KIT, PLACEHOLDER, parse_yaml, sha256  # noqa: E402

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


def build_plan(type_name, pack_names, standalone, type_spec):
    plan = {}
    core, tdir = KIT / "core", KIT / "repo-types" / type_name
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
    add_tree(plan, dt / "project", "docs/agents/templates", "core")
    if type_spec.get("docs_hub") == "true" or standalone:
        plan_put(plan, "docs/architecture/service-map.md", dt / "service-map.md.tmpl", "core")
        plan_put(plan, "docs/onboarding.md", dt / "onboarding.md.tmpl", "core")
        plan_put(plan, "docs/adr/template.md", dt / "adr-template.md", "core")
        plan_put(plan, "GLOSSARY.md", dt / "GLOSSARY.md.tmpl", "core")

    plan_put(plan, "CONTRIBUTING.md", tdir / "CONTRIBUTING.md.tmpl", f"type:{type_name}")
    plan_put(plan, "README.md", tdir / "README.md.tmpl", f"type:{type_name}")

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


def main():
    ap = argparse.ArgumentParser(description="Apply the aiagents kit to a target repository.")
    ap.add_argument("--type", choices=types())
    ap.add_argument("--target", required=True)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--pack", action="append", default=[], choices=packs())
    ap.add_argument("--standalone", action="store_true",
                    help="single-repo project: also install service map, ADR template, glossary, onboarding")
    ap.add_argument("--update", action="store_true", help="refresh unmodified kit-managed files")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    target = pathlib.Path(args.target).resolve()
    if not target.is_dir():
        print(f"error: target {target} is not a directory", file=sys.stderr)
        return 2
    mpath = target / MANIFEST
    manifest = json.loads(read(mpath)) if mpath.exists() else {}
    if args.update and not manifest:
        print(f"error: --update needs {MANIFEST} in the target (apply the kit first)", file=sys.stderr)
        return 2

    type_name = args.type or manifest.get("type")
    if not type_name:
        print("error: --type is required", file=sys.stderr)
        return 2
    pack_names = list(dict.fromkeys((manifest.get("packs") or []) + args.pack)) if args.update else args.pack
    standalone = args.standalone or bool(manifest.get("standalone"))

    cli = {}
    for item in args.set:
        if "=" not in item:
            print(f"error: --set {item!r} must be KEY=VALUE", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        cli[k.strip()] = v

    type_spec = parse_yaml(KIT / "repo-types" / type_name / "type.yaml")
    specs = [parse_yaml(KIT / "core" / "placeholders.yaml"), type_spec]
    specs += [parse_yaml(KIT / "packs" / p / "pack.yaml") for p in pack_names]
    if type_spec.get("docs_hub") == "true" or standalone:
        specs.append({"defaults": {"DOCS_REPO": "{{REPO_NAME}}"}})
    values, missing = resolve_values(specs, manifest.get("values", {}), cli, target)
    if missing:
        print("error: missing required placeholders (use --set KEY=VALUE): " + ", ".join(missing), file=sys.stderr)
        return 1

    plan = build_plan(type_name, pack_names, standalone, type_spec)
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
        elif not args.update:
            action = "unchanged" if dest in files and sha256(read(path)) == new_hash else "skipped"
        elif dest not in files:
            action = "skipped"
        else:
            cur = sha256(read(path))
            if cur == new_hash:
                action = "unchanged"
            elif cur == files[dest]:
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
    print(f"{prefix}aiagents {kit_version()} → {target} (type {type_name}; packs: {', '.join(pack_names) or 'none'})")
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
    mpath.write_text(json.dumps({
        "kit": "aiagents", "version": kit_version(), "type": type_name, "packs": pack_names,
        "standalone": standalone, "values": stored, "files": dict(sorted(files.items())),
    }, indent=2) + "\n", encoding="utf-8")
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
