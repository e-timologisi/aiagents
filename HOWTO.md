# HOWTO — running a project with the aiagents kit

A plain-language guide for the project owner. No engineering background needed.

## What this kit is (in 5 lines)
1. A set of AI "team members" (agents) with fixed jobs: a lead, planners, builders, testers and reviewers.
2. You talk mainly to one of them, the **lead**. It asks you questions, writes the plans and hands work to the others.
3. Nothing important happens without your approval: there are four **gates** where you say "approved" or "change this".
4. Agents never merge code, release to production, touch servers or show passwords. You (or someone you trust) do those.
5. Everything is written down in the project's `docs/` folder, so any new chat can pick up where the last one stopped.

## Three ways to start

All three begin with the same prompt: `prompts/00-start-here.md` (in VS Code: type `/start-here`). Keep the line that fits.

**1. You have an idea (chat)**
```
@lead start project BookIt. IDEA: a simple booking app for hair salons; customers pick a free slot, staff see the day's bookings.
```
The lead asks one question at a time, each with a recommended answer and a few options. You can reply "go with your suggestions".

**2. You have documents (specs, tender, notes, screenshots)**
Attach the files in the chat (or put them in a `docs/input/` folder) and write:
```
@lead start project BookIt. DOCUMENTS: the attached spec.pdf and notes.md. Use document-ingest.
```
The lead lists every requirement with where it found it (document and page), plus contradictions and gaps.

**3. You have an existing project**
```
@lead onboard the existing project at ../bookit-api and ../bookit-web.
```
The lead first sends the **explorer** for a quick, read-only look at each repo, shows you a short summary and asks before a deeper (more expensive) look. The explorer's report (the "dossier") marks each statement as checked, read in the code, or guessed, and never shows secret values. You confirm the open questions; then the lead continues as above.

## How the agents ask you questions

- **One question at a time.** The next question depends on your last answer.
- Every question shows a **recommended answer**, 2–4 options with what each means for you, and "other".
- In OpenCode and VS Code you may see a small form with buttons (the built-in question tool); otherwise it is a normal chat message.
- Agents don't ask what your documents or code already answer; they tell you what they understood and only ask to confirm if it matters.
- Every 3–5 answers you get a short summary to confirm.
- Shortcuts: **"go with your suggestions"**, **"recommend for me"**, **"skip"**, **"later"**. Defaults taken are written to `docs/project-state.md` (question queue), so you can revisit them.
- Approval gates are a single question: "Approve? yes / changes".

Example:
```
Lead:  Will customers need an account to book?
       Recommended: A — quicker to build, less personal data to protect.
         A) No — name and phone are enough
         B) Yes — they can see and cancel their bookings online
         Other: tell me
You:   A
Lead:  Should staff get a reminder of tomorrow's bookings?
       Recommended: B — useful, but can wait for version 2.
         A) Yes, in version 1 (one e-mail per day)
         B) Later
You:   recommend for me
Lead:  Taking B (noted as a default). Summary so far: customers book without account; staff log in;
       reminders later. Is this right?
You:   yes
```

## First-time setup (install the kit into a repo)

You need `git`, `python3` and the GitHub CLI `gh` (logged in). Then:

```sh
git clone <aiagents repo URL> ~/src/aiagents                       # once
cd ~/src/my-project                                                 # a new or existing repo
python3 ~/src/aiagents/scripts/apply-kit.py --type docs-hub --target . \
  --set PROJECT_NAME=BookIt --set ORG=my-org --dry-run              # preview: what would be added
python3 ~/src/aiagents/scripts/apply-kit.py --type docs-hub --target . \
  --set PROJECT_NAME=BookIt --set ORG=my-org                        # install
```
- Types: `docs-hub` (decisions and plans), `backend-go`, `frontend-nextjs`, `serverless-sam`. Code repos also need `--set DOCS_REPO=<name of the docs repo>`. A one-repo project can use any type plus `--standalone`.
- Optional packs add rules for special topics: `--pack multi-tenant-saas`, `--pack auth-sessions-mfa`, `--pack payroll-gr`, `--pack postgres-infra`, `--pack aws-serverless-cost`.
- Existing files are **never overwritten**; the script lists what it created and skipped.
- It writes `.aiagents-manifest.json` in the repo root (the list of kit files and the values you chose).
- Later, to get kit improvements: `python3 ~/src/aiagents/scripts/apply-kit.py --target . --update` (files you edited yourself are left alone and reported as "conflict").
- Commit the new files on a branch and open a pull request (or ask the lead to do it).

Easier: once the kit is installed in one docs repo, the lead can propose and run these commands for other repos after GATE 3.

