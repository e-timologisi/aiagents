---
name: add-migration
description: Add a database schema migration to {{REPO_NAME}} (expand/contract, backward compatible, least-privilege grants, integration test). Use when a ticket needs a new table, column, index, constraint or policy.
---

# add-migration

Migrations are numbered SQL files in `{{MIGRATIONS_DIR}}/NNNN_name.sql`, applied by the project's migration runner in a one-off job in the target environment, never from CI or a laptop against staging/production.

## Rules
- **Never edit an applied migration.** Fix forward with a new file; next number, zero-padded.
- **Backward compatible.** The running release must work with the new schema (deploys migrate before switching, rollback does not undo). Split breaking changes: expand (new table / nullable column) → backfill → switch code → contract (drop old) in a later release.
- Avoid long locks on big tables; plan large index builds separately.
- Least privilege: grant the runtime role only what it needs (no `UPDATE`/`DELETE` on immutable/audit tables).
- No values that change by law or policy as literals; no seed data with real people.
- Multi-tenant projects: follow the `multi-tenant-saas` pack (tenant column, row-level security, fail-closed policy).

## Tests
Integration test on a throwaway database: migrations apply on an empty DB and on the previous schema; constraints and policies behave (denial cases included). Run `{{INTEGRATION_CMD}}`.

## Docs
README migration notes if the process changes; ADR for new data-ownership or retention decisions; `security-reviewer` for anything touching roles, grants or policies.
