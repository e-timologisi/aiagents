# Pack: multi-tenant-saas

For SaaS products where customers' data share one database. Adds:
- `docs/rules/multi-tenancy-isolation.md` — non-negotiable isolation rules
- skill `tenant-table` — new tenant-scoped table with fail-closed row-level security and tests
- an AGENTS.md section on tenancy

Cross-tenant exposure is a release blocker.
