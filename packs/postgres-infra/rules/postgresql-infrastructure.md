# PostgreSQL infrastructure safety rules

- Verify server identities and configuration before proposing changes. Production and staging databases are separate instances with distinct credentials.
- Discovery is read-only; request explicit approval for remote command execution. A conversational rule is not a sandbox: enforce least-privilege SSH, command allowlists and separate read-only credentials.
- Never install packages, restart services, modify firewalls, disks, DNS, SSH, containers, databases or credentials without explicit approval of target and action. Approval for staging is not approval for production.
- On shared hosts, determine CPU, RAM, storage, IOPS and free ports before installing; do not disrupt existing services.
- Never default to public 5432 or a database reachable through a public reverse proxy. Prefer a private network, native PostgreSQL TLS with certificate verification (`verify-full`), WireGuard if needed. Private networking is not by itself encryption.
- Host firewall and `pg_hba.conf` both limit source addresses; SCRAM auth; least-privilege roles; separate migration and application identities.
- Never copy production personal data to staging; never log database secrets or personal data.
- Back up off-server with encryption, WAL/PITR where appropriate, alert on failure, test a restore and document RPO/RTO.
- Prefer straightforward single instances on a supported PostgreSQL release with documented updates; no HA cluster, Kubernetes or extra machines without an explicit requirement.
- Halt on conflicting identity, insufficient capacity, uncertain firewall policy, unsupported OS or an unexpected pre-existing database.
- Independent security review before production go-live.
