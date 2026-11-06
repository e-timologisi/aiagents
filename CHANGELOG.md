# Changelog

## 0.6.0 — 2026-11-06

Process gates and lessons from months of multi-repo agent work, as generic, tool-neutral improvements. Addresses #17 (retro template), progress on #2 and #3.
- Handover gate: new `docs/agents/handover-rules.md` (agent's `AGENT-REPORT tip=<sha>` PR comment, lead's per-PR procedure, wait for the review bot, verify the default branch by content through the hosting API, tracker updates only after a verified merge) and read-only `scripts/handover-check.sh <owner/repo> <pr> [local-clone]` (open PR, `mergeStateStatus` CLEAN, 0 unresolved threads, latest run per check name green, head == latest report tip; label as info; `--json-file` test hook).
- Opt-in CI templates installed to `docs/ci-templates/` (never auto-enabled): `agent-report.yml` (label + current-head report from an allowed author + label after report; `rerun-on-report` job; not required by default), `pinned-actions.yml` with `scripts/check-pinned-actions.py` (40-hex SHAs, docker `sha256:` digests, flow-style/quoted keys, ignores `with`/`env` keys named `uses`), `ticket-key.yml` (`placeholder-key` rule: no key 0, no leading zeros).
- Kit's own `agents-sync.yml` and `ci-skeleton.yml` now pin actions to SHAs verified with `gh api`.
- New templates: `docs/agents/autonomy-policy.md`, `docs/agents/templates/decision-log.md`, `docs/agents/templates/retro-template.md`. New placeholders `AGENT_REPORT_LABEL`, `AGENT_REPORT_AUTHORS`, `MAX_PARALLEL_AGENTS` (with defaults).
- Agents: own worktree per agent, HTTPS + CLI credential helper fallback, `CI ran (run link)` vs `ran locally`, no placeholder ticket keys, tool-doc version noted; lead: review-bot wait, handover script and label, resume the same agent session for fixes, severity routing, autonomy policy, outage rule, retros; security-reviewer: design-review mode for ADRs and two reviews for auth/session/token/crypto; domain-reviewer: calculation-heavy logic reviewed before merge; test-engineer: mutation sanity check.
- Handover pitfalls: "no checks yet" is pending (`EXPECTED_CHECKS` placeholder), red `agent-report`/`UNSTABLE` before the label is expected, report comment first then the check output as a separate comment, stop rule for review bots that re-review every push, shared index files "touched by others" in the dispatch template, reserved keys created before merge, pending decisions to the decision log plus a follow-up ticket (ticket standard, domain docs).
- Permissions: autonomy policy carries an OpenCode v2 recipe (ordered rules, last match wins, agent rules last). `sync-agents.py`: reviewer, planner, docs and orchestrator roles no longer carry their own `shell *` ask (global rules apply); the inspector keeps it and re-appends `SHELL_DENY` after it; `check-kit.py` and tests reject any broad shell allow in generated role rules. Regenerate agents with `python3 scripts/sync-agents.py` after updating.
- `/setup` asks three yes/no questions (handover gate, pinned-actions guard, autonomy policy) with recommendations; lean profile installs the new files.
- `check-kit.py`: new required files, new placeholders in use, handover script has no mutating gh/git command, all workflows and CI templates pinned, home-directory paths and hosted tracker sites added to the forbidden scan. New tests `scripts/test_gates.py`.

## 0.5.0 — 2026-11-04

`/setup` command with a lean default install and a tool-neutral connections step. Addresses #2.
- New single source `core/commands/setup.md`, rendered at install time to `.opencode/commands/setup.md` (OpenCode) and `.github/prompts/setup.prompt.md` (VS Code). Interview: one question at a time with a recommended answer, `skip` everywhere, detection first, no secrets, servers/databases/credentials never asked; connections: code host, ticket tracker, wiki and the method for each (`mcp`, `cli`, `api`, `manual`) with generic login and read-only check; documented fallbacks; writes `.aiagents/access.md`.
- `apply-kit.py`: `--profile lean|full` (default full, unchanged), `--agent`, `--bootstrap` (command files only), `--detect` (read-only JSON). Manifest stores `profile` and `agents`; `--update` keeps them. Identical existing files are adopted as unchanged.
- New placeholders `CODE_HOST_NAME`, `CODE_HOST_METHOD`, `TRACKER_METHOD`, `WIKI_URL`, `WIKI_METHOD` (all with defaults); used by access-and-conflicts and `ticket-tracker`.
- `lead` reads `.aiagents/access.md` at session start; `check-kit.py` checks the command source, its rules and the lean profile names; new tests `scripts/test_setup.py`; CI smoke test also installs the lean profile.
- README quick start leads with `/setup`; HOWTO updated.

## 0.4.0 — 2026-11-01

Parallel-work conflict prevention, access fallback and a generic tracker agent. Addresses #14, #15, #16.
- `lead`: conflict-prevention rules (files per agent before parallel work, serialize overlaps, merge order with PR links, re-check open PRs after every merge, same-file work shares a ticket/branch, never merge before the final report, verify the default branch by content and why).
- Every core agent has an `## Access` paragraph (cheapest read-only check, say it once, `Access:` line, no invented keys, opt-in servers/secrets, merge default branch before reporting and report the tip SHA).
- New agent `ticket-tracker` (generic, optional): updates ticket and wiki after a verified merge with guard rails. New placeholders `TRACKER_*` and `WIKI_*` (all have defaults).
- New installed docs `docs/agents/access-and-conflicts.md` (rules + dispatch template) and `docs/agents/templates/work-log.md` (`LOCAL-<n>` fallback).
- `dispatch-tasks` brief gains `Access:` and file lists; README/HOWTO lessons 11–12.
- `check-kit.py` enforces the Access paragraph and the lead rules.

## 0.3.1 — 2026-10-30

Third-party attribution.
- Added `THIRD-PARTY-NOTICES.md`: full MIT license texts of mattpocock/skills (© 2026 Matt Pocock) and humanlayer/skills (© 2026 HumanLayer) and a programmatic provenance table (kit path → upstream path, commit, ratio, modifications).
- Third-party skill directories (`code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grilling`, `pr`, `tdd`, `writing-for-agents`) now carry `LICENSE.upstream` and `UPSTREAM.md`; derived docs templates (`domain.md`, `issue-tracker.md`, `triage-labels.md`) have an attribution comment.
- `apply-kit.py` installs `docs/agents/THIRD-PARTY-NOTICES.md` whenever third-party files are installed (managed by `--update`).
- `check-kit.py` checks attribution (UPSTREAM.md ⇒ LICENSE.upstream, listed in the notices, both licenses in full); tests added.
- `pr/CREDITS.md`: `show-me` link now points to humanlayer/skills.
- NOTICE, README (license) and CONTRIBUTING (third-party material rule) clarified: the kit is MIT © e-timologisi; third-party material keeps its own MIT notices.

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
