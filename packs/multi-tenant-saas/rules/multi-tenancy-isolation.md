# Multi-tenancy isolation

- Every data access validates tenant membership of the authenticated user and scopes queries by tenant explicitly.
- The tenant comes from the server-side session and membership, never from the client alone (path, body, header).
- Every tenant table has `tenant_id NOT NULL`, `ENABLE` + `FORCE ROW LEVEL SECURITY`, and a fail-closed policy based on `current_setting('{{TENANT_SETTING}}', true)` (no rows when unset).
- Set the tenant with `SET LOCAL` inside the transaction; prove with a test that it does not leak between pooled connections.
- Membership carries one role; permissions are a capability matrix checked server-side, deny by default. Role names and capabilities need product sign-off.
- Superadmin access is deliberate, audited and minimal.
- Tests: for every data path a cross-tenant denial test (tenant A cannot read/write tenant B), plus fail-closed behaviour without tenant context.
- Global tables (users, sessions) are documented as non-tenant and never hold tenant data.
- Logs, metrics and object keys use opaque ids; no tenant data in shared caches without the tenant in the key.
