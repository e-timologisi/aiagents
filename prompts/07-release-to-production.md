<!-- vscode: agent=agent; hint=repos to release -->
# 07 — Release to production (preparation)

**When to use:** before the owner presses the release button.

**Placeholders:** `<REPOS>`.

## Prompt

````text
Use the release-checklist skill for <REPOS>. Do not trigger any release.

For every repo:
1. List PRs merged since the last release tag.
2. Prove the default branch contains the reviewed commits: for each PR compare the reviewed head SHA with the merge,
   `git diff <pr-head-sha> <merge-commit> -- <PR files>` must be empty. Report evidence.
3. Link the CI run that built the artifact; confirm build/deploy jobs needed lint/test/security in that run.
4. Ask me to confirm the human staging smoke test of that exact SHA/tag.
5. Coupled releases: give the order (provider before consumers) and backward-compatibility notes for migrations.
6. Rollback tag, accepted risks (e.g. no required-reviewer protection on this plan), secrets present by NAME only.
End with "ready / not ready" per repo and the blockers.
````
