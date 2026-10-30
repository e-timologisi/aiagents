---
name: implement-ticket
description: 'Implement a ticket — an issue is labelled `ready-for-agent`.'
argument-hint: 'issue URL'
agent: developer
---
<!-- GENERATED from prompts/04-implement-ticket.md by scripts/build-prompts.py -->
Implement ${input:issue_url} in this repo (type ${input:repo_type}). Use the developer agent (infra-developer for serverless-sam).

- backend-go: migration (expand) → contract → handler; skills add-endpoint/add-migration; denial tests for every data path.
- frontend-nextjs: confirm the API change is merged/on staging first; skills add-page/consume-api; no `any`, no secrets in NEXT_PUBLIC_*.
- serverless-sam: skills add-lambda/add-schedule/s3-storage; least-privilege IAM, no database access, never deploy from your machine.

Work on a branch from the default branch, TDD, run lint/test/integration/build until green, open a PR linking the issue.
Push every fix commit to the same branch; never merge. Hand off to test-engineer then security-reviewer.
Report: PR URL and head SHA, checks, staging URL checked, docs updated, follow-ups.
