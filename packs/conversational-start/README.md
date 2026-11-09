# Pack: conversational-start (beta)

For people who do not use a terminal. Everything is additive: without this pack nothing changes.

| Piece | Does |
|---|---|
| `commands/setup.md` | `/setup`: OS detection, one approval per install (winget on Windows, brew on macOS), installs the kit into the current folder |
| `commands/start-here.md` | `/start-here`: talk, choose a stack, hand over to `setup`, first save |
| `agents/setup.md` | The only role that may run installers; every shell command asks |
| `agents/lead.md` | The core `lead` plus one marked block "conversational start" (active only when the project has no `docs/project-state.md`) |
| skills | `stack-selection`, `machine-setup`, `save-work`, `explain-change` |
| `rules/` | `safety-model.md`, `setup-log-template.md` |

Install the two commands once on the machine: see `bootstrap/README.md`. Apply the pack to a project:

```sh
python3 scripts/apply-kit.py --stack web-nextjs --pack conversational-start --target <dir> --set PROJECT_NAME=... --set ORG=... --set DOCS_REPO=...
```

The pack also installs project-level `/start-here` (switches the session to `lead`) and keeps the kit's own `/setup`. Status: beta; the beginner trial (T1 to T8 of the plan) has not run yet.
