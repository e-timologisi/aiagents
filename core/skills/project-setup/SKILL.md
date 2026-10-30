---
name: project-setup
description: "Set up the aiagents workflow (AGENTS.md, service map, glossary seed, agents, skills, ticket standard) in a new or existing project by interviewing the owner and inspecting repos read-only. Use when bootstrapping a project or onboarding an existing repo to the agent workflow."
---

# Project setup

**Prefer the `lead` agent.** It runs the whole pipeline (intake → brief → decisions → architecture → bootstrap → backlog) with owner gates and calls this skill only for the bootstrap step (GATE 3 approved). Use this skill directly only when the kit must be installed into repos whose plan is already agreed. For an existing repo, run `explorer` first (`codebase-discovery`) and use its dossier instead of the analysis below.

Two modes. Decide which applies first; ask if unclear.

## Mode A: new project (no code yet)
Ask **one question at a time** (`docs/agents/interaction-standard.md`), each with a recommended default and options the owner can accept with "ok", in this order:
1. Name, GitHub org, one-sentence purpose, who the users are.
2. Repos: single repo or split (backend / frontend / jobs / docs hub)? Recommended: a docs hub plus one repo per runtime.
3. Stack per repo (repo type: `backend-go`, `frontend-nextjs`, `serverless-sam`, `docs-hub`, or "other").
4. Data and tenancy: multi-tenant? personal data? regulated domain? → which packs (`multi-tenant-saas`, `auth-sessions-mfa`, domain packs).
5. Environments and release: staging URL, production URL, who may release (recommended: owner-only manual release).
6. Domain expert who validates rules (accountant, lawyer, clinician...).
7. Commands: lint, test, integration, build (defaults from `repo-types/<type>/type.yaml`).

Then show the full plan (repos, types, packs, `--set` values) and wait for "approved".

## Mode B: existing repo(s)
1. **Read-only analysis**: languages, build files, test runners, CI workflows, existing `AGENTS.md`/`CONTRIBUTING.md`/docs, branch protection (`gh api repos/<org>/<repo>/branches/<branch>/protection` if permitted). Never run builds that need secrets; never read `.env` or secret values.
2. Propose: repo type per repo, packs, placeholder values, list of files to **add**, and conflicts with existing files (which are never overwritten).
3. Wait for approval. Only add files; never change application code, CI or existing docs. Suggested edits to existing files go into the report (or a follow-up issue).

## Apply (both modes)
```
python3 <kit>/scripts/apply-kit.py --type <type> --target <repo> --set PROJECT_NAME=... --set ORG=... --set DOCS_REPO=... [--pack ...] --dry-run
python3 <kit>/scripts/apply-kit.py ... (same, without --dry-run)
python3 scripts/sync-agents.py --check   # in the target
```
Then fill the generated skeletons: `docs/architecture/service-map.md` (ownership, interfaces, routing table, change order), `GLOSSARY.md` seed (5–15 terms from the interview), first ADR (repo split and release flow), labels from `docs/agents/ticket-standard.md` (`gh label create`).

## Rules
- Never invent facts about the domain; seed the glossary with terms the owner used and mark legal ones "to be validated by an expert".
- Never print secrets; list secret **names** that CI will need.
- Commit on a branch and open a PR per repo; the human merges.

## Output
Plan or proposal (before approval); after applying: created/skipped files per repo, `sync-agents --check` result, open questions, follow-up issues.
