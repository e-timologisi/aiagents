# Contributing

Thank you for your interest. This kit has a single maintainer ([@e-timologisi](https://github.com/e-timologisi)).

## How contributions work

- **Issues, discussions and pull requests from forks are welcome as suggestions.** The maintainer decides what is merged; there is no guarantee that a suggestion or pull request will be accepted, and it may be reworked or reimplemented instead.
- Questions and ideas: use [Discussions](https://github.com/e-timologisi/aiagents/discussions). Bugs and concrete suggestions: use the issue forms.
- Security problems: never in public; see [SECURITY.md](SECURITY.md).
- Be kind; see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- No CLA or DCO sign-off is required. By contributing you agree your contribution is licensed under the MIT License of this repository.
- **Third-party material**: only add content from other projects if its license is compatible with MIT, and in the same PR add its full license text and a provenance row to `THIRD-PARTY-NOTICES.md`, plus `UPSTREAM.md` (source URL, upstream commit, retrieved date, modifications) and `LICENSE.upstream` in the skill directory. Do not edit upstream-derived files beyond what `UPSTREAM.md` records. `check-kit.py` enforces the structure.

## Rules for changes

- Keep the kit project-agnostic: no company, product, customer or person names; use `{{PLACEHOLDERS}}` (declared in `core/placeholders.yaml`, a `type.yaml` or a `pack.yaml`).
- **No secrets or identifiers**: no tokens, keys, passwords, account IDs, ARNs, IP addresses, internal domains or e-mail addresses.
- Edit agent *sources* (`core/agents/`, `repo-types/*/agents/`, `packs/*/agents/`), never generated files.
- Every change gets a `CHANGELOG.md` entry; the maintainer bumps `VERSION`.

## Run the checks

Python 3 (standard library only) is all you need:

```sh
python3 scripts/build-prompts.py      # if you changed prompts/*.md
python3 scripts/check-kit.py          # must print "ok"
python3 -m unittest discover -s scripts -p "test_*.py"
```

`check-kit.py` validates skills, agents, placeholders and prompt sync, and scans for forbidden strings. Built-in patterns are generic (AWS account IDs and ARNs, IPv4 addresses, GitHub tokens, Google OAuth secrets, private keys, password literals). To also catch **your own** domains, organisation names or e-mail patterns, create an untracked `.kit-forbidden.txt` in the kit root (it is in `.gitignore`), one regular expression per line, `#` for comments:

```
# my private identifiers - never committed
example-corp\.com
@example-corp\.
```

The `check-kit` workflow runs the same checks plus an install smoke test on every pull request; it must pass before a merge.
