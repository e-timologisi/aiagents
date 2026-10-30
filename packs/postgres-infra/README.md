# Pack: postgres-infra

For projects that run their own PostgreSQL on rented servers/VMs. Adds four agents and a rule:

| Agent | Role | Does |
|---|---|---|
| `server-inspector` | inspector | Read-only inventory; every remote command approved by the owner |
| `postgres-architect` | inspector | Placement, network isolation, TLS, roles, backups; gated step plan |
| `postgres-deployer` | implementer (edit ask) | Executes one approved step, records status |
| `postgres-security-reviewer` | inspector | Independent audit before go-live |

Expected project docs (create them in the docs hub under `{{INFRA_DOCS}}/`): `server-audit.md`, `postgresql-deployment-plan.md` (ordered steps with gates: approve / do / check / undo), `postgresql-security-plan.md`, runbooks. Keep credentials out of all of them. Server identifiers go only where the owner approves.
