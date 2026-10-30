# BookIt — project state

> Fictional example.

Last updated: 2026-03-06 by lead

## Phase
7 Dispatch

## Gates
| Gate | What the owner approves | Status |
|---|---|---|
| GATE 1 | Project brief | approved 2026-03-02 |
| GATE 2 | Decisions (ADRs) | approved 2026-03-03 |
| GATE 3 | Architecture plan | approved 2026-03-04 |
| GATE 4 | Backlog before issues are created | approved 2026-03-05 |

## Decisions log
| Date | Decision | Option chosen | Decided by | ADR |
|---|---|---|---|---|
| 2026-03-03 | Online payment in v1? | A — pay at the salon | Alex | 0001 |
| 2026-03-04 | One repo or several? | Single repo (`--standalone`) | Alex | — (recorded in brief) |

## Question queue
Asked one question at a time, top to bottom.
| # | Question | Blocking | Recommended / default | Status | Answer |
|---|---|---|---|---|---|
| 1 | Can stylists block time off? | no | Yes, "unavailable" slot | asked | — |
| 2 | Customer data retention period | no | 2 years, expert to confirm | default taken | 2 years (to be validated) |
| 3 | Brand colours for the booking page | no | Use salon logo colours | later | — |

## Tickets
| Issue | Repo | Agent | Branch | PR | Status | Review rounds |
|---|---|---|---|---|---|---|
| BK-001 | bookit | developer | feat/bk-001-book-slot | — | in progress | 0 |

## Risks
| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| No-shows | Lost revenue | Reminder e-mail; revisit deposits | Alex |

## Next actions
- developer — implement BK-001
- Alex — answer question 1

## Session log
- 2026-03-06 — Dispatched BK-001 to developer after GATE 4.
