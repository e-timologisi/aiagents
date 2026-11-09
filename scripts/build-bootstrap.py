#!/usr/bin/env python3
"""Generate bootstrap/commands/ (global /setup and /start-here for OpenCode and VS Code) from
packs/conversational-start/commands/. Usage: python3 scripts/build-bootstrap.py [--check]"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kitlib import KIT  # noqa: E402
from stacks import bootstrap_outputs  # noqa: E402

OUT = KIT / "bootstrap"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    wanted, bad = bootstrap_outputs(), []
    for rel, text in sorted(wanted.items()):
        path = OUT / rel
        current = path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8") if path.exists() else None
        if current != text:
            bad.append(rel)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
    existing = {p.relative_to(OUT).as_posix() for p in (OUT / "commands").rglob("*") if p.is_file()}
    stale = sorted(existing - set(wanted))
    if args.check:
        for rel in bad + stale:
            print(f"error: bootstrap/{rel} is out of date: run python3 scripts/build-bootstrap.py", file=sys.stderr)
        return 1 if bad or stale else 0
    for rel in stale:
        (OUT / rel).unlink()
    print(f"wrote {len(bad)} file(s), removed {len(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
