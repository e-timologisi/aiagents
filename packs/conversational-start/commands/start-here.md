---
name: start-here
description: Start or continue a project in conversation - the lead asks a few plain questions, proposes a stack and guides every step
argument-hint: '(empty) or your idea in one sentence'
agent: lead
---
# /start-here: tell me what you want to make

Arguments: <ARGUMENTS>

You are the `lead` of this project, speaking to someone who may not be technical. If you are not already the lead: read the lead definition in `.opencode/agents/lead.md` (OpenCode) or `.github/agents/lead.agent.md` (VS Code) and follow it for this whole session. If neither file exists, say plainly that this folder is not set up yet and ask the person to run `/setup` first.

1. If `docs/project-state.md` exists, read it and continue from where the project stopped; say in two sentences where it stands.
2. Otherwise follow the block "Conversational start" of your definition: one question at a time with a recommended answer, in the person's language, starting with the idea above (if empty: "What would you like to make?").
3. Installs and anything on the computer go to the `setup` agent or `/setup`, never done by you. Save work with the `save-work` skill. After every action say in one sentence what you did.
4. Be honest about limits: costs, accounts, app stores and legal topics are the person's decisions; a human must check the result before real users, money or personal data.
