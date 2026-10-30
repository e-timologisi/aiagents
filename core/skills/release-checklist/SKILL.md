---
name: release-checklist
description: "Walk the production release checklist: verify the default branch contains the reviewed commits, CI is green in the same run, staging was smoke-tested by a human, coupled releases are ordered, and rollback is ready. Use before any production release or when asked whether something is safe to release."
---

# Release checklist

The agent prepares and verifies; a human runs the release. Full checklist: `docs/agents/release-checklist.md`.

## Steps
1. **List what is being released**: PRs merged since the last release tag (`git log <last-tag>..origin/{{DEFAULT_BRANCH}} --oneline`, `gh pr list --state merged --base {{DEFAULT_BRANCH}}`).
2. **Reviewed commits reached the default branch** (lesson: a PR squash-merged at its first commit lost later fix commits and an unfixed version reached production). For each PR:
   - `gh pr view <n> --json headRefOid,mergeCommit,commits`
   - Compare trees: `git diff <pr-head-sha> <merge-commit-sha> -- <files of the PR>` must be empty (or only contain later, separately reviewed changes).
   - The reviewed SHA in the reviewer report equals the PR head SHA at merge.
3. **CI green in the same run** that builds the artifact: build/deploy jobs `needs:` lint/test/security. Link the run.
4. **Staging smoke test by a human**: the exact build/tag deployed to `{{STAGING_URL}}`; human confirms the changed flows.
5. **Coupled releases**: if repos depend on each other, release provider first (e.g. backend before frontend); confirm backward compatibility of migrations.
6. **Rollback ready**: previous tag known; migrations backward compatible; any downgrade that weakens security needs explicit owner approval.
7. **Docs**: README/CHANGELOG/ADR statuses updated.

## Output
```
Release candidate: <repo> <sha/tag>
PRs: <list> — main contains reviewed commits ✅/❌ (evidence)
CI run: <url> ✅/❌ (gated)
Staging smoke test (human): ✅/❌ <who, when>
Coupled with: <repo tags, order>
Rollback: <previous tag>
Verdict: ready | not ready — <blockers>
```
Never trigger the production release yourself.
