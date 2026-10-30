<!-- vscode: agent=agent; hint=role or skill to add -->
# 11 — Create a new agent or skill

**When to use:** you need a new role (agent) or recipe (skill), in a project or in the kit itself.

**Placeholders:** `<NAME>`, `<PURPOSE>`, `<ROLE>` (implementer | reviewer | planner | inspector | docs).

## Prompt

````text
Use the writing-for-agents skill. Create <NAME> for: <PURPOSE>.

Agent: write agents/<NAME>.md with flat frontmatter (name = file name, description, role <ROLE>, optional model, mode,
extra_permissions) and body sections Read first / Workflow / Rules / Output / Handoff, under ~60 lines.
Reviewers/planners must stay read-only. Run `python3 scripts/sync-agents.py` and `--check`; commit source and generated files.

Skill: write .agents/skills/<NAME>/SKILL.md with frontmatter name = directory and a description that says WHEN to use it;
numbered steps, verification and docs to update.

If this belongs in the aiagents kit: put it under core/, repo-types/<type>/ or packs/<pack>/, use double-brace placeholders declared
in placeholders.yaml / type.yaml / pack.yaml, run `python3 scripts/check-kit.py`, add a CHANGELOG entry and bump VERSION.
````
