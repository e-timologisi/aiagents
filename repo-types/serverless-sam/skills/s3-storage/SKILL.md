---
name: s3-storage
description: Add or change S3 buckets, prefixes, lifecycle rules or presigned URLs in {{REPO_NAME}}. Use for document storage, exports or any object storage work.
---

# S3 storage

Records that must be retained (e.g. legal documents) are never deleted by automation; exposing one to the wrong user is a release blocker.

## Bucket defaults
- Name `{{STACK_PREFIX}}-<purpose>-${Environment}-${AWS::Region}`; tags `Project`, `Environment`.
- Default encryption (SSE-S3 minimum; SSE-KMS with a dedicated key if per-key audit is needed).
- `PublicAccessBlockConfiguration` all `true`; `OwnershipControls: BucketOwnerEnforced`.
- Versioning for buckets holding final documents; bucket policy denying non-TLS access.
- `DeletionPolicy: Retain` / `UpdateReplacePolicy: Retain` for retained records.
- Retention periods: **to be validated by an expert**; do not invent them. Object Lock only after an ADR.

## Lifecycle
- Expiration **only** on explicitly temporary prefixes (e.g. `tmp/`), filtered by prefix, never whole-bucket.
- Never a rule that can match final/retained documents. Prefer separate buckets for final and temporary data.

## Keys and isolation
- Opaque IDs in keys, e.g. `owners/<owner_id>/<kind>/<yyyy>/<mm>/<id>.pdf`; no names or personal identifiers in keys or metadata.
- The owner id comes from the backend after authorization, never from a client payload.

## Presigned URLs
- Generated only after the backend authorized the user for that object; `GET` only, short expiry (minutes), one object per URL.
- Never log full presigned URLs or email them as long-lived links.

## Verify and document
`{{INTEGRATION_CMD}}` and review the template diff. Update README, `{{DOCS_REPO}}` notes/ADR and the issue.
