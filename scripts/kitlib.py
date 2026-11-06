"""Shared helpers for the aiagents kit scripts (standard library only)."""
import hashlib
import pathlib
import re

KIT = pathlib.Path(__file__).resolve().parent.parent
PLACEHOLDER = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".tmpl", ".txt", ".json", ""}

LOCAL_FORBIDDEN_FILE = ".kit-forbidden.txt"

FORBIDDEN = [
    ("aws account id", re.compile(r"(?<![0-9A-Za-z])[0-9]{12}(?![0-9A-Za-z])")),
    ("aws arn", re.compile("arn" + ":aws")),
    ("ip address", re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")),
    ("github token", re.compile("gh" + "o_|gh" + "p_|github" + "_pat_")),
    ("google oauth secret", re.compile("GOC" + "SPX")),
    ("private key", re.compile("PRIVATE" + " KEY")),
    ("password literal", re.compile(r"password\s*[:=]", re.IGNORECASE)),
    ("home directory path", re.compile(r"/Use" r"rs/[A-Za-z]|/home/[a-z][a-z0-9_-]*/")),
    ("hosted tracker site", re.compile(r"[A-Za-z0-9-]+\.atlassian\.net", re.IGNORECASE)),
]

# Mutating commands that must never appear in the read-only handover gate script.
MUTATING = re.compile(
    r"\bgh\s+(?:pr|issue|label|release|repo|run|workflow|secret|variable)\s+"
    r"(?:merge|edit|comment|close|create|delete|review|ready|reopen|rerun|cancel|run|set|lock|transfer)\b"
    r"|\bgh\s+api\b[^\n]*(?:-X\s*|--method[\s=]+)(?:POST|PUT|PATCH|DELETE)"
    r"|\bmutation\b"
    r"|\bgit\s+(?:-C\s+\S+\s+)?(?:push|commit|merge|reset|checkout|switch|rebase|tag|fetch|pull|clean|am|apply|stash|restore|rm|mv|add|branch\s+-[dDmM])\b")


def mutating_lines(text):
    """(line number, line) of non-comment lines that would change a repository or the hosting side."""
    return [(n, line) for n, line in enumerate(text.splitlines(), 1)
            if not line.lstrip().startswith("#") and MUTATING.search(line)]


def local_forbidden(root=KIT):
    """Extra patterns from the untracked `.kit-forbidden.txt` (one regex per line; `#` comments).
    Owners list their own domains, org names and e-mail patterns there; it is never committed."""
    path = pathlib.Path(root) / LOCAL_FORBIDDEN_FILE
    if not path.is_file():
        return []
    patterns = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line and not line.startswith("#"):
            try:
                patterns.append((f"local pattern {LOCAL_FORBIDDEN_FILE}:{n}", re.compile(line)))
            except re.error as err:
                raise ValueError(f"{LOCAL_FORBIDDEN_FILE}:{n}: invalid regex: {err}") from err
    return patterns


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_yaml(path):
    """Parse the kit's tiny YAML subset: top-level `key: scalar`, or a key with an
    indented block of `- item` (list) or `k: v` (mapping). Comments and blanks ignored."""
    data, current = {}, None
    for lineno, raw in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if not line[0].isspace():
            if ":" not in line:
                raise ValueError(f"{path}:{lineno}: expected `key: value`")
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value:
                data[key], current = _scalar(value), None
            else:
                data[key], current = None, key
            continue
        if current is None:
            raise ValueError(f"{path}:{lineno}: unexpected indentation")
        item = line.strip()
        if item.startswith("- "):
            if data[current] is None:
                data[current] = []
            if not isinstance(data[current], list):
                raise ValueError(f"{path}:{lineno}: mixed list/mapping under {current}")
            data[current].append(_scalar(item[2:]))
        else:
            if ":" not in item:
                raise ValueError(f"{path}:{lineno}: expected `k: v` under {current}")
            if data[current] is None:
                data[current] = {}
            if not isinstance(data[current], dict):
                raise ValueError(f"{path}:{lineno}: mixed list/mapping under {current}")
            k, v = item.split(":", 1)
            data[current][k.strip()] = _scalar(v)
    return data


def declared(spec):
    """Placeholder names declared by a placeholders/type/pack yaml."""
    names = set(spec.get("required") or [])
    names |= set((spec.get("defaults") or {}).keys())
    names |= set((spec.get("descriptions") or {}).keys())
    return names


def frontmatter(path):
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return meta
        if ":" in line and not line[:1].isspace():
            k, v = line.split(":", 1)
            meta[k.strip()] = _scalar(v)
    return None


def scan_forbidden(root, skip_dirs=(".git",), extra=None):
    patterns = FORBIDDEN + (local_forbidden(root) if extra is None else list(extra))
    hits = []
    for p in sorted(pathlib.Path(root).rglob("*")):
        if not p.is_file() or any(part in skip_dirs for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if p.name == LOCAL_FORBIDDEN_FILE:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for label, rx in patterns:
                if rx.search(line):
                    hits.append(f"{p.relative_to(root)}:{n}: {label}")
    return hits


NOTICES_FILE = "THIRD-PARTY-NOTICES.md"
UPSTREAM_LICENSE_MARKERS = ("Copyright (c) 2026 Matt Pocock", "Copyright (c) 2026 HumanLayer")
MIT_PERMISSION = "Permission is hereby granted, free of charge"


def check_attribution(root):
    """Every UPSTREAM.md dir needs LICENSE.upstream and a listing in THIRD-PARTY-NOTICES.md."""
    root = pathlib.Path(root)
    errors = []
    notices_path = root / NOTICES_FILE
    notices = notices_path.read_text(encoding="utf-8") if notices_path.exists() else ""
    if not notices:
        errors.append(f"missing {NOTICES_FILE}")
    else:
        for marker in UPSTREAM_LICENSE_MARKERS:
            if marker not in notices:
                errors.append(f"{NOTICES_FILE}: missing license text with {marker!r}")
        if notices.count(MIT_PERMISSION) < len(UPSTREAM_LICENSE_MARKERS):
            errors.append(f"{NOTICES_FILE}: must reproduce every upstream MIT license in full")
    for up in sorted(root.rglob("UPSTREAM.md")):
        if ".git" in up.parts:
            continue
        rel = up.parent.relative_to(root).as_posix()
        lic = up.parent / "LICENSE.upstream"
        if not lic.exists():
            errors.append(f"{rel}: UPSTREAM.md without LICENSE.upstream")
        elif MIT_PERMISSION not in lic.read_text(encoding="utf-8"):
            errors.append(f"{rel}/LICENSE.upstream: missing MIT permission notice")
        if notices and f"`{rel}/`" not in notices:
            errors.append(f"{rel}: not listed in {NOTICES_FILE}")
    return errors


# --- install profiles, /setup command and repo detection -------------------------------------

PROFILES = ("lean", "full")
LEAN_AGENTS = ("lead", "explorer")
LEAN_SKILLS = ("task-intake", "dispatch-tasks", "tdd", "diagnosing-bugs", "code-review", "grilling",
               "domain-modeling", "codebase-design", "pr")
LEAN_FILES = ("AGENTS.md", "scripts/sync-agents.py", "docs/agents/interaction-standard.md",
              "docs/agents/access-and-conflicts.md", "docs/agents/templates/work-log.md",
              "docs/agents/handover-rules.md", "docs/agents/autonomy-policy.md",
              "docs/agents/templates/decision-log.md", "docs/agents/templates/retro-template.md",
              "scripts/handover-check.sh", "scripts/check-pinned-actions.py",
              "docs/ci-templates/agent-report.yml", "docs/ci-templates/pinned-actions.yml",
              "docs/ci-templates/ticket-key.yml")
COMMANDS_DIR = "core/commands"
COMMAND_OUTPUTS = {"opencode": ".opencode/commands/{name}.md", "vscode": ".github/prompts/{name}.prompt.md"}
ARGS_TOKEN = "<ARGUMENTS>"


def lean_keep(dest, origin, agents):
    """True when a planned file belongs to the lean profile (packs always stay complete)."""
    if origin.startswith("pack:") or dest in LEAN_FILES or dest.startswith("docs/rules/"):
        return True
    if dest.startswith("agents/"):
        return dest[len("agents/"):-len(".md")] in agents
    if dest.startswith(".agents/skills/"):
        return dest.split("/")[2] in LEAN_SKILLS
    return False


def parse_command(path):
    """Command source: flat frontmatter (name, description, argument-hint) + Markdown body."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    meta = frontmatter(path)
    if meta is None or not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    for key in ("name", "description", "argument-hint"):
        if not meta.get(key):
            raise ValueError(f"{path}: frontmatter needs {key}")
    if meta["name"] != pathlib.Path(path).stem:
        raise ValueError(f"{path}: name must equal the file name")
    body = text.split("\n---\n", 1)[1].lstrip("\n")
    if ARGS_TOKEN not in body:
        raise ValueError(f"{path}: body must contain {ARGS_TOKEN}")
    return meta, body


def _q(s):
    return "'" + s.replace("'", "''") + "'"


def render_command(path):
    """Return {tool: (relative output path, text)} for OpenCode and VS Code from one source.
    OpenCode: https://opencode.ai/docs/commands/ (`$ARGUMENTS`); VS Code prompt files:
    https://code.visualstudio.com/docs/agent-customization/prompt-files (text after the name)."""
    meta, body = parse_command(path)
    name, src = meta["name"], f"{COMMANDS_DIR}/{pathlib.Path(path).name}"
    oc = "\n".join(["---", f"description: {_q(meta['description'])}", "---",
                    f"<!-- GENERATED from {src} of the aiagents kit; do not edit -->",
                    body.replace(ARGS_TOKEN, "$ARGUMENTS")])
    vs = "\n".join(["---", f"name: {name}", f"description: {_q(meta['description'])}",
                    f"argument-hint: {_q(meta['argument-hint'])}", "agent: agent", "---",
                    f"<!-- GENERATED from {src} of the aiagents kit; do not edit -->",
                    body.replace(ARGS_TOKEN, "the text the user typed after the command name (may be empty)")])
    return {"opencode": (COMMAND_OUTPUTS["opencode"].format(name=name), oc),
            "vscode": (COMMAND_OUTPUTS["vscode"].format(name=name), vs)}


PACK_KEYWORDS = {
    "payroll-gr": ("payroll", "payslip", "salary"),
    "multi-tenant-saas": ("tenant", "multi-tenant", "row level security", "row-level security"),
    "postgres-infra": ("postgres", "pgx", "psycopg"),
    "aws-serverless-cost": ("aws::serverless", "aws-sdk", "aws-lambda", "aws sam", "samconfig"),
    "auth-sessions-mfa": ("totp", "mfa", "two-factor", "session cookie"),
}
EXTRA_AGENTS_CODE = ("developer", "test-engineer", "security-reviewer", "architect", "quick-tasks")
EXTRA_AGENTS_DOCS = ("architect", "quick-tasks")
_SCAN_FILES = ("README.md", "AGENTS.md", "go.mod", "package.json", "template.yaml", "template.yml",
               "samconfig.toml", "docker-compose.yml", "compose.yaml")


def _git_remote(root):
    cfg = root / ".git" / "config"
    if not cfg.is_file():
        return None
    m = re.search(r'\[remote "origin"\][^\[]*?url\s*=\s*(\S+)', cfg.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def detect(target):
    """Read-only guesses for /setup: repo type, name, owner, AI tool, relevant packs and agents.
    Never reads secrets: only well-known manifest files (first 64 KiB) and .git/config."""
    root = pathlib.Path(target).resolve()
    types = []
    if (root / "go.mod").is_file():
        types.append("backend-go")
    pkg = root / "package.json"
    if any(root.glob("next.config.*")) or (pkg.is_file() and '"next"' in pkg.read_text(encoding="utf-8", errors="replace")):
        types.append("frontend-nextjs")
    if any((root / f).is_file() for f in ("template.yaml", "template.yml", "samconfig.toml")):
        types.append("serverless-sam")
    if not types:
        types.append("docs-hub")
    remote = _git_remote(root)
    name, owner = root.name, None
    if remote:
        m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", remote)
        if m:
            owner, name = m.group(1), m.group(2)
    host = None
    if remote:
        m = re.search(r"(?:@|://)(?:[^@/]+@)?([^/:]+)", remote)
        host = m.group(1) if m else None
    tools = []
    if (root / ".opencode").is_dir() or any(root.glob("opencode.json*")):
        tools.append("opencode")
    if (root / ".vscode").is_dir() or (root / ".github" / "copilot-instructions.md").is_file():
        tools.append("vscode")
    blob = ""
    for f in _SCAN_FILES:
        p = root / f
        if p.is_file():
            blob += p.read_text(encoding="utf-8", errors="replace")[:65536].lower() + "\n"
    packs = sorted(k for k, words in PACK_KEYWORDS.items() if any(w in blob for w in words))
    if "serverless-sam" in types and "aws-serverless-cost" not in packs:
        packs.append("aws-serverless-cost")
    agents = list(EXTRA_AGENTS_DOCS if types == ["docs-hub"] else EXTRA_AGENTS_CODE)
    return {"types": types, "type": types[0], "project_name": name, "owner": owner,
            "code_host": host, "ai_tools": tools, "packs": sorted(packs), "agents": agents}
