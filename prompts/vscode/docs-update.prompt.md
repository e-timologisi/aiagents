---
name: docs-update
description: 'Docs update — behaviour, commands, setup, decisions or terms changed and docs must follow.'
argument-hint: 'what changed'
agent: quick-tasks
---
<!-- GENERATED from prompts/09-docs-update.md by scripts/build-prompts.py -->
Apply "Definition of done: documentation" from AGENTS.md for ${input:change}.
Check and update as needed: README/CONTRIBUTING (setup, commands, env var NAMES), service map, ADR status or
implementation notes, GLOSSARY terms, release checklist, related issue comment. Markdown only; open a PR.
Report which docs were updated, or why none were needed. No secrets, server details or personal data.
