---
name: wordpress-ads-analytics
description: Protect advertising and measurement behavior for kolodahearthstone.com when changing or diagnosing Playerok and other banners, ad slots, Plausible tracking, article read events, Blocksy view counters, cache invalidation, mirror delivery, or regional proxy differences. Use for stale ads, missing or duplicated analytics, wrong view counts, and cross-region inconsistencies on the primary, mirror, and staging hosts.
---

# WordPress Ads Analytics

Keep commercial placements current and measurement trustworthy without turning tests into production traffic. Pair this skill with `kolodahearthstone-project`, `wordpress-runtime-stack`, `wordpress-observability`, and `playwright` for browser evidence.

## Measurement contract

- Render the currently configured Playerok banner and target once per intended slot. Do not allow an older cached creative to survive on any edge after a targeted release purge.
- Load one Plausible tracker per page. Keep `data-domain="kolodahearthstone.com"` as the shared reporting property unless an explicitly approved analytics migration changes it.
- A `.com` visit may be measured as mirror traffic, but one browser page load must not emit both mirror and primary pageviews or duplicate article events.
- Keep analytics disabled on staging by default. Active event tests use a disposable staging article and an explicit test marker; never generate synthetic production views.
- A single accepted Blocksy view action may increment `post_views_count` at most once. Cache replay, retries, the mirror rewrite, and multiple frontend handlers must not produce a second increment.

Read [references/measurement-contracts.md](references/measurement-contracts.md) before changing Plausible or view counting. Read [references/delivery-matrix.md](references/delivery-matrix.md) for banner/cache incidents.

## Ownership map

- Banner normalization and the current top creative: `wordpress/mu-plugins/manacost-performance-optimizer.php`.
- Plausible loader, article events, and event properties: `wordpress/mu-plugins/plausible-analytics.php`.
- Blocksy view actions and deduplication: `wordpress/mu-plugins/hs-admin-ajax-guard.php`.
- Origin protection and public view routing: `ops/nginx/resources/20-origin-guard.conf`.
- First-party analytics proxy: `ops/nginx/resources/plausible-first-party.conf`.
- Runtime ad configuration in Blocksy, Ad Inserter, WP Rocket, Redis, and Cloudflare remains data/configuration; do not edit generated cache files as source.

## Workflow

1. Record the exact page, slot, expected creative URL/target, device, authentication state, region, response headers, and whether the response is cold or warm.
2. Locate the owning source/configuration layer. Compare origin, Moscow, Novosibirsk, `.ru`, and `.com` before invalidating anything.
3. Run the bundled passive HTML audit. It does not send analytics events or increment views:

```bash
python3 .agents/skills/wordpress-ads-analytics/scripts/audit_ads_analytics.py \
  --target primary=https://kolodahearthstone.com/ \
  --target mirror=https://kolodahearthstone.ru/ \
  --expected-banner /wp-content/uploads/2026/07/728x90.jpg \
  --forbidden-banner /wp-content/uploads/2026/03/heartstone_sajt.png.webp
```

4. For browser verification, block the outbound Plausible request first, capture the attempted requests, and assert exactly one pageview plus the intended custom events. Do not rely only on DOM script count.
5. Test view increments only on a disposable staging post: read the counter, perform one browser navigation/action, wait for completion, read it again, and require a delta of zero or one according to the documented trigger. Repeat through the mirror route and require no second increment from the same action.
6. Apply the smallest fix, invalidate the owning cache keys, then repeat the delivery matrix and inspect analytics/view logs for errors and duplicates.

## Evidence required

- Before/after creative URL and target for every affected slot.
- Response cache headers and body evidence for origin and both RU edges.
- Captured Plausible request count, domain, page URL, event name, and test marker with personal data removed.
- Staging-only view-counter before/after values and action name.
- Confirmation that `.com` remains canonical/indexable, `.ru` remains a redirect, and staging analytics remains disabled.

## Hard stops

- Do not click paid links, create impressions, or increment production counters merely to prove rendering.
- Do not use production Plausible dashboards or counters as destructive test fixtures.
- Do not load both a direct Plausible script and the first-party proxy.
- Do not change the canonical/noindex policy to simplify analytics.
- Do not start with purge-all, Redis flush, plugin disablement, or direct edits under `/var/www`.
