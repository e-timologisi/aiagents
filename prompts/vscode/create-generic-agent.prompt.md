---
name: create-generic-agent
description: 'Create a new agent or skill — you need a new role (agent) or recipe (skill), in a project or in the kit itself.'
argument-hint: 'role or skill to add'
agent: agent
---
<!-- GENERATED from prompts/11-create-generic-agent.md by scripts/build-prompts.py -->
Use the writing-for-agents skill. Create ${input:name} for: ${input:purpose}.

Agent: write agents/${input:name}.md with flat frontmatter (name = file name, description, role ${input:role}, optional model, mode,
extra_permissions) and body sections Read first / Workflow / Rules / Output / Handoff, under ~60 lines.
Reviewers/planners must stay read-only. Run `python3 scripts/sync-agents.py` and `--check`; commit source and generated files.

Skill: write .agents/skills/${input:name}/SKILL.md with frontmatter name = directory and a description that says WHEN to use it;
numbered steps, verification and docs to update.

If this belongs in the aiagents kit: put it under core/, repo-types/<type>/ or packs/<pack>/, use double-brace placeholders declared
in placeholders.yaml / type.yaml / pack.yaml, run `python3 scripts/check-kit.py`, add a CHANGELOG entry and bump VERSION.
