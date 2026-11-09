"""Stack profiles (stacks/<id>/stack.yaml), added next to repo-types (standard library only).

Nothing here changes kitlib.py or the repo-type flow: apply-kit.py calls these helpers only when
--stack, --list-stacks or --stack-info is used, or when a chosen pack ships commands.
"""
import hashlib
import json
import pathlib
import re

from kitlib import KIT, declared, frontmatter, render_command

STACKS = KIT / "stacks"
CATEGORIES = ("web", "api", "mobile", "desktop", "data", "docs")
OS_KEYS = ("windows", "macos", "linux")
OS_VALUES = ("yes", "no", "untested")
STATUSES = ("stable", "beta")
OWN_TEMPLATES = ("AGENTS.md.tmpl", "CONTRIBUTING.md.tmpl", "README.md.tmpl")
KV = re.compile(r"^[A-Za-z0-9_-]+:(\s|$)")


# --- tiny YAML subset: nested maps, block lists of maps, flow [a, b] and {k: v} ---------------

def _split_flow(text):
    parts, cur, quote = [], "", None
    for ch in text:
        if quote:
            quote = None if ch == quote else quote
            cur += ch
        elif ch in "\"'":
            quote, cur = ch, cur + ch
        elif ch == ",":
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts]


def _scalar(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [_scalar(p) for p in _split_flow(value[1:-1])]
    if value.startswith("{") and value.endswith("}"):
        out = {}
        for p in _split_flow(value[1:-1]):
            k, _, v = p.partition(":")
            out[k.strip()] = _scalar(v)
        return out
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return {"true": True, "false": False}.get(value, value)


def _strip_comment(raw):
    quote = None
    for i, ch in enumerate(raw):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or raw[i - 1].isspace()):
            return raw[:i].rstrip()
    return raw.rstrip()


def parse_stack_yaml(text, name="stack.yaml"):
    items = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if line.strip():
            items.append([len(line) - len(line.lstrip()), line.strip(), n])

    def block(i, indent):
        return listing(i, indent) if items[i][1].startswith("- ") else mapping(i, indent)

    def listing(i, indent):
        out = []
        while i < len(items) and items[i][0] == indent and items[i][1].startswith("- "):
            rest = items[i][1][2:].strip()
            if KV.match(rest):
                items[i] = [indent + 2, rest, items[i][2]]
                value, i = mapping(i, indent + 2)
                out.append(value)
            else:
                out.append(_scalar(rest))
                i += 1
        return out, i

    def mapping(i, indent):
        out = {}
        while i < len(items) and items[i][0] == indent and not items[i][1].startswith("- "):
            key, sep, val = items[i][1].partition(":")
            if not sep:
                raise ValueError(f"{name}:{items[i][2]}: expected `key: value`")
            key, val, i = key.strip(), val.strip(), i + 1
            if val:
                out[key] = _scalar(val)
            elif i < len(items) and items[i][0] > indent:
                out[key], i = block(i, items[i][0])
            else:
                out[key] = None
        if i < len(items) and items[i][0] > indent:
            raise ValueError(f"{name}:{items[i][2]}: unexpected indentation")
        return out, i

    if not items:
        return {}
    data, end = mapping(0, items[0][0])
    if end != len(items):
        raise ValueError(f"{name}:{items[end][2]}: unexpected content")
    return data


# --- stack catalogue ------------------------------------------------------------------------

def stack_ids():
    if not STACKS.is_dir():
        return []
    return sorted(p.name for p in STACKS.iterdir() if (p / "stack.yaml").exists())


def load_stack(stack_id):
    path = STACKS / stack_id / "stack.yaml"
    if not path.is_file():
        raise ValueError(f"unknown stack {stack_id!r} (known: {', '.join(stack_ids()) or 'none'})")
    return parse_stack_yaml(path.read_text(encoding="utf-8"), f"stacks/{stack_id}/stack.yaml")


