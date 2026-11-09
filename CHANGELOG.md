# Changelog

## 0.7.0-beta — 2026-11-09

Conversational start (phases 0-1 of the kit v2 plan). **Additive only**: `repo-types/`, the five packs, the core agents, prompts, `core/placeholders.yaml` and the existing `apply-kit.py` usage are unchanged. `--type` stays supported (nothing is deprecated in 0.x). New `scripts/baseline-0.6.4.json` lists every file that must stay byte-identical to v0.6.4; `check-kit.py` verifies it.
- **Stack profiles** `stacks/<id>/stack.yaml` (schema in `stacks/README.md`): `web-nextjs`, `api-go`, `docs-hub`, `serverless-sam` (aliases of the existing repo types, no duplicated files), `api-node`, `data-python` (own templates), `mobile-expo` (beta stub). Fields: category, plain-language title, `fits`/`not_for`, per-OS support, `needs_mac`, `toolchain` (check, minimum, winget/brew install commands, why, admin), accounts, risks, `run_cmd`.
- **Pack `conversational-start`** (beta): `setup` agent (the only role that installs software; every shell command asks; edits only `docs/setup-log.md`), `lead` overlay (core lead text plus one marked block, inactive unless `docs/project-state.md` is missing), skills `stack-selection`, `machine-setup`, `save-work`, `explain-change`, rules `safety-model` and `setup-log-template`, project-level `/start-here` (`agent: lead`).
- **Global commands** `/setup` and `/start-here` for OpenCode (`~/.config/opencode/commands/`, plus the `setup` agent in `agents/`) and VS Code prompt files, generated into `bootstrap/commands/` by `scripts/build-bootstrap.py`; one-time `bootstrap/install-commands.py` (stdlib; never overwrites without `--force`; `--dry-run`).
- `apply-kit.py`: new optional flags `--stack`, `--list-stacks`, `--stack-info [--os]`; manifests record `stack` only when `--stack` is used; `--target` is checked in code instead of by argparse. Output for `--type` is byte-identical to 0.6.4 (checked on all four repo types).
- `check-kit.py`: stack schema, pack and overlay checks, bootstrap currency, additive-only baseline. Tests in `scripts/test_stacks.py`; CI smoke test applies every stack with the pack.
- Not done yet (later phases): Windows CI job and path/CRLF port, beginner trials T1-T8, release zip with checksum, generated permission templates, desktop and Flutter stacks.

## 0.6.4 — 2026-11-11

- **Lead model default moved from the premium to the mid tier**: `MODEL_PLANNER` now defaults to the same model as `MODEL_REVIEWER`; the premium model stays an explicit choice (`MODEL_PREMIUM`). Reversible with one placeholder (`--set MODEL_PLANNER=<premium model>`). `check-kit.py` and tests enforce the defaults.
- Lessons ported generically: implementers (linters with every CI build tag; database-code rules: nullable CHECK comparisons, validate before INSERT, fixed-string errors, real clock for expiry, no deferred-trigger dedupe via settings, fixtures for new global guards, fail-closed trigger note, caller-set timeouts tested for cancellation, no untested safety claims, local database shim, split very large tickets, late bot reviews, re-request without response reported as missing); reviewers (reproducibility checks, restore implications); lead (tracker keys never from memory, field limits, label refresh, retarget stacked PRs, applied migrations immutable, runtime guards not asserts, verify by content, ruleset changes owner-authorised and backed up). Merged into existing bullets of the role, `handover-rules` and `how-to-use-agents` templates; `check-kit.py` checks them.

## 0.6.3 — 2026-11-10