## How to call agents

### OpenCode
- `@lead …` — start or continue the project (the lead is a "primary" agent; you can also select it with Tab).
- `@explorer map ../bookit-api, overview only` — read-only discovery.
- Other agents: `@architect`, `@developer`, `@infra-developer`, `@test-engineer`, `@security-reviewer`, `@domain-reviewer`, `@quick-tasks`. Usually the lead calls them for you.
- Skills: ask "use the task-intake skill: …" (or the skill name, e.g. `@status-report`).

### VS Code (GitHub Copilot)
- Open the repo (or a workspace with all repos). In Copilot Chat choose the **Local** harness, then pick **lead** from the agent dropdown.
- Type `/` for skills and prompt files (e.g. `/start-here`, `/write-ticket`, `/review-pr`).
- **Subagents:** VS Code documents that, in the Local harness, a custom agent can run other custom agents as subagents when its file lists the `agent` tool and an `agents` list; the kit's lead has both. Turn on **Run Subagent** under **Configure Tools** if it does not delegate. Limits (from the VS Code docs): subagents do not see your chat (the lead writes self-contained briefs), cannot ask you questions, and cannot start further subagents unless you enable `chat.subagents.allowInvocationsFromSubagents`. In the **Copilot** harness the `agents` field is not supported. **Fallback:** if delegation is unavailable, ask the lead to "print the task prompts" and paste each one into a new chat with the named agent selected.
- In VS Code the lead's file-editing tool cannot be limited to documentation files the way OpenCode can; the lead's instructions forbid code edits, and reviewers stay read-only.

## The approval gates

| Gate | You approve | Before that, agents may | Agents never do without you |
|---|---|---|---|
| GATE 1 | Project brief (what we build, for whom, v1 scope) | ask questions, read documents, explore code read-only | invent requirements or legal facts |
| GATE 2 | Decisions (one brief per open question → recorded as ADR) | compare options, recommend | choose for you |
| GATE 3 | Architecture plan (repos, environments, security, data) | draft the plan | create repos, environments, secrets |
| GATE 4 | Backlog (list of tickets, order, sizes) | draft tickets | create GitHub issues |
| Every PR | Merge | build, test, review, fix | merge |
| Release | Press "Release to production" | prepare the checklist | release, touch servers/DNS/cloud |

Always yours: merging, releasing, passwords and secrets (agents may only mention their *names*), server and cloud changes, legal/domain truth (agents mark such claims "to be validated by an expert").

## A first day, worked example (fictional "BookIt")

1. **You:** `@lead start project BookIt. IDEA: salons publish free slots; customers book without an account; staff see the day.`
2. **Lead** asks one question at a time, each with a recommendation: Who signs in? → you: "A, staff only". Several salons, each seeing only its own data? → "recommend for me" (yes; adds the multi-tenant pack). Payments? → "go with your suggestions" (no online payment, English only). You add: "plus Greek". The lead summarises the four answers and asks "Is this right?" → "yes".
3. **Lead** writes `docs/requirements-register.md` (R-001 book a slot, R-002 staff see own salon only …) and `docs/project-brief.md`, then: "GATE 1: please approve the brief". **You:** "approved".
4. **Decisions:** the lead (with the architect) brings two decision briefs: *staff login: e-mail link vs password + MFA* and *hosting: managed platform vs own server*, each with cost, risks and a recommendation. **You** pick; the lead records ADR 0001 and 0002 → GATE 2.
5. **Architecture plan:** three repos (`bookit-docs` docs-hub, `bookit-api` backend-go, `bookit-web` frontend-nextjs), staging + production, packs `multi-tenant-saas`, `auth-sessions-mfa` → GATE 3. **You:** "approved; create the repos".
6. **Bootstrap:** the lead shows the exact `gh repo create` and `apply-kit.py` commands, runs them after your OK, and opens one setup PR per repo. You merge them.
7. **Backlog:** 3 epics, 9 tickets with sizes S/M and order (API before web), two can run in parallel → GATE 4. **You:** "approved"; the issues are created.
8. **Dispatch:** the lead asks "start 2 agents in parallel (cost: two sessions)?" **You:** "yes". `developer` builds ticket #4 in bookit-api on branch `feat/staff-day-view` and opens a PR; `test-engineer` adds tests; `security-reviewer` reviews (and again after fixes, because it touches login). The lead checks that every commit is in the PR and no review comment is left open.
9. **You** merge the PR (GitHub button), test on staging, and tell the lead "staging looks good".
10. **Release prep:** the lead runs the release checklist (main contains the reviewed commits, checks green, your staging test, order API → web) and says "ready". **You** press "Release to production".
11. The lead updates `docs/project-state.md` and gives you a short status report.

