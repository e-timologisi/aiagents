# Worked-example snippets

Short filled-in examples (fictional "BookIt" appointment-booking app) showing the expected level of detail.

## Requirement rows
| ID | Requirement | Type | Priority | Source | Confidence | Status |
|---|---|---|---|---|---|---|
| R-001 | A customer can book a free 30-minute slot without an account | functional | must | chat 2026-01-10 | high | confirmed |
| R-002 | Staff see all bookings of their own shop only | functional | must | spec.pdf p.3 | high | confirmed |
| R-003 | Cancellation reminder e-mail 24 h before | functional | should | spec.pdf §4.2 | medium | proposed |

## Gap with recommended answer
| # | Question | Recommended answer | Blocks |
|---|---|---|---|
| 1 | Can customers pay online in v1? | No — pay in the shop; add payments later (less compliance work) | R-00x payments |

## Decision brief (options row)
| Option | What it means | Cost / effort | Risks | Reversible? |
|---|---|---|---|---|
| A: e-mail magic link | Customers log in with a link | S | e-mail delivery | yes |
| B: password + MFA | Classic login | M | more support | yes |

## Ticket (ready-for-agent)
- Goal: staff list today's bookings of their shop.
- Repo: bookit-api, then bookit-ui. Size: M. Depends on: #12 (shop membership).
- Acceptance: 1) list returns only own-shop bookings; 2) other shop → 404; 3) empty day → empty list.

## Status report line
| Ticket | What it does for users | Status | PR |
|---|---|---|---|
| #14 | Staff see today's bookings | in review (security, round 1) | bookit-api#20 |
