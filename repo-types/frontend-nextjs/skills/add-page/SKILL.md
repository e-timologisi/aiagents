---
name: add-page
description: Add a route/page to the {{REPO_NAME}} Next.js App Router. Use when creating a new screen, page, layout or route segment in this repo.
---

# Add a page

1. **Contract first.** Find the data the page shows in `{{API_CONTRACT}}`. If the operation is missing, follow `consume-api` and stop.
2. **Location.** `app/<segment>/page.tsx`. Add `loading.tsx` and `error.tsx` (`"use client"`) in the same segment. Route handlers under `app/api/` only for UI concerns, never business logic.
3. **Data fetching.** Async server components fetch the API server-side: base URL from `process.env.{{API_URL_ENV}}` at request time (`cache: "no-store"` for per-user data), with a timeout and explicit handling of non-OK responses. Forward the user's session; never send an owner/tenant id chosen in the browser.
4. **No calculations.** Display what the API returns. Money arrives as decimal strings or minor units: format it, never float arithmetic.
5. **Types.** TypeScript strict, no `any`; types come from the contract (see `consume-api`).
6. **Text.** {{UI_LANGUAGES}}; terms from the glossary; no hardcoded strings if the repo uses dictionaries.
7. **Accessibility.** Landmarks (`main`, one `h1`), labelled controls, keyboard reachable, errors announced (`role="alert"`).
8. **Protected pages** use the repo's auth guard; add new protected prefixes where the repo lists them.
9. **Tests.** Cover rendering and loading/error states. No test setup? Say so in the PR and open a follow-up; do not add tooling in a page PR.
10. Run `{{LINT_CMD}} && {{INTEGRATION_CMD}} && {{BUILD_CMD}}`; update the README routes list.
