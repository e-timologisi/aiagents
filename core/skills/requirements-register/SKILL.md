---
name: requirements-register
description: "Maintain docs/requirements-register.md - numbered requirements, constraints and risks with source references, confidence, status and links to tickets. Use whenever requirements are captured, changed, traced to tickets or questioned."
---

# Requirements register

Template: `docs/agents/templates/requirements-register.md.tmpl`.

## Rules
- IDs are permanent (`R-001`, `C-001`, `K-001`); never reuse or renumber. Superseded items keep their row with status `superseded by R-0xx`.
- Each row: ID, statement (one testable sentence), type, priority (must/should/could), source (doc§/page or `chat <date>`), confidence (high/medium/low), status (`proposed` → `confirmed` → `planned` → `done`, or `rejected`), ticket links.
- Only the owner moves an item to `confirmed`; record when.
- Contradictions and gaps have their own sections until resolved; resolutions cite the decision or ADR.
- Legal/compliance items carry "to be validated by {{DOMAIN_EXPERT}}" until validated.
- When a ticket is created, add its link; when merged and released, set `done`.

## Traceability check
Before GATE 4 (backlog), every `must` requirement maps to at least one ticket or is explicitly deferred.

## Questions about requirements
Open items (gaps, contradictions, unconfirmed `must` rows) are raised **one question at a time** (`docs/agents/interaction-standard.md`), most blocking first, each with a recommended answer; record the answer or the default in the row and in the question queue of `docs/project-state.md`.
