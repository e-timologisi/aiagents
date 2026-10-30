---
name: tenant-table
description: Add a tenant-scoped table with fail-closed row-level security, least-privilege grants and cross-tenant denial tests. Use when a migration creates a table that holds customer data.
---

# Tenant table

Use together with `add-migration`. Rules: `docs/rules/multi-tenancy-isolation.md`.

```sql
CREATE TABLE things (
    id         uuid        PRIMARY KEY,
    tenant_id  uuid        NOT NULL REFERENCES tenants (id),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX things_tenant_id_idx ON things (tenant_id);

ALTER TABLE things ENABLE ROW LEVEL SECURITY;
ALTER TABLE things FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON things
    USING (tenant_id = nullif(current_setting('{{TENANT_SETTING}}', true), '')::uuid)
    WITH CHECK (tenant_id = nullif(current_setting('{{TENANT_SETTING}}', true), '')::uuid);

-- Grant the runtime role only what it needs (e.g. no UPDATE/DELETE on immutable tables).
```

## Steps
1. Migration with the template above (owner role, grants per the project's migration conventions).
2. Repository code runs inside the tenant transaction helper (sets `{{TENANT_SETTING}}` with `SET LOCAL`) and still filters by `tenant_id`.
3. Integration tests: tenant A cannot read/insert/update/delete tenant B rows; no rows without tenant context; setting does not leak across pooled transactions.
4. Request `security-reviewer`.
