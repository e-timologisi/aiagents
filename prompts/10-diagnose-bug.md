<!-- vscode: agent=agent; hint=symptom, environment, version -->
# 10 — Diagnose a bug

**When to use:** something is broken, throwing, failing or slow.

**Placeholders:** `<SYMPTOM>`, `<ENVIRONMENT>`, `<VERSION>`.

## Prompt

````text
Use the diagnosing-bugs skill: <SYMPTOM> in <ENVIRONMENT> at <VERSION>.

Reproduce locally with synthetic data first (never against production data). Form hypotheses, test them one at a time,
find the root cause. Write a failing regression test, fix, run all checks, open a PR referencing the bug issue.
Never read or print secret values or personal data from logs; redact. If production access is needed, ask me with the
exact read-only command.
````
