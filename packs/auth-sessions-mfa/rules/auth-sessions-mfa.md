# Authentication, sessions and MFA — design checklist

Decide each item in an ADR; check each in review. Values in brackets are starting points, not mandates.

## Passwords
- [ ] argon2id with documented parameters; cap concurrent hashing (memory) and set container memory limits accordingly.
- [ ] Minimum length, breached-password check optional; no composition rules that reduce entropy.
- [ ] Constant-time comparison; same response and timing for unknown users (no account enumeration).

## Tokens (verification, password reset, invites)
- [ ] Random (≥ 128 bits), stored **hashed** (e.g. SHA-256), single-use, short expiry (reset ≈ 1 h).
- [ ] Verification requires proof of the password or binds to the original sign-up, so a squatter cannot keep an unverified account.
- [ ] Password change/reset revokes other sessions.

## Sessions
- [ ] Server-side sessions in the database (revocable); session id stored hashed.
- [ ] Cookie `{{SESSION_COOKIE}}`: `HttpOnly`, `Secure`, `SameSite=Lax` (or Strict), `Path=/`, no `Domain` (the `__Host-` prefix enforces this).
- [ ] Absolute and idle lifetimes ("remember me" vs browser session) documented.
- [ ] Expired rows cleaned up by a job.

## MFA (TOTP)
- [ ] RFC 6238 parameters documented (digits, step, tolerance); replay protection (last used step).
- [ ] TOTP secret encrypted at rest (AEAD) with a key from environment secrets; key fingerprint checked on deploy; key change requires explicit approval and a rotation plan.
- [ ] Limited "MFA pending" session with short lifetime; only verify/logout/me allowed.
- [ ] Which roles require MFA; enforcement server-side before any protected endpoint ships (release gate).
- [ ] Recovery codes: ~10, shown once, stored hashed, regenerable; never in storage, URLs, logs or analytics on the client.
- [ ] Device reset requires password + second factor or recovery code; old device active until the new one is confirmed.

## Abuse limits
- [ ] Rate limits and lockouts stored in the **database or shared store**, not per-process memory (multiple instances, restarts).
- [ ] Per-user and per-session failure limits with `429` + `Retry-After`; document residual risks (e.g. attacker with a password can block MFA).

## Network and browser
- [ ] Client IP from forwarding headers only via explicitly trusted proxy CIDRs.
- [ ] CSRF: SameSite cookies plus `Origin` check on state-changing requests (or tokens).
- [ ] Redirect targets after login validated against an allowlist of relative paths (no open redirects).
- [ ] Browser talks to a same-origin proxy that forwards `Set-Cookie`; CORS limited to exact origins.
- [ ] Security headers: CSP (nonce-based), HSTS, `X-Frame-Options: DENY`, `Referrer-Policy`, `X-Content-Type-Options`.

## Secrets and operations
- [ ] Mail/OAuth/encryption secrets are CI environment secrets written by the deploy job to root-only files; never printed by agents or scripts (a credentials check once echoed OAuth secrets — check names only).
- [ ] Rolling back below an auth migration that weakens security needs explicit owner approval.
- [ ] Independent security review before go-live.
