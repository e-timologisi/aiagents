---
name: project-intake
description: "Discovery interview for a new idea in chat - one question at a time, each with a recommended answer and options, adapting the next question to the answer. Use when a project or large feature starts from a conversation rather than documents or code."
---

# Project intake (chat)

Follow `docs/agents/interaction-standard.md`: **one question at a time**, never the whole interview at once.

## The loop
```
queue = question bank below, ordered by blocking-ness, minus anything already known
repeat:
  1. drop questions answered by documents, repo or earlier answers (state the inference instead)
  2. ask the FIRST question in the queue (question tool if available), with recommended answer + 2–4 options + other
  3. record the answer (or the default for "skip" / "later" / "recommend for me") in the requirements register
  4. adapt: add follow-ups the answer raised, remove questions it made irrelevant, re-order
  5. every 3–5 answers: short running summary + "Is this right?"
until no blocking question remains; nice-to-have questions get stated defaults
"go with your suggestions" → take the recommended answers for the rest of the current topic, list them, move on
```

## Question bank (most blocking first)
1. **Purpose and users** — what problem, for whom, who signs in (blocks everything).
2. **Scope v1** — the 3–5 must-haves; what waits; how we know it works.
3. **Data** — personal/sensitive data, several customers sharing the app (separation), existing data to import.
4. **Security/compliance** — sign-in method, MFA, regulations, audit (legal points: "to be validated by {{DOMAIN_EXPERT}}").
5. **Integrations** — payments, e-mail/SMS, partner or government APIs (contract documents?).
6. **Hosting/cost** — monthly budget, preferred provider, data location, uptime expectations.
7. **Team** — who reviews and merges, who releases, domain expert, timeline.
8. Nice-to-have — branding, languages beyond the first, analytics (default and move on).

## Example turns
```
Lead: Who is the app for, mainly?
      Recommended: A — matches what you described.
        A) Salon staff managing bookings — staff-facing tool first
        B) Customers booking online — customer-facing site first
        C) Both equally — larger first version
        Other: tell me
Owner: B, but staff must see the bookings
Lead: Got it: customers book, staff view. Do customers need an account?
      Recommended: A — faster to build, fewer personal-data duties.
        A) No account, just name and phone
        B) Account with password — they can see past bookings
Owner: go with your suggestions
Lead: Taking defaults for "users": no customer account; staff log in with e-mail link. Next topic — what must v1 do? …
```

## After the interview
- `docs/requirements-register.md` (`requirements-register`) with source `chat <date>` and confidence.
- `docs/project-brief.md` from `docs/agents/templates/project-brief.md.tmpl`.
- Remaining open decisions go into the question queue of `docs/project-state.md`.
