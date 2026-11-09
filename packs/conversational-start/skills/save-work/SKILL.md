---
name: save-work
description: Save the person's work with plain-language git so they never type git; checkpoint before risky steps and undo on request. Use after each finished step.
---
# Save work

The person never types git. You do, locally, and explain in one sentence.

- First time: `git init`, create `.gitignore` entries for `.env`, `node_modules`, build output and `.aiagents/kit.local`; scan the staged files for secrets before the first commit (refuse and explain if any).
- Save = `git add` + `git commit -m "<plain sentence of what changed>"`. One branch per task when the person works with others; otherwise stay on the main branch.
- Checkpoint = a commit plus a tag `checkpoint-<n>` before every risky step (installs, large edits, dependency changes). Tell the person its name.
- "Undo the last change": show what the checkpoint contains, ask yes/no, then restore the files from that tag with a new commit; never use history-rewriting or force commands.
- Hosted copy (GitHub or similar): only after plain approval; the person creates the account and signs in; you never create repos, push or handle tokens without that approval and never paste a token.
- Report: "Saved: <message>. You can go back to it with: <what to say>".
