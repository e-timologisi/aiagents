# BookIt — requirements register

> Fictional example. Sources are invented.

Sources: "Salon wishlist" notes from Alex (2026-02-20), intake chat with Alex (2026-02-24), photo of the paper appointment book (2026-02-24). Chunks read: all.

## Requirements
| ID | Requirement (testable) | Type | Priority | Source | Confidence | Status | Tickets |
|---|---|---|---|---|---|---|---|
| R-001 | A customer can book one service with one stylist in a free slot; overlapping bookings for the same stylist are rejected | functional | must | Wishlist §1 | high | approved | BK-001 |
| R-002 | A customer can cancel a booking until 24 h before its start; later cancellations are refused with a message | functional | must | Intake chat 2026-02-24 | high | approved | |
| R-003 | The customer receives a reminder e-mail about 24 h before the appointment | functional | must | Wishlist §3 | medium | approved | |
| R-004 | The owner can add, edit and retire services (name, duration in 15-minute steps) and opening hours | functional | must | Paper book photo; intake chat | high | approved | |
| R-005 | Stylists see their own schedule for today and the next 7 days on a phone screen | functional | should | Intake chat 2026-02-24 | medium | approved | |
| R-006 | Pages load in under 2 s on a mid-range phone on 4G | non-functional | should | Assumption by lead, confirmed by Alex | low | proposed | |

## Constraints
| ID | Constraint | Kind (legal/technical/budget/time) | Source | Confidence | Validated by expert |
|---|---|---|---|---|---|
| C-001 | Fixed small monthly hosting budget | budget | Intake chat | high | n/a |
| C-002 | Live before the summer season | time | Wishlist §0 | high | n/a |
| C-003 | Customer data retention 2 years after last visit | legal | Intake chat | low | to be validated by a privacy expert |

## Gaps (questions for the owner)
| # | Question | Recommended answer | Blocks |
|---|---|---|---|
| 1 | Should a stylist be able to block personal time off? | Yes, as a simple "unavailable" slot | R-005 detail |
