# Security review checklist

Used by `security-reviewer`. Report file:line only; never quote secret values or personal data.

## Every PR
- [ ] Reviewed SHA = PR head SHA (re-review after new commits).
- [ ] No secrets, tokens, keys, connection strings or personal data in code, fixtures, logs, docs or PR text.
- [ ] Errors do not leak internals (stack traces, SQL, secret names with values).
- [ ] New dependencies are necessary, maintained and pinned (lockfile committed).

## Authentication and sessions
- [ ] Passwords hashed with a memory-hard KDF (e.g. argon2id) with bounded concurrency.
- [ ] Tokens (session, reset, verification) random, stored hashed, single-use where applicable, expiring.
- [ ] Session cookies `HttpOnly`, `Secure`, `SameSite`, host-only (`__Host-` prefix); server-side revocation.
- [ ] State-changing requests protected against CSRF (SameSite + Origin check or token).
- [ ] Redirect targets validated (no open redirects).
- [ ] Rate limits/lockouts enforced in shared storage (not per-process memory).
- [ ] Client IP taken from forwarding headers only via trusted proxies.

## Authorization and data isolation
- [ ] Every endpoint checks authentication and permission server-side; deny by default.
- [ ] Owner/tenant identifiers derived from the session, never trusted from the client alone.
- [ ] Tests prove denial for other users/tenants and missing permissions.

## Data and migrations
- [ ] Migrations backward compatible with the running release; least-privilege grants.
- [ ] Personal data minimised; retention rules respected; no lifecycle deletion of records that must be kept.

## CI/CD and infrastructure
- [ ] Build/deploy jobs `needs:` lint/test/security of the same run.
- [ ] Actions pinned; tokens least privilege; OIDC instead of long-lived cloud keys.
- [ ] Deploy secrets from environment secrets written to root-only files; never echoed.
- [ ] No data store reachable from public networks or CI without an ADR.
- [ ] Actor conditions are not treated as security controls; environments restricted to the default branch.

## Agent configuration
- [ ] Reviewers/planners remain read-only; `python3 scripts/sync-agents.py --check` passes.