def stack_base(spec, stack_id):
    """(type name, directory with templates/agents/skills, apply-time spec or None for an alias)."""
    alias = spec.get("repo_type")
    if alias:
        return alias, KIT / "repo-types" / alias, None
    own = {"name": stack_id, "docs_hub": "true" if spec.get("category") == "docs" else "false",
           "defaults": {k: str(v) for k, v in (spec.get("defaults") or {}).items()}}
    return stack_id, STACKS / stack_id, own


def describe(stack_id, spec, os_name=None):
    tools = spec.get("toolchain") or []
    if os_name:
        tools = [{**t, "install": (t.get("install") or {}).get(os_name)} for t in tools]
    return {"id": stack_id, "status": spec.get("status", "stable"), "title": spec.get("title"),
            "plain": spec.get("plain"), "category": spec.get("category"), "needs_mac": spec.get("needs_mac"),
            "os_support": spec.get("os_support"), "toolchain": tools,
            "accounts_needed": spec.get("accounts_needed") or [], "run_cmd": spec.get("run_cmd"),
            "risks": spec.get("risks") or [], "repo_type": spec.get("repo_type")}


def validate_stack(stack_id, packs):
    """Schema errors for stacks/<id>/stack.yaml (see stacks/README.md)."""
    where = f"stacks/{stack_id}/stack.yaml"
    try:
        spec = load_stack(stack_id)
    except ValueError as err:
        return [str(err)]
    errors = []

    def need(key, kind):
        if not isinstance(spec.get(key), kind) or not spec.get(key):
            errors.append(f"{where}: {key} must be a non-empty {kind.__name__}")

    if spec.get("id") != stack_id:
        errors.append(f"{where}: id must be {stack_id!r}")
    if spec.get("category") not in CATEGORIES:
        errors.append(f"{where}: category must be one of {CATEGORIES}")
    if spec.get("status", "stable") not in STATUSES:
        errors.append(f"{where}: status must be one of {STATUSES}")
    for key in ("title", "plain", "run_cmd"):
        need(key, str)
    for key in ("fits", "not_for", "risks"):
        need(key, list)
    if not isinstance(spec.get("needs_mac"), bool):
        errors.append(f"{where}: needs_mac must be true or false")
    support = spec.get("os_support") if isinstance(spec.get("os_support"), dict) else {}
    if set(support) != set(OS_KEYS) or any(v not in OS_VALUES for v in support.values()):
        errors.append(f"{where}: os_support needs {OS_KEYS} each one of {OS_VALUES}")
    tools = spec.get("toolchain")
    if not isinstance(tools, list) or not tools:
        errors.append(f"{where}: toolchain must list at least one tool")
        tools = []
    for t in tools:
        tid = t.get("id", "?") if isinstance(t, dict) else "?"
        if not isinstance(t, dict) or not all(t.get(k) for k in ("id", "check", "why")):
            errors.append(f"{where}: toolchain item {tid}: id, check and why are required")
            continue
        if not isinstance(t.get("admin"), bool):
            errors.append(f"{where}: toolchain {tid}: admin must be true or false")
        install = t.get("install") if isinstance(t.get("install"), dict) else {}
        for os_name in ("windows", "macos"):
            if support.get(os_name) == "yes" and not install.get(os_name):
                errors.append(f"{where}: toolchain {tid}: no install command for {os_name} (claimed yes)")
    if not isinstance(spec.get("accounts_needed"), list):
        errors.append(f"{where}: accounts_needed must be a list (may be empty: [])")
    for p in spec.get("recommended_packs") or []:
        if p not in packs:
            errors.append(f"{where}: recommended pack {p!r} does not exist")
    alias = spec.get("repo_type")
    if alias:
        if not (KIT / "repo-types" / alias / "type.yaml").is_file():
            errors.append(f"{where}: repo_type {alias!r} does not exist")
    else:
        for f in OWN_TEMPLATES:
            if not (STACKS / stack_id / f).is_file():
                errors.append(f"stacks/{stack_id}: missing {f} (stacks without repo_type carry their own templates)")
        if not isinstance(spec.get("defaults"), dict) or not spec["defaults"].get("STACK"):
            errors.append(f"{where}: defaults with STACK is required when there is no repo_type")
    return errors


