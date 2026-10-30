---
name: consume-api
description: Call the backend API from {{REPO_NAME}} contract-first. Use when the UI needs data or an action from the backend, or when adding or changing an API call or its types.
---

# Consume the API

The contract is `{{API_CONTRACT}}`.

1. **Find the operation**: path, method, request/response schemas, error responses, auth.
2. **Never invent endpoints, fields or status codes.** Missing or different? Stop. Open or link an issue in `{{BACKEND_REPO}}`; the API change lands first (service map routing). Do not code against a fictional endpoint.
3. **Types.** Hand-type (or generate) from the schema, named after it; no `any`; narrow unknown JSON at the boundary. Do not add dependencies in a feature PR.
4. **Call server-side** with `{{API_URL_ENV}}`; browser calls only via a same-origin proxy that checks `Origin`. Handle timeouts, non-2xx and network errors explicitly; never log tokens or personal data.
5. **Identity and money.** Owner/tenant comes from the session on the API side; money stays decimal string or minor units.
