<!-- vscode: agent=architect; hint=issue URL -->
# 03 — Plan a feature

**When to use:** a ready ticket needs a per-repo plan (and maybe an ADR).

**Placeholders:** `<ISSUE_URL>`.

## Prompt

````text
@architect plan <ISSUE_URL>.

Use the cross-repo-feature skill. Route with the service map; list ADR conflicts with the exact clause.
If a decision is needed, give options, pros/cons and a recommendation and stop for my answer.
Plan in change order (decision → contract/provider → consumers → jobs → docs) with files, tests and the PR each step produces,
then propose child issues "Part of <org>/<repo>#<n>". Note coupled releases and their order. No code.
````
