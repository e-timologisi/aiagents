# AWS cost optimization

- Pay-per-use services first; prefer arm64 where supported.
- Benchmark memory and timeouts; change them only with a measured reason.
- Every stack: AWS Budget with alerts, CloudWatch log retention set explicitly, alarms for errors/throttles.
- Free tiers expire or have limits; check current pricing instead of assuming free.
- Least-privilege IAM per function on exact resources; CI uses OIDC roles, no long-lived keys.
- Lifecycle-delete only explicitly temporary exports/prefixes; preserve retained records under an approved retention policy.
- Avoid NAT gateways and always-on resources unless an ADR justifies the cost.
- Per-customer resources (schedules, queues) multiply cost; prefer fan-out from shared resources.
