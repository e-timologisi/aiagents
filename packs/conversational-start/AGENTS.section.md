## Conversational start (pack: conversational-start, beta)

The person may not use a terminal. Say what you did in one sentence after each action; use plain words and explain a term the first time. Only the `setup` agent runs installers or system commands, one separate approval per install; never ask for or display passwords or secrets. Save work through the `save-work` skill (local git by default; a hosted copy only after approval). AI output must be checked by a human before real users, money or personal data are involved. Rules: `docs/rules/safety-model.md`.
