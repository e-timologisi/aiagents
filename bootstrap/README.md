# Bootstrap: install `/setup` and `/start-here` once

After this one step, everything else happens by typing slash commands in OpenCode or VS Code chat. Beta; not yet trial-tested on a clean machine.

## What you get
| Command | Does |
|---|---|
| `/setup` | Detects your system, installs the tools your project needs one approval at a time (winget on Windows, Homebrew on macOS), installs the kit into the open folder |
| `/start-here` | A conversation with the project lead: your idea, a stack suggestion, then step by step with plain yes/no questions |

## Install (OpenCode)
1. Download the kit release zip from the releases page of the repository and unpack it.
2. Run once: `python3 bootstrap/install-commands.py` (macOS) or `python bootstrap/install-commands.py` (Windows). It copies two command files to `~/.config/opencode/commands/`, the `setup` agent to `~/.config/opencode/agents/` and writes `~/.aiagents/kit.path`. It never overwrites a different file without `--force`; `--dry-run` shows what it would do.
3. Without Python: copy the files by hand from `bootstrap/commands/opencode/` to `~/.config/opencode/commands/` and `bootstrap/commands/opencode-agents/setup.md` to `~/.config/opencode/agents/`, then create `~/.aiagents/kit.path` containing the folder of the unpacked kit. (Global folders as documented at https://opencode.ai/v2/docs/commands/ and https://opencode.ai/v2/docs/agents/; on Windows the same relative path under your user folder is assumed, not verified.)
4. Restart OpenCode, open an empty folder, type `/setup`, then `/start-here`.

## Install (VS Code, Copilot chat, Local sessions)
`python3 bootstrap/install-commands.py --vscode` copies the two `.prompt.md` files to the VS Code user prompts folder if it finds the User folder (the folder path is an assumption per operating system; VS Code documents only that user prompt files live in the profile). If it does not, use the command "Chat: New Prompt File", choose User, and paste the files from `bootstrap/commands/vscode/`. Then type `/setup` in the chat. Prompt files run only in Local sessions.

## Differences you should know
- OpenCode: the global `/setup` command switches the session to the `setup` agent, so its permission rules apply (every shell command asks, only version checks run freely, edits limited to the setup log). VS Code: the prompt carries the same rules as text, but no permission enforcement; approve each command yourself.
- A project that already has the kit's own `/setup` (the interview that configures the kit) keeps working: a project command replaces the global one of the same name (documented for OpenCode). Use `/start-here` for the conversation there.
- `/start-here` in a project that uses the `conversational-start` pack switches to the `lead` agent (`agent: lead` in the command; documented behaviour: the command switches the current session to that agent).

## Changing the default agent (optional, not done for you)
OpenCode can start every new session in a chosen agent with `"default_agent": "lead"` in a configuration file (https://opencode.ai/v2/docs/agents/ "Selection"). The agent must exist, be visible and primary-capable; it does not change existing sessions. The kit does not edit your configuration; `/start-here` is enough.

## Honest limits
iOS builds need a Mac with Xcode and an Apple developer account; Android builds need Android Studio (several GB); hosting, domains, payments, app-store accounts and legal topics are your decisions and your accounts; correctness is not guaranteed; a human must check the result before real users, money or personal data. No telemetry.
