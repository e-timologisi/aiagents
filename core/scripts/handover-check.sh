#!/usr/bin/env bash
# Read-only handover gate for one pull request (see docs/agents/handover-rules.md).
#
# Usage:
#   scripts/handover-check.sh <owner/repo> <pr> [local-clone]
#   scripts/handover-check.sh --json-file <fixture.json> <owner/repo> <pr> [local-clone]   # test hook
#
# Checks (all must hold for CLEAN):
#   - the PR is OPEN (a merged or closed PR is NOT CLEAN: the gate is for handing over, not after)
#   - mergeStateStatus is CLEAN
#   - 0 unresolved review threads
#   - the LATEST run of every check name succeeded (older failed runs of the same name are ignored)
#   - the PR head equals the tip named by the latest `AGENT-REPORT tip=<sha>` comment
# Info only: whether the `agent-reported` label (AGENT_REPORT_LABEL) is present, and whether the
# optional local clone already has the head commit (local clones can be stale; the API is the truth).
#
# Exit codes: 0 CLEAN, 1 NOT CLEAN, 2 usage or lookup error.
# Needs bash, python3 and (without --json-file) an authenticated `gh`. Never changes anything.
set -euo pipefail

json_file=""
if [[ "${1:-}" == "--json-file" ]]; then
  json_file="${2:-}"
  shift 2 || true
fi
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 [--json-file <fixture.json>] <owner/repo> <pr> [local-clone]" >&2
  exit 2
fi
repo="$1"
pr="$2"
clone="${3:-}"
label="${AGENT_REPORT_LABEL:-agent-reported}"
if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ || ! "$pr" =~ ^[1-9][0-9]*$ ]]; then
  echo "error: expected <owner/repo> and a PR number" >&2
  exit 2
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

if [[ -n "$json_file" ]]; then
  cp "$json_file" "$tmp"
else
  owner="${repo%%/*}"
  name="${repo##*/}"
  pr_json="$(gh pr view "$pr" --repo "$repo" \
    --json state,mergeStateStatus,headRefOid,labels,comments,statusCheckRollup)" || {
    echo "error: gh pr view failed" >&2
    exit 2
  }
  # Read-only GraphQL query (no mutation). Retry once: the endpoint is occasionally flaky.
  query='query($o:String!,$n:String!,$p:Int!){repository(owner:$o,name:$n){pullRequest(number:$p){reviewThreads(first:100){nodes{isResolved}}}}}'
  threads_json=""
  for _ in 1 2; do
    if threads_json="$(gh api graphql -f query="$query" -F o="$owner" -F n="$name" -F p="$pr" \
      --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | {isResolved}]')"; then
      break
    fi
    threads_json=""
  done
  if [[ -z "$threads_json" ]]; then
    echo "error: review threads query failed" >&2
    exit 2
  fi
  printf '{"pr": %s, "threads": %s}\n' "$pr_json" "$threads_json" > "$tmp"
fi

local_info="not given"
if [[ -n "$clone" ]]; then
  head_sha="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["pr"].get("headRefOid",""))' "$tmp")"
  if [[ "$head_sha" =~ ^[0-9a-f]{40}$ ]] && git -C "$clone" cat-file -e "${head_sha}^{commit}" 2>/dev/null; then
    local_info="has the head commit"
  else
    local_info="lacks the head commit (stale or no credentials; the API result above is authoritative)"
  fi
fi

python3 - "$tmp" "$repo" "$pr" "$label" "$local_info" <<'PY'
import json, re, sys

path, repo, pr, label, local_info = sys.argv[1:6]
data = json.load(open(path, encoding="utf-8"))
p, threads = data["pr"], data.get("threads", [])
problems = []

state = p.get("state", "")
if state != "OPEN":
    problems.append(f"PR state is {state or 'unknown'} (only an OPEN PR can be handed over)")
mss = p.get("mergeStateStatus", "")
if mss != "CLEAN":
    problems.append(f"mergeStateStatus is {mss or 'unknown'}, not CLEAN")

unresolved = sum(1 for t in threads if not t.get("isResolved"))
if unresolved:
    problems.append(f"{unresolved} unresolved review thread(s)")

latest = {}
for c in p.get("statusCheckRollup") or []:
    name = c.get("name") or c.get("context") or "?"
    when = c.get("startedAt") or c.get("completedAt") or c.get("createdAt") or ""
    if name not in latest or when >= latest[name][0]:
        latest[name] = (when, c)
ok = {"SUCCESS", "SKIPPED", "NEUTRAL"}
for name, (_, c) in sorted(latest.items()):
    result = (c.get("conclusion") or c.get("state") or "").upper()
    if c.get("__typename", "CheckRun") == "CheckRun" and (c.get("status") or "COMPLETED").upper() != "COMPLETED":
        result = (c.get("status") or "").upper()
    if result not in ok:
        problems.append(f"latest run of check '{name}' is {result or 'PENDING'}")
if not latest:
    problems.append("no checks reported")

head = p.get("headRefOid", "")
report_rx = re.compile(r"^AGENT-REPORT tip=([0-9a-f]{40})\s*$")
reports = []
for c in p.get("comments") or []:
    first = (c.get("body") or "").splitlines()[:1]
    m = report_rx.match(first[0]) if first else None
    if m:
        reports.append((c.get("createdAt") or "", m.group(1)))
if not reports:
    problems.append("no AGENT-REPORT comment")
    tip = "none"
else:
    tip = max(reports)[1]
    if tip != head:
        problems.append(f"latest AGENT-REPORT tip {tip[:12]} != PR head {head[:12]} (a new push invalidates the report)")

labels = {l.get("name") for l in p.get("labels") or []}
print(f"{repo}#{pr} head {head}")
print(f"  state {state}, mergeStateStatus {mss}, unresolved threads {unresolved}, checks {len(latest)} (latest run each)")
print(f"  latest AGENT-REPORT tip: {tip}")
print(f"  info: label '{label}' {'present' if label in labels else 'absent'} (the lead adds it after verifying)")
print(f"  info: local clone {local_info}")
if problems:
    print("NOT CLEAN:")
    for x in problems:
        print(f"  - {x}")
    sys.exit(1)
print("CLEAN")
PY
