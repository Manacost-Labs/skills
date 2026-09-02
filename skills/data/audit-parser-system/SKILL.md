---
name: audit-parser-system
description: Deep, evidence-driven audit of the HS Data API parser for fresh-only reliability, completeness, provider failures, schedule coverage, post-patch behavior, and safe remediation. Use when investigating stale or provisional sources, reliability below 99%, parser incidents, patch-day regressions, provider fallbacks, rollout readiness, or before changing publication and freshness logic.
---

# Audit Parser System

Audit the parser as a data pipeline, not merely as an HTTP service. A successful API response is not proof of fresh or complete data.

## Safety rules

- Work in the source repository. Treat `/srv/hs-data-api` as runtime state and never edit it as source.
- Read the nearest `AGENTS.md` and run CodeGraph first when `.codegraph/` exists.
- Do not print or copy cookies, tokens, proxy credentials, `.env` values, response bodies, or production database rows containing sensitive data.
- Keep production probes read-only. Do not call paid providers or force all-source refreshes unless the user explicitly requests them.
- Do not count cached/LKG data, provisional data, an HTTP 200, or a non-empty body as full-fresh success.
- Never improve a percentage by excluding failures unless the occurrence is independently proven ineligible, such as an upstream artifact that has not yet been published. Keep that occurrence excluded from the parser SLO but included as bad in end-to-end freshness.

## Audit workflow

### 1. Establish the exact system under audit

Read `references/system-map.md`. Record the source commit, runtime commit, current UTC time, active patch-policy window, configured schedules, and telemetry coverage start. Separate code defects from deployment drift and from insufficient observation time.

### 2. Capture the public reliability snapshot

Run the bundled analyzer against the public API:

```bash
python .agents/skills/audit-parser-system/scripts/audit_reliability.py \
  --base-url https://api.kolodahearthstone.com/v1
```

For a saved response, use `--input report.json`. The script is read-only and returns a non-zero status only when the report cannot be parsed, not when reliability is poor.

Always report these separately for 24h, 7d, and 30d:

- full-fresh rate;
- end-to-end fresh rate, including independently verified upstream publication gaps;
- accepted-fresh rate, including provisional;
- data-available rate, including LKG;
- exact good, bad, and allowed-bad counts;
- measurement and schedule-ledger coverage;
- verified completeness coverage;
- provider and bounded failure-reason counts.
- recovery of historical provisional/LKG events: later fresh, verified upstream
  publication delay, and still unresolved.

Treat completeness as three independent gates: catalog instrumentation,
instrumented-source observation coverage, and completeness evidence coverage for
all eligible parser attempts. A full catalog alone is not evidence that retrieval
was observed or verified.

If coverage is incomplete, label the result as observed evidence rather than a proven monthly SLO.

### 3. Trace every bad terminal outcome

Inspect the telemetry database with bounded aggregate queries. Rank source IDs by `provisional`, `lkg_served`, `failed`, `timed_out`, and `missing`, then sample only metadata needed to reproduce the classification. Group retries by logical refresh window so retries do not inflate the denominator.

Do not describe every historical provisional/LKG count as still active. Reconcile
it with `outcome_recovery`; recovered events remain bad in their original SLO
window, while `unresolved` is the current remediation queue. A verified upstream
reclassification explains the cause but does not make the served data fresh.

For each offender, determine one primary class:

1. upstream artifact not published;
2. transport/provider failure;
3. authentication or quota failure;
4. semantic extraction failure;
5. contract/completeness failure;
6. regression or patch-baseline mismatch;
7. publication/storage failure;
8. scheduler/telemetry gap;
9. unknown because evidence is insufficient.

Keep `unknown` visible until evidence justifies a narrower class.

### 4. Prove freshness and completeness

For each changed source, verify the full chain:

`upstream evidence -> transport verdict -> parser output -> semantic validator -> source contract -> regression gate -> atomic publication -> public API metadata`

Require source-specific evidence such as upstream timestamp, report/patch identifier, stable entity IDs, expected dimensions, row-count floors, uniqueness, and plausible distributions. Compare hashes only after canonicalization; identical content can be a valid fresh observation when the upstream explicitly confirms it has not changed.

During a patch window, evaluate strict stable rules first. Use provisional rules only when strict rules fail. A new lower baseline may become stable only after repeated, mutually consistent, structurally valid observations tied to the same patch window.

### 5. Audit provider escalation

Confirm the configured order and eligibility rules. Scrape.do is the normal paid transport. Bright Data residential transport must stay disabled unless the user explicitly changes that policy. Check that paid escalation follows a retryable transport failure and cannot be triggered by local schema, parsing, contract, or integration errors.

For ParsesUnix shadow mode, require bounded source allowlists, daily request budgets, per-refresh budgets, sanitized telemetry, and no effect on publication. Promote a source only after enough shadow observations prove transport, candidate, and publication compatibility.

### 6. Audit schedules and observability

Compare all primary schedules in the catalog with the durable schedule ledger. Every due occurrence must become exactly one terminal logical outcome after retries are folded together. Conditional schedules must be explicitly ineligible outside their active policy window, not silently absent.

Check alert delivery configuration without exposing secrets. Confirm alerts distinguish stale upstream, parser failure, provider exhaustion, contract regression, and missing schedules.

### 7. Rank and implement fixes

Rank findings by:

`fresh-data impact x affected sources x recurrence / implementation risk`

Implement one thin slice at a time. Add regression tests for any contract, schema, publication gate, telemetry denominator, scheduler, or post-patch-policy change. Commit independently after each green slice. Never weaken a gate solely to turn the dashboard green.

### 8. Verify and hand off

Run targeted tests, then `make check` and `make security`. Validate the skill itself with:

```bash
python /home/debian/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/audit-parser-system
```

After deployment, compare the runtime commit, `/v1/health`, `/v1/system/parsing-reliability`, and a bounded real refresh. State how many sources produced fresh new observations, how many were unchanged upstream, provisional, LKG, failed, skipped, or missing. Do not claim 99% until a complete observation window proves it.

## Required audit output

Return:

- a short verdict with confidence and observation limits;
- exact current metrics, never rounded claims without counts;
- ranked findings with evidence and affected sources;
- fixes completed, tests run, commits, deployment status;
- remaining actions needed to reach 99% full-fresh over a complete month.
