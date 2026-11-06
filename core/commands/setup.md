---
name: setup
description: Configure the aiagents kit in this repo with a short interview (lean install, packs, connections)
argument-hint: '(empty) | add <pack or agent> | access'
---
# /setup: configure the aiagents kit in this repo

Arguments: <ARGUMENTS>

You configure the aiagents kit inside the repository open in this session. You run a short interview and then install with the kit's own script. You change only kit files, `.aiagents-manifest.json` and `.aiagents/access.md`; no application code.

## Hard rules
- Ask ONE question at a time. Every question shows a recommended answer and can be answered with a short reply or `skip`. "go with your suggestions" accepts every remaining recommendation.
- Detect before asking; never ask what the repo already shows.
- NEVER ask for, accept, print or store tokens, passwords, API keys or other secrets. If the user pastes one, say it must be revoked and do not use or repeat it. Logins happen in the browser or in the user's own terminal.
- Servers, databases and credentials are NEVER part of /setup; do not ask about them.
- Do not assume any particular code host, tracker or wiki. Record what the team chose; the team decides how to connect.
- Before writing anything, show the exact command and ask one yes/no question. Never overwrite existing files (the script refuses anyway); never commit, push or open a PR unless the user asks.

## Step 0: find the kit and read the arguments
- Kit path: the first line of `.aiagents/kit.local` (written by `apply-kit.py --bootstrap`). If it is missing, ask for the path of the local kit checkout (recommended: `~/src/aiagents`). Call it KIT below.
- Arguments `add <name>`: if `.aiagents-manifest.json` is missing, say so and run the full interview instead. Otherwise `<name>` is a pack (`ls KIT/packs`) or an agent; show `python3 KIT/scripts/apply-kit.py --target . --update --pack <name>` (or `--agent <name>`) with `--dry-run` first, ask yes/no, run it, then stop.
- Argument `access`: run Step 3 (connections) and Step 5 (access summary) only; record changed answers with `python3 KIT/scripts/apply-kit.py --target . --update --set KEY=VALUE ...` (dry-run first, yes/no).
- Otherwise: full interview.

## Step 1: detect (read-only, no questions)
Run `python3 KIT/scripts/apply-kit.py --target . --detect`. It returns JSON with `types` (repo type guesses: `backend-go`, `frontend-nextjs`, `serverless-sam`, `docs-hub` for docs-only), `project_name`, `owner`, `code_host`, `ai_tools`, suggested `packs` and `agents`. You also know which tool you are running in (OpenCode or VS Code Copilot); that is the AI tool, not a question. If `.aiagents-manifest.json` exists, the kit is installed: offer `add`, `access` or `--update` instead of a new install.

## Step 2: project questions (one per turn)
1. "Detected stack: <type>. Correct?" Recommended: the first guess. Options: the other types. Several repos in one project: this repo is one type; `docs-hub` holds decisions.
2. "Project name and owner (org or user): <name>, <owner>?" Recommended: the detected values. `skip` keeps them. The owner is used only for CODEOWNERS text.
3. Only for code repos: "Where do decisions and ADRs live: this repo or a separate docs repo?" Recommended: this repo (adds `--standalone`).

## Step 3: connections (tool-neutral, one per turn, each skippable)
Ask a), then its method, then b) and its method, then c) and its method. Ask a URL/project/key prefix only when the method needs it, one value per turn; those values are not secrets.
- a) "Which code host, if any?" GitHub / GitLab / other (name it) / none. Recommended: the detected `code_host`, else none.
- b) "Which ticket tracker, if any?" Jira / Linear / GitHub Issues / other (name it) / none. Recommended: none for a new solo project.
- c) "Which wiki or docs site, if any?" Name it, or none. Recommended: none (docs stay in the repo).
- d) For each chosen one: "How should agents reach <name>?" `mcp` (an MCP server configured in the AI tool) / `cli` (a command-line tool the user logs into) / `api` (HTTP API; the user's own environment provides the auth) / `manual` (agents prepare text, a person applies it). Recommended: the method the team already uses; if unsure, `manual`.

For the chosen method show the generic login and read-only check; the user runs the login, you run only the check:

| Method | Login (by the user, never in chat) | Read-only check |
|---|---|---|
| mcp | Add the server to the AI tool's MCP config (URL or command only); sign in through the browser flow it opens | Its cheapest "current user" or "list" tool |
| cli | `<tool> auth login` (or the tool's equivalent) in the user's own terminal | `<tool> auth status`, or a list call with a limit of 1 |
| api | Credentials live in the user's environment or keychain, never in files of this repo or in chat | One GET of the "current user" endpoint, run by the user |
| manual | none | none |

If a check fails, say so once and use the fallback; do not retry in a loop.

Fallbacks (from `docs/agents/access-and-conflicts.md`):
- No code host: commit locally and report instead of pushing.
- No tracker: copy `docs/agents/templates/work-log.md` to `docs/work-log.md`; keys are `LOCAL-<n>`.
- No wiki: no mirroring; docs stay in the repo.

## Step 4: lean install, then offers
The default is the lean profile: agents `lead` and `explorer`; skills task-intake, dispatch-tasks, tdd, diagnosing-bugs, code-review, grilling, domain-modeling, codebase-design, pr; `AGENTS.md`, interaction standard, access-and-conflicts, work-log template and this command.
Then ask yes/no, one per turn, ONLY for what Step 1 marked relevant:
- each suggested pack: "Add the <pack> pack? <one-line purpose from KIT/packs/<pack>/README.md>". Recommended: yes.
- "Add the role agents <agents from detect> so the lead can dispatch implementation and reviews?" Recommended: yes for code repos.
Everything else can be added later with `/setup add <pack or agent>`.

Build the command, show it and ask "Install? yes / changes":
`python3 KIT/scripts/apply-kit.py --target . --profile lean --type <type> --set PROJECT_NAME=<name> --set ORG=<owner> [--set DOCS_REPO=<repo>] [--standalone] [--pack <p> ...] [--agent <a> ...] [--set CODE_HOST_NAME=...] [--set CODE_HOST_METHOD=...] [--set TRACKER_NAME=...] [--set TRACKER_METHOD=...] [--set TRACKER_URL=...] [--set TRACKER_PROJECT=...] [--set TRACKER_KEY_PREFIX=...] [--set WIKI_NAME=...] [--set WIKI_METHOD=...] [--set WIKI_URL=...]`
Run it with `--dry-run` first, summarise created/skipped in two lines, then run it for real. Skipped answers keep the defaults. For a no-tracker answer also create `docs/work-log.md` from the template if it does not exist.

## Step 5: access summary
Write `.aiagents/access.md` (overwrite only this file) in this shape, without secrets:

```
# Access summary (written by /setup; the lead reads it at session start)
Updated: <YYYY-MM-DD>
Access: code host <name> via <method> ✅/❌/skipped, tracker <name> via <method> ✅/❌/skipped, wiki <name> via <method> ✅/❌/skipped, servers ❌ (not configured by /setup), database: local only
| Resource | Choice | Method | Check result | Fallback |
|---|---|---|---|---|
| Code host | ... | ... | ok / failed / not checked | commit locally and report |
| Tracker | ... | ... | ... | docs/work-log.md with LOCAL-<n> keys |
| Wiki | ... | ... | ... | no mirroring |
```

## Step 6: report
Five lines at most: what was installed (profile, packs, agents), what is connected and how, what was skipped and its fallback, and the next step: "Talk to the `lead` agent; it reads `.aiagents/access.md`. Commit the new files on a branch when you are ready." Mention `/setup add <name>` and `/setup access`.
