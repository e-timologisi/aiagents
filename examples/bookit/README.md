# Example: BookIt (fictional)

**Everything in this folder is invented.** BookIt is a made-up booking app for a small hair salon; "Alex" is a made-up owner. There is no real company, customer, person or system behind it. The files show what the kit's `lead` agent and skills produce in the first days of a project, so you can see the shape before you start your own.

| File | Produced by |
|---|---|
| `docs/project-brief.md` | `lead` with the `project-intake` skill (prompt `prompts/00-start-here.md`), approved at GATE 1 |
| `docs/requirements-register.md` | `document-ingest` + `requirements-register` skills |
| `docs/project-state.md` | `project-state` skill (kept up to date by `lead`) |
| `docs/decisions/DB-001-online-payments.md` | `lead`, prompt `prompts/08-decision-brief.md` |
| `docs/adr/0001-pay-at-the-salon-in-v1.md` | `domain-modeling` skill (ADR format), after GATE 2 |
| `docs/tickets/BK-001.md` | `backlog-planning` + `task-intake` skills (prompt `prompts/02-write-ticket.md`), approved at GATE 4 |

In a real project these live in the docs repo (or `docs/` of a single repo) and tickets are GitHub issues; here the ticket is a Markdown file so the example is self-contained.
