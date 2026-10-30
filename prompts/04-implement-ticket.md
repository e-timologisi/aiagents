<!-- vscode: agent=developer; hint=issue URL -->
# 04 — Implement a ticket

**When to use:** an issue is labelled `ready-for-agent`.

**Placeholders:** `<ISSUE_URL>`, `<REPO_TYPE>` (backend-go | frontend-nextjs | serverless-sam).

## Prompt

````text
Implement <ISSUE_URL> in this repo (type <REPO_TYPE>). Use the developer agent (infra-developer for serverless-sam).

- backend-go: migration (expand) → contract → handler; skills add-endpoint/add-migration; denial tests for every data path.
- frontend-nextjs: confirm the API change is merged/on staging first; skills add-page/consume-api; no `any`, no secrets in NEXT_PUBLIC_*.
- serverless-sam: skills add-lambda/add-schedule/s3-storage; least-privilege IAM, no database access, never deploy from your machine.

Work on a branch from the default branch, TDD, run lint/test/integration/build until green, open a PR linking the issue.
Push every fix commit to the same branch; never merge. Hand off to test-engineer then security-reviewer.
Report: PR URL and head SHA, checks, staging URL checked, docs updated, follow-ups.
````
