<!-- vscode: agent=security-reviewer; hint=PR URL -->
# 05 — Review a PR

**When to use:** a PR is ready for review (always for auth, data access, CI, infrastructure or domain rules).

**Placeholders:** `<PR_URL>`.

## Prompt

````text
@security-reviewer and @domain-reviewer: review <PR_URL> (read-only).

Record the head SHA you reviewed. Use docs/agents/security-review-checklist.md and the domain rules.
Findings format, per severity (Blocker / High / Medium / Low): `file:line — issue — fix`. Never quote secrets or personal data.
Also check: build/deploy gated on checks of the same run; reviewers remain read-only; docs updated; legal/domain
claims flagged "to be validated by an expert".
End with: "Safe to merge? yes/no — because …" and "Second review needed after fixes? yes/no" (yes for auth/sessions/crypto).
````
