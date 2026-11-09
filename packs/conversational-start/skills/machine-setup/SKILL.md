---
name: machine-setup
description: Procedure for the setup agent to prepare a person's computer (Windows or macOS) for a chosen stack with one approval per install, verification and an undo log. Use when tools are missing.
---
# Machine setup

Only the `setup` agent runs these steps. One question at a time.

## 1. Detect (read-only)
- Windows: `winget --version`; macOS: `brew --version`; `python --version` (or `python3 --version`). Say what is present.
- No package manager: Windows without winget: send the person to the vendor installer page of the tool and explain each click; macOS without Homebrew: explain what Homebrew is and ask before running its installer from its official site (a separate approval; never pipe a download into a shell).

## 2. Plan
Read `python3 scripts/apply-kit.py --stack-info <id> --os <windows|macos>`. Show the person the table of missing tools: name, why, size or time if known, `admin` yes/no. Tools with `optional: true` are skipped unless asked.

## 3. For each missing tool (one approval each)
1. Plain words: "I want to install <tool> (<why>). Command: `<install>`. OK?" If `admin` is true, first explain that the installer may ask for administrator rights, what changes, and offer a user-scope alternative; never ask for the password in chat.
2. Run only after "yes". On "no" skip and explain what will not work.
3. Verify with `check` against `min`; a new terminal session may be needed for the PATH: say so.
4. Append a block to `docs/setup-log.md` (template `docs/rules/setup-log-template.md`): time, command, reason, result, undo command (`winget uninstall --id <id>` or `brew uninstall <formula>`). Also copy the log outside the project when the person agrees.

## 4. Kit
Apply the kit to the current folder: `apply-kit.py --stack <id> --pack conversational-start --target . --set ...` with `--dry-run` first, then ask, then for real. Never overwrite files; read the dry-run output to the person in plain words.

## 5. Undo and failures
- "Undo setup": replay the logged undo commands one by one, each with its own approval.
- No internet, winget missing, install denied or blocked by company policy: stop with a clear message, leave no half-state, offer a retry. Never bypass a block.
- Secrets: never display or store them; the person types them into a file you only name.
