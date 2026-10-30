---
name: backlog-planning
description: "Turn the approved brief, decisions and architecture into epics and ready tickets - vertical slices, dependency graph, parallelisable sets, S/M/L estimates, definitions of ready and done. Use before creating issues for a project or a large feature."
---

# Backlog planning

## Steps
1. **Epics**: one per user-visible capability (plus one "foundation" epic: repos, CI, auth skeleton). Link requirements.
2. **Slice vertically**: each ticket delivers something testable end to end (contract → backend → UI) or is a clearly bounded layer when the change order requires it (API ticket before UI ticket). Avoid "do all the database" tickets.
3. **Ticket fields** via `task-intake` (definition of ready in `docs/agents/ticket-standard.md`): goal, repo, acceptance criteria, out of scope, data/contract impact, domain impact, docs to update.
4. **Estimate** S (≤ half day agent work, one PR), M (one PR, several files/tests), L (split it).
5. **Dependencies**: list `blocked by`; draw the graph (mermaid allowed). Contract/API before consumers; decisions before dependent work.
6. **Parallel sets**: group tickets with no mutual dependency and different files/repos; mark the critical path.
7. **Definition of done**: checks green, reviews done, docs updated, issue commented, merged by a human.
8. Show the backlog as a table to the owner (epic, ticket, repo, size, depends on, parallel set) → GATE 4. Create issues only after approval (`gh issue create`, sub-issues or `Part of` lines).

## Asking the owner
GATE 4 is one question ("Approve this backlog? yes / changes"). Questions about scope, order or splitting are asked **one question at a time** with a recommended answer and options; never a list of open points.
