# Changelog

## 0.3.0 — 2026-10-30

First public-ready version (MIT).
- Added LICENSE (MIT), SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md (Contributor Covenant 2.1), CODEOWNERS, issue forms, PR template, Dependabot config and the `check-kit` workflow (SHA-pinned actions, read-only token).
- Replaced the project-specific example with `examples/bookit/`, an invented toy example.
- `check-kit.py`: forbidden-string scan uses generic built-in patterns plus optional local regexes from the untracked `.kit-forbidden.txt`; unit tests in `scripts/test_kitlib.py`.
- `payroll-gr` pack: disclaimer (not legal/tax/accounting advice; validate with a qualified expert).
- README: status, safety notes, contributing, security, license.

## 0.2.1 — 2026-10-29

- Interaction standard (`docs/agents/interaction-standard.md`): agents ask the owner ONE question per turn with a recommended answer, 2–4 options with consequences and "other"; most blocking first; adapt to answers; running summary every 3–5 answers; shortcuts "go with your suggestions", "skip", "later", "recommend for me"; subagents return ONE question instead of guessing. Short form in every agent's Rules (enforced by `check-kit.py`).
- `sync-agents.py`: every role gets OpenCode `question` `*` allow; VS Code roles with a tools list get `vscode/askQuestions` (both documented tools).
- Skills updated for one-question-at-a-time: project-intake (explicit loop, example turns), document-ingest, requirements-register, backlog-planning, dispatch-tasks, status-report, project-state (question queue), codebase-discovery, task-intake, project-setup, writing-for-agents.
- lead: gates are single yes/changes questions; decisions presented one at a time; walks dossier questions one by one.
- explorer/dossier: top-3 blocking questions + "Later"; branch claims name branch, base and hashes; counts from the files; optional approval-gated secrets-history COUNT on shallow clones.
- Prompts 00-start-here, 00-new-project-bootstrap, 01, 02, 08 (+ VS Code); HOWTO "How the agents ask you questions".

## 0.2.0 — 2026-10-29

- New `lead` agent (role `orchestrator`): single entry point running intake → brief (GATE 1) → decisions/ADRs (GATE 2) → architecture (GATE 3) → bootstrap → backlog (GATE 4) → dispatch → PR gates → release prep → reports, resumable from `docs/project-state.md`.
- New `explorer` agent (read-only) + skill `codebase-discovery` + `project-dossier.md.tmpl`.
- `sync-agents.py`: new role `orchestrator` (OpenCode `mode: primary`, docs-only edits, read-only git/gh allowlist, `subagent` allow; VS Code tools incl. `agent` and `agents: ['*']`). Existing roles unchanged. Projects copying the script should update it.
- New skills: `project-intake`, `document-ingest`, `requirements-register`, `backlog-planning`, `dispatch-tasks`, `status-report`, `project-state`.
- New templates (installed to `docs/agents/templates/`): project brief, requirements register, project state, status report, decision brief, project dossier, worked examples.
- New prompt `00-start-here`; `01-existing-project-onboarding` now runs explorer → dossier → lead. `project-setup` defers to `lead`.
- `HOWTO.md` for owners; `check-kit.py` validates the new role, skills, templates and files.

## 0.1.0 — 2026-10-29

Initial kit extracted from real multi-repo projects (docs, ui, api, serverless repos).

- core: 7 generic agents (single-source format), `sync-agents.py`, 12 skills (incl. new `project-setup` and `release-checklist`), issue forms, PR template, CODEOWNERS, `agents-sync.yml`, CI skeleton, docs templates (AGENTS.md, ticket standard, onboarding, service map, ADR, glossary, how-to-use-agents, release and security checklists).
- repo types: `backend-go`, `frontend-nextjs`, `serverless-sam`, `docs-hub`.
- packs: `multi-tenant-saas`, `payroll-gr`, `postgres-infra`, `aws-serverless-cost`, `auth-sessions-mfa`.
- prompts 00–11 plus generated VS Code prompt files.
- scripts: `apply-kit.py` (install/update with manifest), `check-kit.py`, `build-prompts.py`.
- examples: reference snapshot of a multi-repo setup (replaced by an invented example in 0.3.0).
