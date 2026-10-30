# 0001 — Pay at the salon in version 1

Status: Accepted (2026-03-03)

> Fictional example.

## In plain words
Version 1 of BookIt does not take money online. Customers book online and pay at the salon, as they do today.

## Context
Launch must happen before the summer season (C-002) on a small budget (C-001). No-shows are a known risk. Decision brief: `docs/decisions/DB-001-online-payments.md`.

## Options considered
1. Pay at the salon — no cost, no new rules; no-shows unchanged.
2. Full online payment — fewer no-shows; provider fees, refunds, more personal data.
3. Online deposit — middle ground; same setup work as option 2.

Recommendation: option 1.

## Decision
- No payment provider, card data or payment status is stored or handled by BookIt v1.
- Booking and cancellation flows must not assume a payment step.

## Consequences
Faster launch and less data to protect. No-shows are handled by reminders only. Accepted risk: revenue loss from no-shows; revisit after three months of data.

## Open questions
Refund/cancellation-fee policy if deposits are added later (to be validated by an expert).
