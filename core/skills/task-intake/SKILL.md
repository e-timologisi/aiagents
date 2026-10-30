---
name: task-intake
description: "Turn a vague {{PROJECT_NAME}} request into a ready ticket (goal, affected repos, acceptance criteria, out of scope, docs to update, risks). Use when someone asks for work that is not yet a fully specified issue, or before labelling an issue ready-for-agent."
---

# Task intake

Goal: produce a ticket that satisfies `docs/agents/ticket-standard.md`. Never guess a missing decision.

## Steps
1. Read `docs/architecture/service-map.md`, relevant ADRs and `GLOSSARY.md` (in `{{DOCS_REPO}}`).
2. Restate the request in one sentence: who needs what, and why.
3. Route it with the service-map routing table → affected repos, in order.
4. Draft the ticket using the fields of `.github/ISSUE_TEMPLATE/feature.yml` (or `bug.yml` / `decision.yml`):
   - Goal; user story
   - Affected repos
   - Acceptance criteria (testable, numbered; include an authorization-denial case if data is touched)
   - Out of scope
   - Data impact (new tables/fields, migrations expand/contract, contract changes)
   - Domain / legal impact (claims → "to be validated by an expert"; no figures invented)
   - Docs to update
   - Risks and open questions
5. List every open decision as a question. **Ask the human one question at a time** (`docs/agents/interaction-standard.md`: recommended answer, 2–4 options, most blocking first) instead of filling it in. Typical open decisions: legal interpretation, external API contract, auth design, who may do what (roles), data retention.
6. If an architectural decision is needed, propose a `decision.yml` issue / ADR first and mark the feature blocked by it.
7. Label: `needs-info` while questions are open; `ready-for-agent` only when every field is filled and no decision is open; `ready-for-human` if it needs owner-only access or judgement. Add matching `area:*` labels.
8. Create the issue with `gh issue create` (in the repo with most of the work, or `{{DOCS_REPO}}` for multi-repo parents) only after the human confirms the draft.

## Output
The ticket body in Markdown, the proposed labels, and the list of questions for the human.
