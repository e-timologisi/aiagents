---
name: payroll-rule
description: Implement or change a Greek payroll calculation rule (tax, EFKA contributions, allowances) with versioned statutory parameters, exact money arithmetic and reproducible snapshots. Use when a ticket touches payroll calculations or statutory parameters.
---

# payroll-rule

Incorrect statutory payroll is a release blocker. Rules: `docs/rules/payroll-temporal-logic.md`.

1. **Get the rule validated first.** The ticket must cite the source (law/circular) and an accountant-approved worked example. If either is missing or ambiguous, stop and ask; never infer legal obligations.
2. **No hardcoded statutory figures.** Rates, ceilings, thresholds and brackets live in versioned parameter records (PostgreSQL tables via the `add-migration` skill) with `valid_from` / `valid_to` (half-open `[valid_from, valid_to)`; `valid_to` NULL = open). Enforce non-overlap in the database (exclusion constraint) and in a test. Resolve parameters by the payroll period's effective date. Parameter values are data loaded by an approved process, not literals in Go or SQL migrations.
3. **Money.** Never `float32/float64`. Use integer minor units (`int64` cents) or a decimal type; state the rounding policy (mode and step) explicitly and apply it at the documented points only.
4. **Pure calculation.** Put the calculation in `{{PAYROLL_PACKAGE}}/` (create if absent) as a pure function of inputs + resolved parameters; no I/O, no clock, independent of billing/invoicing.
5. **Reproducible.** Each run stores an immutable snapshot: inputs, parameter record IDs/values, rules/calculation version, rounding policy, outputs. Corrections create a new run; snapshots are never updated in place.
6. **Tests.** Table-driven (use the `payroll-unit-test-generator` skill): boundaries at every threshold and validity date, zero/negative, part-time, rounding, determinism; accountant-approved fixtures as golden cases. Integration test for parameter resolution and overlap rejection.
7. **Review.** Request `domain-reviewer` (and `security-reviewer` if tenancy is touched). Mark legal interpretations "to be validated by accountant" in the PR.
8. **Docs.** GLOSSARY terms in `{{DOCS_REPO}}`, ADR for new calculation/rounding conventions, issue updated.

Not legal, tax or accounting advice: rules and contracts must be validated by a qualified expert.
