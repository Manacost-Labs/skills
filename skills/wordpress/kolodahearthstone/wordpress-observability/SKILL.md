---
name: wordpress-observability
description: Measure and report health, availability, latency, errors, capacity, cron, queues, PHP-FPM, MariaDB, WordPress, cache, S3 offload, image optimization, backups, Cloudflare, and regional proxies for kolodahearthstone.com. Use for health reports, monitoring design, performance diagnosis, capacity alerts, SLOs, post-release observation, and recurring operational checks.
---

# WordPress Observability

Collect decision-ready signals without exposing secrets or mutating the system. Measure the user journey and each owning layer, not only process uptime.

## Start here

1. Use `kolodahearthstone-project`; add `wordpress-runtime-stack` for cache/runtime and `wordpress-media-integrity` for media.
2. Run `scripts/read-only-health.sh` for a safe local snapshot. Add `--probe` only when external HTTP checks are appropriate.
3. Read [signals.md](references/signals.md) to select measurements.
4. Read [health-report.md](references/health-report.md) before presenting conclusions.

## Workflow

1. Define the user-visible question, interval, environment and comparison baseline.
2. Collect timestamps, request route and cold/warm/authentication context with each sample.
3. Measure from outside inward: DNS/TLS, public domains/proxies, origin, application, database/cache, cron/queues, media/S3 and capacity.
4. Correlate a symptom with the first abnormal layer. Do not infer a cause from one metric.
5. Bound log queries by time/service and redact tokens, cookies, query values, post bodies, IPs and personal data.
6. Compare before/after using the same URL, headers, route and cache state.
7. Turn recurring failure modes into automated status checks with explicit thresholds and runbooks.
8. During release observation, verify the exact deployed SHA and the changed flow, not only the homepage.

## Required signals

- availability/status and latency for `kolodahearthstone.com`, `kolodahearthstone.ru`, `test.kolodahearthstone.com`, origin, Moscow and Novosibirsk;
- canonical/robots correctness per host;
- PHP-FPM and MariaDB health, saturation and error trends;
- WP-Cron/Action Scheduler lateness and failures;
- WP Rocket/Redis/edge cache cold-versus-warm behavior;
- `hs-local-image-optimizer` queue/result failures and sidecar savings;
- `hs-manacost-s3-offload` freshness/failures and independent backup restore freshness;
- disk/inode pressure, especially upload and cache paths;
- application error rate and slow query/TTFB trends.

## Safety rules

- Default to read-only commands and bounded requests with timeouts.
- Never print environment files, credentials, cookies, signed URLs, SQL values or unrestricted logs.
- Never enable debug display on production; direct errors to protected logs with retention.
- Do not purge caches, restart services or repair queues as part of observation.
- Do not optimize away view counting, security, personalization or editorial correctness to improve a metric.
- Separate observed facts, thresholds, inference and recommended action.

## Completion evidence

Report observation window, routes, cold/warm state, measurements, first abnormal layer, threshold/baseline, confidence, user impact, next safe action and its rollback. State gaps where a signal is unavailable.
