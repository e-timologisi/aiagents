---
name: cross-repo-feature
description: "Plan and deliver a {{PROJECT_NAME}} task that spans more than one repo, using the project service map for ownership and change order. Use when a ticket touches several services, adds an endpoint consumed by another repo, or changes a contract."
---

# Cross-repo feature

Follow these steps in order. Stop and ask the owner when a step cannot be completed.

## 1. Read
- `{{DOCS_REPO}}/docs/architecture/service-map.md` (ownership, routing table, change order).
- ADRs in `{{DOCS_REPO}}/docs/adr/` that touch the area; `GLOSSARY.md` for terms.
- Each affected repo's `AGENTS.md` and `CONTRIBUTING.md`.

## 2. Check the issue is ready
Every field of the feature template must be filled (`docs/agents/ticket-standard.md`) and no decision open. If not, run `task-intake` and ask; do not start implementation.

## 3. Plan per repo (ordered)
Write a short plan in the parent issue: for each repo, in the service map's change order, list files/areas, tests and the PR it produces. Create child issues starting with `Part of {{ORG}}/<repo>#<parent>`.

## 4. Decision and contract first
- Architectural change → ADR in `{{DOCS_REPO}}` (`docs/adr/template.md`), merged or owner-approved before code depends on it.
- Contract (OpenAPI, events, schemas) changes land in the provider repo first. Additive only; never remove or repurpose a field in place.

## 5. Provider repo (usually the backend)
- Migrations: forward-only, **expand** step only; contract step later, in a separate release.
- Tests: unit, integration, authorization denial (cross-tenant denial in multi-tenant projects).
- Checks green; request `security-reviewer`, and `domain-reviewer` for domain rules.

## 6. Consumer repos (frontend, jobs)
Implement only against the merged/staged contract. Never code against an invented endpoint.

## 7. Branches and PRs
- Same branch name in every repo (e.g. `feat/<slug>`).
- Each PR: `Part of {{ORG}}/<repo>#<parent>`, `Closes #<child>`, links to sibling PRs.
- Merge in change order; never push to `{{DEFAULT_BRANCH}}`; never trigger production releases.
- Coupled changes are released together (provider first); note the coupling in each PR.

## 8. Never
- Touch staging/production databases or servers from CI or a laptop.
- Commit or print secrets/personal data; invent external API contracts.

## 9. Done
Apply "Definition of done: documentation" in `AGENTS.md` for every repo touched; comment on the parent issue with links to all PRs and docs updated; open issues for deferred work (e.g. the contract migration).
