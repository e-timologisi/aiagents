---
name: explain-change
description: Explain a change, review result or failure in plain language for a non-technical owner - what changed, what could go wrong for them, what to check. Use for reports to the person.
---
# Explain a change

Write for someone who does not read code. Keep it short.

1. **What changed**: two or three sentences, no file lists unless asked.
2. **What it means for you**: what you can now see or do; how to see it (`run_cmd` of the stack, or the page to open).
3. **What could go wrong**: honest risks in everyday words (data lost, wrong amounts shown, public exposure, cost). Say which checks ran (tests, security review) and which did not; never claim an unchecked result.
4. **What I need from you**: one yes/no or one thing to look at.
5. Terms: explain a technical word the first time, or avoid it.

Reviews (`security-reviewer`, `test-engineer`) keep their technical reports; you translate them with this skill. Reminder when real users, money or personal data come near: a human professional must check before going live.
