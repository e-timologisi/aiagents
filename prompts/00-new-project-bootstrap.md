<!-- vscode: agent=agent; hint=project name and one-sentence purpose -->
# 00 — New project bootstrap

**When to use:** starting a brand-new (possibly multi-repo) project and you want the full agent workflow from day one.

**Placeholders:** `<PROJECT_NAME>`, `<PURPOSE>`, `<KIT_PATH>` (local clone of aiagents).

## Prompt

````text
Use the project-setup skill (mode A, new project) from <KIT_PATH>/core/skills/project-setup/SKILL.md.

Project: <PROJECT_NAME> — <PURPOSE>.

Interview me ONE question at a time, each with a recommended default and options I can accept with "ok", adapting to my answers:
repos and repo types, stack and commands, tenancy/personal data/regulated domain (→ packs), environments and URLs,
who releases, who validates domain/legal claims.

Then show the complete plan: repos to create, type per repo, packs, every --set value, the apply-kit commands
(--dry-run first), the first ADR (repo split + release flow), labels to create, and a glossary seed.
Wait for my "approved" before creating repos or files. Never print secrets; list only secret NAMES CI will need.
After applying: run `python3 scripts/sync-agents.py --check` in each repo, open one PR per repo, and report
created/skipped files, open questions and follow-up issues.
````
