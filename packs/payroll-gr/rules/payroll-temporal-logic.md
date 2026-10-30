# Payroll temporal logic

- Never embed Greek payroll statutory figures in source code, migrations or tests about law.
- Resolve parameters by effective period from versioned records with half-open `[valid_from, valid_to)` ranges; enforce non-overlap in the database and in a test.
- Preserve parameter snapshots, calculation version and rounding policy on every run, so corrections are reproducible; corrections create new runs, snapshots are immutable.
- Money in decimal or integer minor units; rounding mode and points documented.
- Payroll is independent of billing/invoicing.
- Every legal interpretation is "to be validated by the accountant" until confirmed with a source and a worked example.
