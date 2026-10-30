---
name: add-schedule
description: Add a scheduled or time-triggered job to {{REPO_NAME}} using EventBridge Scheduler. Use when a job must run on a cron/rate or at a specific time (reminders, periodic exports, retries).
---

# Add a schedule (EventBridge Scheduler)

Use **EventBridge Scheduler** (`AWS::Scheduler::Schedule` / `AWS::Scheduler::ScheduleGroup`), not legacy EventBridge rules. Create the target function first with `add-lambda`.

## Design rules
- **Time zone**: `ScheduleExpressionTimezone: {{SCHEDULE_TIMEZONE}}` for business-time schedules; document the expression in local time in a comment.
- **Target**: prefer Scheduler → SQS → Lambda (buffering, retries, DLQ). Direct Scheduler → Lambda is fine for low-volume idempotent jobs.
- **Retries/DLQ**: `RetryPolicy` and a DLQ with encryption; with SQS a redrive policy and visibility timeout ≥ 6× function timeout. Values in an environment mapping.
- **Idempotency**: at-least-once delivery; derive an idempotency key from schedule name + scheduled time and let the backend deduplicate.
- **IAM**: scheduler role trusted only by `scheduler.amazonaws.com` (consider `aws:SourceAccount`), permission only on the exact target.
- **Naming/tags**: `{{STACK_PREFIX}}-<name>-${Environment}`; tags `Project`, `Environment`.
- **Staging**: disabled or lower frequency via a mapping to avoid noise and cost.
- **Payload**: identifiers only, no personal data; never trust an owner/tenant id from the payload without the backend authorizing it.

## Cost
Check current pricing rather than assuming free tier. Prefer one schedule that fans out over one schedule per customer.

## Verify and document
`{{TEST_CMD}}`, `{{INTEGRATION_CMD}}`, `{{BUILD_CMD}}`. Update README resources, `{{DOCS_REPO}}` notes/ADR and the issue.
