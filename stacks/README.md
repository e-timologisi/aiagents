# Stack profiles

A stack is a folder `stacks/<id>/` with a `stack.yaml`. It sits **next to** `repo-types/` and replaces nothing: `--type` keeps working.

```sh
python3 scripts/apply-kit.py --list-stacks
python3 scripts/apply-kit.py --stack-info web-nextjs --os windows     # read-only JSON for the setup agent
python3 scripts/apply-kit.py --stack api-go --target <dir> --set PROJECT_NAME=Acme --set ORG=acme --set DOCS_REPO=acme-docs
```

`--stack` and `--type` are mutually exclusive. `--stack` also records `stack` in `.aiagents-manifest.json` (manifests made with `--type` are unchanged).

## Two kinds
- **Alias** (`repo_type: <name>`): points to an existing repo type; its templates, agents, skills and defaults are used as they are. `web-nextjs` → `frontend-nextjs`, `api-go` → `backend-go`, `docs-hub`, `serverless-sam`.
- **Own** (no `repo_type`): the folder carries `AGENTS.md.tmpl`, `CONTRIBUTING.md.tmpl`, `README.md.tmpl`, `pull_request_template.additions.md` and `defaults:` (with `STACK`); optional `agents/` and `skills/` overlays use the same order as repo types (core, stack, packs).

## stack.yaml
| Key | Meaning |
|---|---|
| `id` | folder name |
| `status` | `stable` (default) or `beta` |
| `category` | web, api, mobile, desktop, data, docs |
| `title`, `plain` | plain-language name and one-line explanation |
| `fits`, `not_for` | matched against the interview answers by `stack-selection` |
| `os_support` | `windows`, `macos`, `linux`: `yes`, `no` or `untested` |
| `needs_mac` | true when a build needs a Mac (iOS) |
| `toolchain` | list of `id`, `check` (version command), `min`, `install: {windows, macos}`, `why`, `admin` (true when the installer may ask for administrator rights), optional `optional: true` |
| `accounts_needed` | accounts the human must create (may be `[]`) |
| `defaults`, `descriptions` | placeholder defaults (own stacks) |
| `recommended_packs` | existing pack names |
| `run_cmd` | what "show me it works" runs |
| `risks` | limits told to the person before they choose |

`check-kit.py` validates the schema, that every toolchain item has an install command for each OS marked `yes` (windows, macos), and the forbidden-string scan.

## Add a stack
Copy a folder, fill `stack.yaml`, run `python3 scripts/check-kit.py`. No script change is needed.
