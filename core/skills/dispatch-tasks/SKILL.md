---
name: dispatch-tasks
description: "Brief implementation and review agents on ready tickets - exact self-contained prompts per agent, branch names, parallelism and cost rules, and verification that each PR contains all intended commits. Use when the lead hands tickets to agents."
---

# Dispatch tasks

Subagents do not see the lead's conversation: every brief is self-contained.

## Brief template (implementers)
```
Agent: <developer | infra-developer | test-engineer>
Ticket: <issue URL>   Repo: <org/repo>   Branch: <feat/slug> (from origin/{{DEFAULT_BRANCH}})
Goal: <one sentence>
Acceptance criteria: <numbered, copied from the ticket>
Read first: AGENTS.md, CONTRIBUTING.md, <contract/files>, skills <ids>
Constraints: do not merge; push every commit to this branch; no secrets; docs Definition of done
Owner decision needed? Stop and return ONE question with a recommended answer and options; do not guess
Depends on: <merged PR/contract version or "none">
Report: PR URL, head SHA, commit list, checks run, docs updated, open questions
```

## Brief template (reviewers)
```
Agent: <security-reviewer | domain-reviewer>
PR: <URL> at head <sha>   Round: initial | after fixes
Focus: <auth/tenancy/crypto/domain rules touched>
Report: verdict, findings by severity with file:line, second review needed?
```

## Parallelism and cost
- Independent tickets (different repos/files, no dependency) may run in parallel.
- Ask the owner before running more than 3 agents at once; state the expected cost (each agent is a separate model session).
- Dependent tickets run in order; consumers start only after the provider PR is merged (or the contract is merged).

## After each implementer report
1. `gh pr view <n> --json headRefOid,commits,reviewDecision` — head SHA matches the report; every intended commit is listed.
2. `gh pr checks <n>` — CI green.
3. Read all review comments (`gh pr view <n> --comments`), including automated reviewers; each one is fixed or answered.
4. Update the ticket table in `docs/project-state.md`.

## Decisions inside delegated work
Subagents cannot chat with the owner. Every brief includes: "If you need a decision from the owner, stop and return ONE question with a recommended answer and 2–4 options instead of guessing." The lead then asks the owner **one question at a time** (`docs/agents/interaction-standard.md`) and re-dispatches with the answer.
