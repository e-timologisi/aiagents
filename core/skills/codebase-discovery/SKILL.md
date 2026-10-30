---
name: codebase-discovery
description: "Read-only discovery of an existing codebase into an evidence-based project dossier (architecture, key flows with file:line, data model, delivery, health, security, unknowns). Use when onboarding an existing project or before changing an unfamiliar area."
---

# Codebase discovery

Template: `docs/agents/templates/project-dossier.md.tmpl`. Output path: `docs/discovery/<repo>.md` (added to the repo only after owner approval).

## Evidence tags
Every claim ends with a tag and a citation:
- `[verified]` — observed by running a read-only command or approved test (state the command)
- `[read-from-code]` — read in the source (`path:line`)
- `[inferred]` — reasoned from indirect evidence (say from what)
Trust code over docs; record each disagreement in "Docs vs code".

## Steps
1. **Overview (cheap)**: tree to depth 2, languages, build files, entry points, CI workflows, README. Report and ask before going deeper.
2. **Architecture**: components, runtime boundaries, external services, configuration (env var NAMES only).
3. **Key flows**: 3–5 most important user flows traced step by step with `path:line`; optional mermaid sequence diagram.
4. **Data model & tenancy**: schema/migrations, ownership/tenant boundaries, how authorization scopes data.
5. **Delivery**: build, test and lint commands, CI/CD jobs and their gating, environments, release mechanism.
6. **Health**: test coverage areas and gaps, dependency age and known vulnerabilities (from lockfiles/advisories readable offline or approved scanners), tech debt hot spots.
7. **Security findings**: severity, `path:line`, description, suggested fix. Secrets: location and kind only, never the value.
8. **Unknowns & questions**: at most the TOP 3 BLOCKING questions up front (each with a recommended answer), the rest under "Later". Ask the owner at most one question at a time during discovery; normally return questions to the lead, who walks the owner through them one by one.

## Evidence rules
- Branch claims (merged / not merged / ahead / behind) name the branch, the base branch compared with and both commit hashes.
- Line and file counts come from the files themselves (`wc -l`, `git ls-files | wc -l`).
- Secrets history (optional, approval-gated): on a shallow clone ask ONE question whether to deepen history; then a targeted `git log -S'<pattern>' --format='%h %ad'` gives a COUNT plus first/last commit date only, never values.

## Rules
- No side effects: no writes, installs, migrations, network calls to project services. Existing tests only with owner approval.
- Multi-repo or large codebases: one explorer per repo/module in parallel; the lead merges dossiers.
