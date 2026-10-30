---
name: project-state
description: "Maintain docs/project-state.md - the single file that lets any agent resume a project in a fresh chat: phase, gate status, decisions log, open questions, ticket table, risks, next actions. Use after every lead step and at the start of every new session."
---

# Project state

Template: `docs/agents/templates/project-state.md.tmpl`.

## Schema
1. **Phase**: 1 Intake · 2 Brief · 3 Decisions · 4 Architecture · 5 Bootstrap · 6 Backlog · 7 Dispatch · 8 PR gates · 9 Release · 10 Report.
2. **Gates**: GATE 1–4 with status (`not reached` / `waiting` / `approved <date>` / `changes requested`).
3. **Decisions log**: date, decision, chosen option, who decided, ADR link.
4. **Question queue** (asked one question at a time, in this order): #, question, blocking yes/no, recommended/default answer, status (`queued` / `asked` / `answered` / `default taken` / `skipped` / `later`), answer.
5. **Tickets**: issue, repo, agent, branch, PR, status, review rounds.
6. **Risks**: risk, impact, mitigation, owner.
7. **Next actions**: who does what next.
8. **Session log**: date, what happened (one line).

## Updating
- Update after every step, before reporting. Append to logs; never rewrite history.
- No secrets, personal data or server details.

## Resuming in a fresh chat
1. Read `docs/project-state.md`, then the brief, register and latest ADRs.
2. Summarise the state for the owner in five lines and confirm the phase.
3. Refresh PR/ticket statuses with `gh` before acting.
