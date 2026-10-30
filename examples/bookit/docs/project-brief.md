# BookIt — project brief

Status: approved by owner on 2026-03-02 (GATE 1)

> Fictional example. BookIt and Alex are invented.

## In one paragraph
BookIt lets customers of a single small hair salon book, move and cancel appointments online, so the owner, Alex, spends less time on the phone. Version 1 is a simple web app for one salon with three stylists.

## Users and roles
| Who | What they need | How many |
|---|---|---|
| Customer | See free slots, book, cancel, get a reminder | ~400 per month |
| Stylist | See today's and this week's appointments | 3 |
| Owner (Alex) | Set opening hours, services and stylists; see all bookings | 1 |

## Version 1 must do
1. Customers book a service with a stylist in a free slot (R-001).
2. Customers cancel up to 24 hours before (R-002).
3. Reminder e-mail the day before (R-003).
4. Owner manages services, durations and opening hours (R-004).
5. Stylists see their schedule on a phone (R-005).

## Not in version 1
- Online payment (see ADR 0001), multiple salons, loyalty points, SMS.

## Data
Customer name, e-mail and phone; booking history. Keep for 2 years after the last visit (to be validated by a privacy expert).

## Constraints
Hosting budget under a small fixed monthly amount; launch before the summer season; must work on phones (C-001, C-002).

## Success looks like
Half of all bookings are made online within three months; phone time drops noticeably.

## Open decisions
| # | Question | Recommended | Decision brief |
|---|---|---|---|
| 1 | Take payment online in v1? | No, pay at the salon | `decisions/DB-001-online-payments.md` (decided) |

## Risks
| Risk | Impact | Mitigation |
|---|---|---|
| No-shows increase with easy online booking | Lost revenue | Reminder e-mail; revisit deposits after v1 |
