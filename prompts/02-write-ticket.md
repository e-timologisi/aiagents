<!-- vscode: agent=agent; hint=describe the idea in plain words -->
# 02 — Write a ticket

**When to use:** you have an idea or request that is not yet a ready issue.

**Placeholders:** `<IDEA>`.

## Prompt

````text
Use the task-intake skill: <IDEA>

Read the service map, glossary and relevant ADRs first. Draft the ticket with every field of the feature (or bug/decision)
template, numbered testable acceptance criteria, out of scope, data/contract impact, domain/legal impact
("to be validated by an expert" where applicable), docs to update and risks.
Then ask me the open decisions ONE question at a time (most blocking first), each with your recommended answer and 2–4 options with consequences; adapt to my answers. Do not create the issue until I confirm.
Propose labels (needs-info / ready-for-agent / ready-for-human + area:*).
````
