---
name: status-report
description: "Write a plain-language status report for a non-technical owner after each step or weekly - what was done, what is waiting for them, progress table, risks, next steps. Use at the end of every lead step or when the owner asks 'where are we?'."
---

# Status report

Template: `docs/agents/templates/status-report.md.tmpl`. Keep it under one screen.

## Rules
- Start with **the one next decision** you need from the owner (question, recommended answer, 2–4 options with consequences), then a short **queue** of later decisions (one line each), then progress. One question at a time: never a list of questions to answer at once.
- Plain words: "the login page is ready for your test on staging" instead of jargon. Explain any unavoidable term in brackets.
- Tables: ticket, what it does for users, status (`waiting`, `in progress`, `in review`, `ready to merge`, `merged`, `released`), PR link.
- Risks in one line each with what reduces them.
- Never include secrets, personal data or internal hostnames.
- Save to `docs/status/<yyyy-mm-dd>.md` if the owner wants a history; always update `docs/project-state.md`.