def stack_declared(stack_id):
    return declared({"defaults": load_stack(stack_id).get("defaults") or {}})


# --- commands: one source, optional `agent` ---------------------------------------------------

def render_command_with_agent(path, scope="project"):
    """kitlib.render_command plus an `agent:` key. Project scope uses the source key `agent` for both
    tools; global scope uses `global_agent` for OpenCode only (VS Code has no global custom agent here)."""
    outputs = render_command(path)
    meta = frontmatter(path) or {}
    result = {}
    for tool, (dest, text) in outputs.items():
        agent = meta.get("agent") if scope == "project" else (meta.get("global_agent") if tool == "opencode" else None)
        if agent:
            head, sep, rest = text.partition("\n---\n")
            if tool == "vscode":  # the VS Code output already carries `agent: agent`
                head = head.replace("agent: agent", f"agent: {agent}")
            else:
                head = head + f"\nagent: {agent}"
            text = head + sep + rest
        text = text.replace(f"core/commands/{pathlib.Path(path).name}",
                            pathlib.Path(path).resolve().relative_to(KIT).as_posix())
        result[tool] = (dest, text)
    return result


def pack_commands(pack_names):
    """{dest: (text, origin)} of project-level commands shipped by packs (packs/<p>/commands/*.md);
    commands marked `scope: global` are installed on the machine by bootstrap/, not into projects."""
    out = {}
    for p in pack_names:
        for src in sorted((KIT / "packs" / p / "commands").glob("*.md")):
            if (frontmatter(src) or {}).get("scope") == "global":
                continue
            for dest, text in render_command_with_agent(src).values():
                out[dest] = (text, f"pack:{p}")
    return out


def global_setup_agent():
    """OpenCode global copy of the setup agent: no model (the session model is used), generic names."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_agents", KIT / "core" / "scripts" / "sync-agents.py")
    sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync)
    src = KIT / "packs" / "conversational-start" / "agents" / "setup.md"
    meta, body = sync.parse(src)
    meta.pop("model", None)
    values = {"PROJECT_NAME": "your project", "SETUP_LOG": "docs/setup-log.md", "MODEL_REVIEWER": "the session model",
              "MODEL_PREMIUM": "a larger model"}
    from kitlib import PLACEHOLDER
    render = lambda s: PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), s)
    meta = {k: render(v) for k, v in meta.items()}
    text = sync.render_opencode(meta, render(body), src)
    return text.replace(f"GENERATED from agents/{meta['name']}.md", "GENERATED from packs/conversational-start/agents/setup.md of the aiagents kit", 1).replace(
        "edit the source, then run python3 scripts/sync-agents.py", "edit the source, then run python3 scripts/build-bootstrap.py", 1)


def bootstrap_outputs():
    """{path relative to bootstrap/: text}: the global commands (and the OpenCode setup agent) that
    `bootstrap/install-commands.py` copies to the machine. Generated; check-kit verifies they are current."""
    out = {}
    for src in sorted((KIT / "packs" / "conversational-start" / "commands").glob("*.md")):
        for tool, (dest, text) in render_command_with_agent(src, scope="global").items():
            out[f"commands/{tool}/{pathlib.Path(dest).name}"] = text
    out["commands/opencode-agents/setup.md"] = global_setup_agent()
    return out


# --- additive-only baseline -----------------------------------------------------------------

BASELINE = KIT / "scripts" / "baseline-0.6.4.json"


def baseline_problems():
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    problems = []
    for rel, want in sorted(data["files"].items()):
        p = KIT / rel
        if not p.is_file():
            problems.append(f"{rel}: removed (must stay unchanged since {data['baseline']})")
        elif hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != want:
            problems.append(f"{rel}: changed (must stay byte-identical to {data['baseline']})")
    return problems