Documents produced that day: requirements register, project brief, decision briefs + ADRs, service map, project state, status report, 9 issues, PRs.

## Resuming in a fresh chat
Write: `@lead resume from docs/project-state.md`. The lead reads the state file (phase, gates, decisions, open questions, tickets), summarises it in five lines, checks PR statuses and continues. Keep the state file committed.

## Keeping kit and repos in sync
- **Agents changed?** Edit only `agents/<name>.md`, then `python3 scripts/sync-agents.py` (the generated `.opencode/` and `.github/agents/` files must be committed; CI checks with `--check`).
- **Kit improved?** In each repo: `python3 ~/src/aiagents/scripts/apply-kit.py --target . --update`, review, PR.
- **Changing the kit itself?** `python3 scripts/check-kit.py` must say "ok"; add a CHANGELOG line and bump `VERSION`.

## Troubleshooting

| Problem | What to do |
|---|---|
| Agent not visible | Run `python3 scripts/sync-agents.py`; OpenCode: type `@` and check the list; VS Code: Chat view → right-click → Diagnostics; agent names are case-sensitive |
| Skill not found | It must be in `.agents/skills/<name>/SKILL.md` with `name: <name>` in its header |
| "stale" from sync-agents --check | Someone edited a generated file or forgot to regenerate: run `python3 scripts/sync-agents.py` and commit |
| `--update` reports conflict | You changed that kit file; compare with the kit version and merge by hand, or keep yours |
| Lead does not delegate in VS Code | Local harness, **Run Subagent** enabled; otherwise ask it to print task prompts |
| Very large documents | Upload in parts or as text/markdown; the lead processes them in chunks and lists which parts it read |
| Scanned PDF unreadable | Provide a text version; the lead names the pages it could not read |
| Costs feel high | Ask for "overview only", limit parallel agents (the lead asks before more than 3) |

## Where things are (in the kit)
- `prompts/` — copy-paste prompts (`00-start-here` first); `prompts/vscode/` — the same as VS Code `/` commands.
- `core/` — agents, skills, templates that every repo gets.
- `repo-types/` — extras per kind of repo (Go backend, Next.js web, AWS serverless, docs hub).
- `packs/` — optional topic rules (multi-tenant, auth/MFA, Greek payroll, PostgreSQL servers, AWS cost).
- `examples/bookit/` — a small invented example (a simpler, single-salon, single-repo variant of the BookIt story above) showing the documents the lead and its skills produce.

## Lessons learned (why the rules exist)
1. Before a release, check that the main branch really contains the reviewed fixes — a merge taken from an early commit can silently drop later fixes.
2. Never build or deploy unless the checks passed in the same run.
3. Agents never read or print secret values; check secret names only — a tool that shows configuration can leak credentials into chat logs.
4. Deploy secrets come from the CI system, never typed onto servers by hand.
5. Some GitHub plans lack "required reviewers": write down the accepted risk and the precondition (e.g. before adding collaborators).
6. Reviewers only read; builders hand off to tester → security reviewer → human merge.
7. Login, sessions and encryption changes get two security reviews.
8. Documentation is part of "done".
9. The API contract is agreed before the screens are built.
10. Legal and domain statements are "to be validated by an expert".

---

## Cheat sheet (one page)

| I want to… | Do this |
|---|---|
| Start anything | `@lead` + `prompts/00-start-here.md` (VS Code `/start-here`) |
| Start from an idea | `@lead start project X. IDEA: …` |
| Start from documents | attach files, `@lead start project X. DOCUMENTS: …` |
| Onboard existing code | `@lead onboard the existing project at <paths>` (explorer goes first) |
| Continue tomorrow | `@lead resume from docs/project-state.md` |
| Accept recommendations | "go with your suggestions" / "recommend for me" / "skip" / "later" (agents ask one question at a time) |
| Approve a gate | "GATE n approved" (or say what to change) |
| Turn an idea into a ticket | `/write-ticket` or "use the task-intake skill: …" |
| Get a review | `/review-pr <PR URL>` |
| Prepare a release | `/release-to-production` → then you press the release button |
| Install the kit | `python3 ~/src/aiagents/scripts/apply-kit.py --type <type> --target . --set PROJECT_NAME=… --set ORG=… [--dry-run]` |
| Update the kit in a repo | `python3 ~/src/aiagents/scripts/apply-kit.py --target . --update` |
| Regenerate agents | `python3 scripts/sync-agents.py` |
| Never | let agents merge, release, touch servers, or show secret values |
