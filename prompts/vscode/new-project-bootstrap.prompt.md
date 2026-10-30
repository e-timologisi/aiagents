---
name: new-project-bootstrap
description: 'New project bootstrap — starting a brand-new (possibly multi-repo) project and you want the full agent workflow from day one.'
argument-hint: 'project name and one-sentence purpose'
agent: agent
---
<!-- GENERATED from prompts/00-new-project-bootstrap.md by scripts/build-prompts.py -->
Use the project-setup skill (mode A, new project) from ${input:kit_path}/core/skills/project-setup/SKILL.md.

Project: ${input:project_name} — ${input:purpose}.

Interview me ONE question at a time, each with a recommended default and options I can accept with "ok", adapting to my answers:
repos and repo types, stack and commands, tenancy/personal data/regulated domain (→ packs), environments and URLs,
who releases, who validates domain/legal claims.

Then show the complete plan: repos to create, type per repo, packs, every --set value, the apply-kit commands
(--dry-run first), the first ADR (repo split + release flow), labels to create, and a glossary seed.
Wait for my "approved" before creating repos or files. Never print secrets; list only secret NAMES CI will need.
After applying: run `python3 scripts/sync-agents.py --check` in each repo, open one PR per repo, and report
created/skipped files, open questions and follow-up issues.