Cost and model policy, generic.
- New placeholders `MODEL_REVIEWER` (default mid tier) and `MODEL_PREMIUM` (optional). Reviewer, architect, explorer and inspector roles (core, docs-hub, payroll and postgres packs) now use `MODEL_REVIEWER`; `MODEL_PLANNER` stays with the lead. Role text: the lead names the premium model in a dispatch only for the first review/design of new authentication, session, token, cryptography, privileged-database or calculation-critical designs; implementers never ask for a bigger model; quick-tasks uses the cheap tier.
- `handover-rules` template: "Cost and model policy" (model tiers, review tiers A/B/C, fewer and scoped reviews, compact reports, parallel cap of `MAX_PARALLEL_AGENTS` / 2 under quota pressure, one restart on HTTP 429, draft PR process: push freely, mark ready once, at most one extra bot-driven push, report states bot status). Short form in `how-to-use-agents`; lead rule.
- README and HOWTO: "host settings to consider" (limit automatic code-review requests, spending budget) as owner decisions the kit never changes.
- `check-kit.py` checks the new text and placeholders and that reviewer roles default to `MODEL_REVIEWER` while the premium model is never a role default; tests added.

## 0.6.2 — 2026-11-09

Process lessons from a long multi-repo project, ported generically.
- Standing rule "lessons feed the agents" in the `how-to-use-agents` and `AGENTS.md` templates (with a definition-of-done line); agent reports list lessons learned and the agent files they should change.
- Implementer roles (developer, infra-developer, test-engineer, quick-tasks and the repo-type variants): report only when the final tip has a review-bot review or a quoted quota message (a missing or quota-limited review is never clean), batch fixes, at most one extra bot-driven push, push early after provider interruptions, stacked PRs after a squash, tracker keys looked up and field limits checked, never claim unchecked results. Roles that touch schema also get the migration rules (version-number-only runners, never edit an applied migration, check ALL open PRs for the next number, privileged steps as runtime guards).
- Reviewer and planner roles: state what was NOT read or run, severity with file:line and fix, review routing (two security reviews for auth/session/token/crypto, one for tenant or personal data in the UI, domain review, database-security review, short re-check, design review before implementation).
- `handover-rules` template: final-tip bot review rule, report contents (bot status, migration numbers, files touched by others, lessons), label remove-and-re-add after each new report, lead-posted report for branch-update commits, stacked PR conflicts, verify by content, migrations, tracker keys, review routing. Dispatch template gains a migration-number line; lead agent checks lessons and migration numbers.
- `check-kit.py` checks the new lesson text; README lists the lessons.

## 0.6.1 — 2026-11-07

Hardened permissions recipe for autonomous runs (ported from real use; generic).
- `docs/agents/autonomy-policy.md` recipe: every force-push form denied (`-f`, `--force*` incl. `--force-with-lease`, `+refspec`, also `git <options> push`); recursive `rm` forms ask; `gh api` sensitive path components (rulesets, branch protection, environments, secrets, variables, dependabot secrets, hooks, keys, collaborators, invitations, visibility, transfer, dispatches) and `--input` ask in any flag order; docker volume/network/image removals and prunes ask; cloud/IaC deploy tools (`aws`, `sam deploy|delete|sync|publish`, `terraform apply|destroy`, `kubectl`, `helm`) ask while validate/build/local/plan are allowed; production workflow names re-asked in more spellings; honest residual-gap list.
- `sync-agents.py`: `SHELL_DENY` renamed `DENY_SHELL` and aligned with the recipe; `REVIEWER_SHELL_RULES` appended last for reviewer/planner (no git/gh writes, `git branch` read forms only, no `gh api` write methods or `--input`, no `rm`/`mv`/`cp`/`tee`/`sed -i`); narrower `DOCS_SHELL_RULES` for the docs role (may branch, commit, push, open a PR, merge `origin/*`); `--check` fails when `DENY_SHELL` differs from the shell denies of an existing `opencode.json`.
- `check-kit.py`: the recipe's shell denies must equal `DENY_SHELL`; tests for reviewer/planner read-only rules, docs rules and the drift check. Regenerate agents with `python3 scripts/sync-agents.py` after updating.

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
