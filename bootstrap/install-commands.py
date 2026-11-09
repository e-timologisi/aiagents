#!/usr/bin/env python3
"""One-time install of the global /setup and /start-here commands (and the OpenCode `setup` agent).

Usage (from the unpacked kit):  python3 bootstrap/install-commands.py [--vscode] [--dry-run] [--force]
  OpenCode  -> ~/.config/opencode/commands/*.md and ~/.config/opencode/agents/setup.md
  --vscode  -> the user prompts folder of VS Code, only when its User folder exists
  Also writes ~/.aiagents/kit.path (the folder of this kit) so /setup can find the kit.
Never overwrites a different existing file unless --force; standard library only.
"""
import argparse
import os
import pathlib
import shutil
import sys

KIT = pathlib.Path(__file__).resolve().parent.parent
SRC = KIT / "bootstrap" / "commands"


def vscode_prompts_dir():
    home = pathlib.Path.home()
    if sys.platform == "win32":
        base = pathlib.Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = home / ".config"
    return base / "Code" / "User" / "prompts"


def copy(src, dest, force, dry):
    if dest.exists():
        if dest.read_bytes() == src.read_bytes():
            print(f"  unchanged: {dest}")
            return
        if not force:
            print(f"  skipped (exists, different; use --force): {dest}")
            return
    print(f"  {'would write' if dry else 'wrote'}: {dest}")
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vscode", action="store_true", help="also install the VS Code user prompt files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite different existing files")
    args = ap.parse_args()
    if not SRC.is_dir():
        print(f"error: {SRC} not found (run this from an unpacked kit)", file=sys.stderr)
        return 2
    home = pathlib.Path.home()
    oc = home / ".config" / "opencode"
    print(f"aiagents kit at {KIT}")
    for f in sorted((SRC / "opencode").glob("*.md")):
        copy(f, oc / "commands" / f.name, args.force, args.dry_run)
    for f in sorted((SRC / "opencode-agents").glob("*.md")):
        copy(f, oc / "agents" / f.name, args.force, args.dry_run)
    if args.vscode:
        target = vscode_prompts_dir()
        if target.parent.is_dir():
            for f in sorted((SRC / "vscode").glob("*.prompt.md")):
                copy(f, target / f.name, args.force, args.dry_run)
        else:
            print(f"  VS Code user folder not found at {target.parent}: in VS Code run 'Chat: New Prompt File', "
                  "choose User, and paste the files from bootstrap/commands/vscode/")
    kit_path = home / ".aiagents" / "kit.path"
    print(f"  {'would write' if args.dry_run else 'wrote'}: {kit_path}")
    if not args.dry_run:
        kit_path.parent.mkdir(parents=True, exist_ok=True)
        kit_path.write_text(str(KIT) + "\n", encoding="utf-8")
    print("next: restart OpenCode (or VS Code), open an empty folder and type /setup")
    return 0


if __name__ == "__main__":
    sys.exit(main())
