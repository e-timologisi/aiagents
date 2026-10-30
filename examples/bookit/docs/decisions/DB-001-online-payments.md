# Decision brief: Take payment online in version 1?

Asked by: lead   Date: 2026-03-02   Decides: owner (Alex)   Blocks: backlog (GATE 4)

> Fictional example.

## In plain words
Customers could pay when they book, or pay at the salon as today. Paying online reduces no-shows but adds cost, setup work and more rules to follow.

## Options
| Option | What it means | Cost / effort | Risks | Reversible? |
|---|---|---|---|---|
| A | Pay at the salon (as today) | S | No-shows stay as they are | Yes — add payments later |
| B | Full payment online via a payment provider | L, plus per-transaction fees | Refunds, provider setup, more data to protect | Hard once customers rely on it |
| C | Small deposit online | M, plus fees | Same as B, smaller amounts | Medium |

## Recommendation
A for version 1: it meets the launch date and budget. Revisit C if no-shows exceed an agreed level after three months.

## Questions for the owner
1. Is pay-at-the-salon acceptable for the first season?

## Legal / domain points
Any refund or cancellation-fee policy is to be validated by an expert before payments are added.

## After the decision
ADR 0001 drafted from `docs/adr/template.md`; follow-up: none for v1; "revisit deposits" added to the risks.
