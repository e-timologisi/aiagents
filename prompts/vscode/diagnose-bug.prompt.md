---
name: diagnose-bug
description: 'Diagnose a bug — something is broken, throwing, failing or slow.'
argument-hint: 'symptom, environment, version'
agent: agent
---
<!-- GENERATED from prompts/10-diagnose-bug.md by scripts/build-prompts.py -->
Use the diagnosing-bugs skill: ${input:symptom} in ${input:environment} at ${input:version}.

Reproduce locally with synthetic data first (never against production data). Form hypotheses, test them one at a time,
find the root cause. Write a failing regression test, fix, run all checks, open a PR referencing the bug issue.
Never read or print secret values or personal data from logs; redact. If production access is needed, ask me with the
exact read-only command.
