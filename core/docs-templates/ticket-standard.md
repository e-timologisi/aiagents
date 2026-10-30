# Ticket standard: definition of ready and labels

Canonical issue forms live in `.github/ISSUE_TEMPLATE/` (`feature.yml`, `bug.yml`, `decision.yml`; blank issues disabled). Every {{PROJECT_NAME}} repo uses the same forms.

## Definition of ready

An issue is **ready** when:

1. Every template field is filled; "none" is a valid answer, empty is not.
2. Affected repos are listed and the change order follows `{{DOCS_REPO}}/docs/architecture/service-map.md`.
3. Acceptance criteria are numbered and testable (authorization denial included when data is touched).
4. **No open decision**: needed ADRs are accepted; legal/domain questions are answered or explicitly out of scope ("to be validated by {{DOMAIN_EXPERT}}").
5. No secrets or personal data in the issue.

Turn vague requests into ready tickets with the `task-intake` skill; it asks the human instead of guessing.

## Labels

| Label | Use when |
|---|---|
| `needs-triage` | Default on new issues; owner has not evaluated it |
| `needs-info` | Any field is missing or a decision/question is open |
| `ready-for-agent` | **Only** when the definition of ready is fully met; an agent may implement, a human reviews and merges |
| `ready-for-human` | Needs owner-only access (servers, databases, releases, secrets) or human judgement |
| `wontfix` | Will not be done |
| `area:architecture`, `area:infra`, `area:security`, `area:domain` | Area; add all that apply |

Create them once per repo: `gh label create ready-for-agent --color 0E8A16` (repeat per label).

Multi-repo work: one parent issue plus per-repo child issues that start with `Part of {{ORG}}/<repo>#<n>` (see the `cross-repo-feature` skill).
