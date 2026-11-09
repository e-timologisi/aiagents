---
name: stack-selection
description: Decide the technology stack with a non-technical person in a short interview, one question at a time. Use when a project starts and no stack is chosen.
---
# Stack selection

Ask ONE question at a time, in the person's language, in plain words, each with a recommended answer and 2-4 options. Never use "repo type", "ADR" or "CLI" without explaining them.

## Interview (at most 8 questions, skip what is already known)
1. What do you want to make? (one sentence)
2. Who will use it? (only you, your team, the public)
3. Where: in a browser, on a phone, as a background service, or as a data analysis?
4. Do you already use a tool, language or hosting? (default: no)
5. Does it handle money, personal data or health data? (if yes: say a professional must review before real use)
6. Budget and hosting: free preview first, or paid hosting from the start?
7. Which computer do you use? (Windows or Mac; matters for phone apps)

## Choose
1. List the stacks: `python3 scripts/apply-kit.py --list-stacks` (use `python` on Windows) and read `python3 scripts/apply-kit.py --stack-info <id> --os <windows|macos>`.
2. Score each by `fits` and `not_for` against the answers. Drop any stack whose `os_support` for the person's computer is not `yes`, and any `mobile` stack for iOS on Windows (`needs_mac`).
3. Propose the best match plus ONE alternative: say in plain words what it is, what it costs or needs (`accounts_needed`), and its limits (`risks`, beta status). Default when unsure: `web-nextjs` (needs no accounts).
4. Several parts (website plus API) are separate stacks; start with one and say so.
5. On a "yes": write `docs/adr/0001-stack.md` (decision, alternatives, consequences) and `docs/project-state.md` (stack, OS, next step). If something is uncertain (legal, privacy, tax), note it for a professional; never invent.

Beta stacks are offered only when the person asks for them or nothing else fits, with the beta warning.
