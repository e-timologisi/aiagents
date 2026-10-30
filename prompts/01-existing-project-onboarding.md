<!-- vscode: agent=lead; hint=repo paths to onboard -->
# 01 — Existing project onboarding

**When to use:** an existing repo (or several) should adopt the agent workflow without touching its code.

**Placeholders:** `<REPO_PATHS>`, `<KIT_PATH>` (local clone of aiagents).

## Prompt

````text
@lead onboard the existing project at <REPO_PATHS>.

1. Explorer first: launch one explorer per repo (codebase-discovery skill), QUICK OVERVIEW only; show me the summaries
   and the estimated effort before any deep dive. Every claim needs evidence (path:line) and a tag
   (verified | read-from-code | inferred). Secrets: location only, never values. No commands with side effects;
   running existing tests only if I approve.
2. Dossiers: after my go, deep dives produce docs/discovery/<repo>.md drafts (not committed yet). Merge them and show me
   only the TOP 3 blocking questions; ask them ONE at a time with a recommended answer and options (the rest go to the
   question queue with defaults). Branch claims must name branch, base branch and commit hashes.
3. I confirm the unknowns, one question at a time. Then continue your pipeline: project brief (GATE 1), decisions (GATE 2),
   architecture/kit plan (GATE 3: repo type and packs per repo, --set values, files to ADD; existing files are never
   overwritten), backlog (GATE 4).
4. After GATE 3 apply the kit: python3 <KIT_PATH>/scripts/apply-kit.py ... --dry-run, show the report, then for real,
   run python3 scripts/sync-agents.py --check, commit on branch chore/aiagents and open a PR per repo (with the
   approved dossier). Never change application code or existing CI.
````
