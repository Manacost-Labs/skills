---
name: wordpress-admin-performance
description: Measure, diagnose, improve, and regression-test authenticated WordPress administration performance for hs-manacost.ru. Use when wp-admin, the article editor, media library, list tables, settings pages, AJAX/REST actions, autosave, search, filtering, saving, or bulk actions feel slow; when admin work degrades with large datasets; or when an admin UI change needs performance budgets and before/after evidence.
---

# WordPress Admin Performance

Improve the editor's real workflow, not an isolated synthetic number. Keep permissions, saving, autosave, revisions, media/S3, counters, accessibility, and error handling correct while reducing latency and browser work.

## Project boundaries

- Work in `/srv/projects/wordpress/hs-manacost.ru`; treat `/var/www` as runtime only.
- Target WordPress 6.9.7, PHP-FPM 8.4, MariaDB 10.11 and the committed Newspaper integrations.
- Use `wordpress-admin-ui` for UX, `wp-performance` for backend profiling, `wordpress-observability` for runtime signals, and `wordpress-article-editor` when editor behavior is involved.
- Test changes on `test.hs-manacost.ru`. Do not load-test production, enable `SAVEQUERIES`, install profilers, expose timing details, or flush caches there without explicit authorization.
- Never improve a number by weakening capabilities, nonces, Wordfence, autosave, revisions, view counting, S3 correctness, accessibility, or cache correctness.

## Required workflow

1. Name one operator journey and its user-visible delay: for example opening the editor, filtering 1,000 posts, selecting media, autosaving, publishing, or completing a bulk action.
2. Record environment, authenticated role, dataset size, route/screen, cache state, browser viewport, and network conditions. Never store cookies, credentials, personal data, post bodies, or signed URLs in evidence.
3. Select the relevant guide:
   - measurement method and trace hygiene: [profiling.md](references/profiling.md)
   - budgets and metric definitions: [budgets.md](references/budgets.md)
   - SQL, options, cache, cron and PHP work: [database-and-runtime.md](references/database-and-runtime.md)
   - editor, AJAX, REST and asset work: [editor-and-ajax.md](references/editor-and-ajax.md)
   - browser scenarios and release evidence: [testing-and-release.md](references/testing-and-release.md)
4. Capture at least five comparable baseline samples. Separate cold and warm cache runs instead of averaging them together.
5. Locate the first abnormal layer: navigation/network, PHP bootstrap/hook, SQL/options, remote HTTP, cron, REST/AJAX, asset loading, main-thread work, DOM/rendering, or repeated polling.
6. Add a failing regression check or a reproducible budget report before changing behavior. Optimize one dominant bottleneck with the smallest supported extension point.
7. Repeat the same samples and run the complete operator journey, including loading, empty, error, permission-denied, mobile and desktop states.
8. Store a non-secret evidence manifest outside runtime data and run:

```bash
.agents/skills/wordpress-admin-performance/scripts/evaluate_admin_performance.py report.json
```

   For the automated isolated WordPress suite, run `make admin-performance`. The collector in `ops/performance` records five browser samples for Dashboard, posts, media and the editor, builds evaluator-compatible reports with `config/admin-performance-budgets.json`, and stores only non-secret artifacts under `.artifacts/admin-performance`.

9. Run `make check`, the staged security scan, deploy through Git, and verify staging. A `PASS` report complements behavioral tests; it never replaces them.

## Measurement contract

- Compare the same screen, role, data volume, cache state, viewport and network profile.
- Use medians for navigation/server timings and p95 for repeated AJAX/REST actions. Keep raw samples when available.
- Require at least `ttfb_ms`, `interactive_ms`, `sql_queries`, `peak_memory_mb`, and `long_tasks` in the evidence manifest.
- Block release when a metric exceeds its approved budget, regresses by more than 5%, or any functional check fails.
- Treat default budgets as starting gates, then tighten them from stable project baselines. Never raise a budget only to make a change green.
- Report both absolute results and percentage change; a faster empty database is not evidence for a large editorial dataset.

## Diagnostic order

1. Confirm the slowdown with the real role and data size.
2. Inspect network waterfall and repeated requests.
3. Measure server/SQL/options/cache/remote calls.
4. Measure browser long tasks, transferred assets and rendering.
5. Attribute the cost to an owned hook, query, endpoint, asset or component.
6. Fix the cause rather than hiding it behind a global cache, delayed spinner or disabled feature.

Prefer bounded queries, server-side pagination, screen-scoped assets, cached stable computations, batched requests, debounced search, targeted invalidation, background processing, and progressive feedback. Require rollback for every cache/schema/background-job change.

## Hard stops

- Do not compare anonymous public pages with authenticated wp-admin requests.
- Do not mix cold and warm measurements or compare different data sizes/roles.
- Do not print auth cookies, nonces, SQL values, post content, user identifiers, secrets or unrestricted traces.
- Do not add a performance plugin, profiler, persistent cache, index or dependency before measurement proves the owning bottleneck.
- Do not use unbounded post/media/user queries, synchronous remote calls in page rendering, global admin assets, polling without backoff, or optimistic writes without rollback.
- Do not claim success from one fast request, a Lighthouse score, a screenshot, or a passing budget with broken behavior.

## Completion evidence

Report the journey, baseline and after measurements, sample count, role/data/cache context, first abnormal layer, implemented cause-level fix, functional checks, budget result, staging SHA, rollback, and remaining limitation. Separate measured facts from inference.
