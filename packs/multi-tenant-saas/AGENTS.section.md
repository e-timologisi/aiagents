## Multi-tenancy (pack: multi-tenant-saas)

Every request authenticates and authorizes tenant membership. Queries are explicitly tenant-scoped; PostgreSQL row-level security is defence in depth. Never trust a tenant id supplied only by the client. Shared/admin functions need audited, explicit authorization. Cross-tenant exposure is a release blocker. Rules: `docs/rules/multi-tenancy-isolation.md`.
