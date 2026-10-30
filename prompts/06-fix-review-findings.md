<!-- vscode: agent=developer; hint=PR URL and findings -->
# 06 — Fix review findings

**When to use:** a reviewer reported findings on a PR.

**Placeholders:** `<PR_URL>`, `<FINDINGS>` (paste or link).

## Prompt

````text
Fix the review findings on <PR_URL>: <FINDINGS>

- Work on the PR's own branch; one commit per finding (or a clearly grouped commit), with a test for each fix where possible.
- Run lint/test/integration; push.
- VERIFY all fix commits reached the PR: `gh pr view <n> --json headRefOid,commits` must list them and the head SHA
  must equal your local HEAD. If the PR was already merged, STOP: compare `git diff <pr-head> origin/<default-branch> -- <files>`
  and open a new PR for anything missing (lesson: a squash-merge at the first commit once dropped later fixes and
  an unfixed version reached production).
- Reply to each finding with the commit SHA that fixes it; request re-review of the new head SHA.
- Never merge yourself.
````
