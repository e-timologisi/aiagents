---
name: write-ticket
description: 'Write a ticket — you have an idea or request that is not yet a ready issue.'
argument-hint: 'describe the idea in plain words'
agent: agent
---
<!-- GENERATED from prompts/02-write-ticket.md by scripts/build-prompts.py -->
Use the task-intake skill: ${input:idea}

Read the service map, glossary and relevant ADRs first. Draft the ticket with every field of the feature (or bug/decision)
template, numbered testable acceptance criteria, out of scope, data/contract impact, domain/legal impact
("to be validated by an expert" where applicable), docs to update and risks.
Then ask me the open decisions ONE question at a time (most blocking first), each with your recommended answer and 2–4 options with consequences; adapt to my answers. Do not create the issue until I confirm.
Propose labels (needs-info / ready-for-agent / ready-for-human + area:*).
