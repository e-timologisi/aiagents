#!/usr/bin/env python3
"""Fail when a GitHub Actions `uses:` reference is not pinned to an immutable version.

Usage: python3 scripts/check-pinned-actions.py [workflow files or dirs ...]   (default: .github)

Allowed:  ./local/action                         (same repository)
          owner/repo[/path]@<40-hex commit SHA>  (add the tag as a comment: `# v4.2.0`)
          docker://image@sha256:<64 hex>
Anything else (tags, branches, short SHAs, docker tags) is reported. Stdlib only; YAML-aware enough
for workflow files: only `uses` keys of steps and jobs count (quoted or flow-style keys included);
keys named `uses` inside `env:` or `with:` mappings are ignored.
Get a SHA from the hosting API, never from memory: `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.
"""
import pathlib
import re
import sys

SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
DOCKER = re.compile(r"^docker://[^@\s]+@sha256:[0-9a-f]{64}$")
KEY = re.compile(r"""^(?P<indent>\s*)(?:-\s+)?(?P<q>["']?)(?P<key>[A-Za-z0-9_-]+)(?P=q)\s*:(?P<rest>.*)$""")
FLOW_USES = re.compile(r"""[{,]\s*(["']?)uses\1\s*:\s*(?P<val>"[^"]*"|'[^']*'|[^,}\s]+)""")
IGNORED_PARENTS = {"env", "with"}
NESTED_IGNORED = re.compile(r"""(["']?)(?:env|with)\1\s*:\s*\{[^{}]*\}""")


def clean(value):
    value = re.sub(r"\s+#.*$", "", value.strip())
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def pinned(ref):
    return ref.startswith("./") or bool(SHA.match(ref)) or bool(DOCKER.match(ref))


def flow_refs(flow):
    """`uses` values of a flow mapping such as `{ name: x, uses: a/b@v1, with: { uses: y } }`."""
    flow = NESTED_IGNORED.sub("", flow)
    return [clean(m.group("val")) for m in FLOW_USES.finditer(flow)]


def uses_refs(text):
    """Yield (line number, reference) for every step/job `uses` in a workflow text."""
    stack = []  # (indent, key) of open mappings
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY.match(line)
        if not m:
            item = line.lstrip()
            if item.startswith("- {") and not any(k in IGNORED_PARENTS for _, k in stack):
                for ref in flow_refs(item[1:]):
                    yield n, ref
            continue
        indent = len(m.group("indent")) + (2 if line.lstrip().startswith("- ") else 0)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        key, rest = m.group("key"), m.group("rest")
        ignored = any(k in IGNORED_PARENTS for _, k in stack)
        if key == "uses" and not ignored:
            yield n, clean(rest)
        elif rest.strip().startswith("{") and key not in IGNORED_PARENTS and not ignored:
            for ref in flow_refs(rest):
                yield n, ref
        stack.append((indent, key))


def check_text(text):
    return [(n, ref) for n, ref in uses_refs(text) if not pinned(ref)]


def files(args):
    for a in args or [".github"]:
        p = pathlib.Path(a)
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*") if x.suffix in (".yml", ".yaml"))
        elif p.is_file():
            yield p


def main(argv):
    bad = 0
    for f in files(argv):
        for n, ref in check_text(f.read_text(encoding="utf-8")):
            print(f"{f}:{n}: not pinned to a commit SHA or digest: {ref}")
            bad += 1
    print(f"pinned-actions: {bad} unpinned reference(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
