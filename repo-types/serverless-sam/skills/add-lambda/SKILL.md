---
name: add-lambda
description: Add a new Lambda function to {{REPO_NAME}} (SAM). Use when creating a side job such as a PDF renderer, export or worker in this repo.
---

# Add a Lambda function

Constraints (`AGENTS.md`): no VPC/NAT, **never connect to the database** (call the backend with `{{API_URL_ENV}}`), arm64, least-privilege IAM, log retention always set, no secrets in the repo or stack parameters. Use an existing function as the reference.

## Steps
1. **Logic** in `internal/<name>/`: pure functions/types, no SDK globals. Table-driven tests: success, invalid input, error paths. Mock the backend and any external endpoint; never invent their contracts. Money never float.
2. **Entry point** `lambda/<name>/main.go`: thin — read env vars, build dependencies, start the handler. No business logic.
3. **Build**: run `{{BUILD_CMD}}` (each `lambda/*` → zip for linux/arm64).
4. **Template** (`template.yaml`):
   - Explicit `AWS::Logs::LogGroup` with `RetentionInDays` from an environment mapping; tags `Project`/`Environment`.
   - Function named `{{STACK_PREFIX}}-<name>-${Environment}`, JSON logs, globals for runtime/arch/memory/timeout; override only with a measured reason.
   - `Policies`: only needed statements on exact resources (prefer SAM policy templates); justify any `*` in a comment.
   - No `VpcConfig`, function URL or API Gateway unless an ADR requires it.
5. **Secrets**: owner creates them in SSM SecureString / Secrets Manager; pass only the **name** as env var; grant read on that exact secret. Never log secrets or personal data.
6. **Smoke test**: if safe to invoke with a synthetic payload, extend the CI deploy smoke test; otherwise document why. Tell the owner which IAM permission CI needs; do not change the cloud account yourself.
7. **Verify**: `{{TEST_CMD}}`, `{{LINT_CMD}}`, `{{INTEGRATION_CMD}}`, `{{BUILD_CMD}}`. Do not deploy from your machine.
8. **Docs**: README resource table, new CI variables (names only), `{{DOCS_REPO}}` infrastructure notes/ADR/GLOSSARY, related issue.
