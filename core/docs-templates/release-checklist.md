# Release checklist

Production releases are run by a human ({{RELEASE_OWNER}}). Agents prepare evidence with the `release-checklist` skill and never trigger the release.

## Before the release

- [ ] **Released PRs are listed** (`git log <last-tag>..origin/{{DEFAULT_BRANCH}} --oneline`).
- [ ] **`{{DEFAULT_BRANCH}}` contains the reviewed commits.** For every PR: the reviewed head SHA is the PR head at merge, and `git diff <pr-head-sha> <merge-commit> -- <PR files>` is empty. *Lesson: a PR squash-merged at its first commit lost later fix commits; an unfixed version reached production.*
- [ ] **CI is green in the run that built the artifact**; build/deploy jobs `needs:` lint, test and security. *Lesson: never let image build/deploy run unless checks pass in the same run.*
- [ ] **Security review done** for PRs touching auth, sessions, crypto, permissions or data access; **second review after fixes** for auth/sessions/crypto.
- [ ] **Staging smoke test by a human** on {{STAGING_URL}} with the exact artifact (SHA/tag) to be released.
- [ ] **Coupled releases ordered**: provider (backend) before consumers; migrations backward compatible with the running release.
- [ ] **Secrets present** in the production environment (names only checked; values never printed). Deploy writes them to root-only files; nothing is hand-edited on servers.
- [ ] **Backup/preflight** done where data changes (migrations).
- [ ] **Rollback** plan: previous tag; any security-weakening downgrade needs explicit owner approval.
- [ ] **Accepted risks** reviewed (e.g. required-reviewer protection unavailable on the current plan; preconditions such as "restrict environments before adding collaborators").

## After the release
- [ ] Health checks on {{PROD_URL}}.
- [ ] Release notes / CHANGELOG; ADR implementation notes if relevant.
- [ ] Issues commented and closed; follow-ups opened.
