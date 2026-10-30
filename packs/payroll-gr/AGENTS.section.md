## Payroll (pack: payroll-gr)

Keep payroll calculations independent of billing and invoicing. Do not hardcode tax, EFKA or statutory amounts; use versioned parameter records with valid_from/valid_to and no overlapping windows. Historical payroll must be reproducible (formulas, rounding policy, rules version, inputs) via immutable calculation snapshots. Never use float for money. Mock government endpoints (ERGANI, AADE/myDATA). Incorrect statutory payroll is a release blocker; legal interpretations are "to be validated by the accountant".

This pack is not legal, tax or accounting advice; every rule is to be validated by a qualified expert.
