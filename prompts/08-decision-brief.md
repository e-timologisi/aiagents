<!-- vscode: agent=architect; hint=the question to decide -->
# 08 — Decision brief → ADR

**When to use:** an architectural, infrastructure, security or legal question needs an owner decision.

**Placeholders:** `<QUESTION>`.

## Prompt

````text
@architect decision brief: <QUESTION>

Context and constraints (link ADRs, rules, service map). 2–4 options with pros, cons, risks, cost and reversibility.
Your recommendation and why. Then ask me ONE question at a time (start with the choice itself: recommended option + options with one-line consequences); questions only the owner (or an expert) can answer, marked "to be validated by an expert"
where legal/domain. Conflicts with existing ADRs. After I choose, draft the ADR from docs/adr/template.md
(status Proposed) and list follow-up tickets. Do not decide for me.
````
