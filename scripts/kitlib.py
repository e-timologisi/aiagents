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
]


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
