---
name: add-endpoint
description: Add or change an HTTP endpoint in {{REPO_NAME}} contract-first (contract, handler, authorization, tests, docs). Use when a ticket adds, changes or removes an API route.
---

# add-endpoint

Follow in order. Stop and ask if the auth scheme, a permission or a domain rule is undecided; do not invent one.

1. **Contract first.** Edit `{{CONTRACT_PATH}}`: path under `{{API_PREFIX}}/...`, `operationId`, request/response schemas, every status code, errors as `application/problem+json`. Money as decimal string or integer minor units, never a JSON number. No owner/tenant id input trusted on its own. Bump `info.version` (minor if additive, major if breaking). Lint the contract.
2. **Handler.** Register the route; the handler only parses, authorizes and maps errors; logic lives in `internal/<domain>/`. A route/contract sync test fails until both match.
3. **Scope.** Derive the owner/tenant from the authenticated session; scope every query explicitly.
4. **Authorization.** Check the caller's permission for the action; deny by default. New permissions need product sign-off.
5. **Tests.**
   - Table-driven unit tests: success, validation errors, each denied role, unknown role.
   - Integration test on a throwaway database: denial for another user/tenant; fail-closed when context is missing.
   - Schema change? Use the `add-migration` skill.
6. **Logs/errors** carry no secrets or personal data.
7. **Verify:** `{{LINT_CMD}}`, `{{TEST_CMD}}`, `{{INTEGRATION_CMD}}`.
8. **Docs:** README endpoints, consumers notified (issue in the consuming repo), ADR if a convention changes, GLOSSARY for new terms. Request `security-reviewer` for anything touching auth or data access.
