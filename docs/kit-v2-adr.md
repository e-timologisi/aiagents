# ADR: conversational start (kit v0.7 beta)

Status: accepted by the owner (all 14 recommendations of the kit v2 plan). Scope of this change: phases 0 and 1 plus the conversational-start pack.

## Decisions
1. Target audience A (non-technical) first; developers keep using `apply-kit.py` directly.
2. Python-only scripting (no WSL, no PowerShell duplicates). Port work (paths, CRLF, Windows CI) is a later phase.
3. Entry points are slash commands installed once (`/setup`, `/start-here`); no pasted prompt, no `@` names.
4. `setup` is a separate agent and the only role that installs software (winget on Windows, Homebrew on macOS; Linux outside the beta).
5. Stacks live in `stacks/` next to `repo-types/`; four are aliases. `--type` is supported indefinitely.
6. Local git by default; a hosted copy only after plain approval. Administrator installs only after an explanation and approval, user-scope preferred, never the password in chat.
7. Follow the person's language; files and commands stay English. No telemetry.
8. Versions: 0.7 beta, 1.0 after the beginner trial passes on two clean machines with two models. Misthodosia stays pinned and is untouched.

## Consequences
- The additive-only rule is enforced by `scripts/baseline-0.6.4.json` in `check-kit.py`; the baseline file itself and the files listed as "optional section" (README, HOWTO, CHANGELOG, VERSION, `apply-kit.py`, `check-kit.py`, the CI workflow) are the only changed existing files.
- Lead behaviour changes only through a pack overlay; without the pack it is byte-identical.
- Open uncertainties: OpenCode behaviour when a command names an agent that does not exist (the global `/start-here` therefore carries no `agent:`), the VS Code user prompts folder path per OS, Windows path of `~/.config/opencode`, winget ids on a clean machine, and weaker models ignoring the approval rules.
