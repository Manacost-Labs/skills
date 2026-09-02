---
name: wordpress-runtime-stack
description: Safely operate, change, update, debug, and validate the active kolodahearthstone.com WordPress runtime plugin stack. Use for WP Rocket, Redis, Cloudflare, proxy cache, Perfmatters, All in One SEO, Wordfence, Redirection, plugin compatibility, cache purge, WAF incidents, SEO runtime settings, plugin updates, or rollback planning.
---

# WordPress Runtime Stack

Operate the installed cache, optimization, SEO and security plugins as a layered system. Diagnose the owning layer first, change one responsibility at a time, and preserve a tested rollback.

## Project invariants

- Work from `/srv/projects/wordpress/kolodahearthstone.com`; inspect production read-only and deploy source changes to staging first.
- The active stack includes WP Rocket page cache, Redis object cache, Cloudflare integration, custom production proxy paths, Perfmatters optimizations, All in One SEO, Wordfence and Redirection.
- Custom MU-plugins, especially `manacost-cache-purge`, domain mirror rules, media/S3 integration and view counting are part of runtime behavior even though they are not ordinary plugins.
- Keep `kolodahearthstone.com` canonical and indexable, `kolodahearthstone.ru` a one-hop legacy redirect to `.com`, and `test.kolodahearthstone.com` noindex.
- Do not expose configuration values, API tokens, licenses, salts, cookies, database contents or private keys while inspecting the stack.

## Required workflow

1. Classify the symptom: origin application, database/object cache, page cache, asset optimization, Cloudflare, regional proxy, browser, SEO metadata/redirect, WAF or plugin update.
2. Inspect active versions, health and relevant configuration without printing secret values. Capture the failing URL, request type, authentication state, region/edge and cold/warm response evidence.
3. Read the relevant guide:
   - Installed ownership and conflict map: [stack-map.md](references/stack-map.md)
   - Cache layers, targeted purge and warming: [cache-layers.md](references/cache-layers.md)
   - All in One SEO, Redirection and Wordfence boundaries: [seo-security.md](references/seo-security.md)
   - Safe inspection, update and rollback operations: [operations.md](references/operations.md)
   - Cross-region verification matrix: [testing.md](references/testing.md)
4. Reproduce on staging when possible. For a production incident, use read-only comparisons to isolate the first layer that diverges.
5. Make one minimal, reversible change in source or the correct configuration owner. Do not make the same optimization in WP Rocket and Perfmatters.
6. Invalidate only affected URLs or cache groups, working from origin/application outward, then warm public URLs through the intended paths.
7. Compare cold and warm responses on staging, origin, the public domain and every configured production proxy. Check authenticated and anonymous behavior when relevant.
8. Run `make check`, security validation, staging deploy and smoke checks. Promote only a tested commit and retain an executable rollback.

## Layer ownership

- WP Rocket owns generated page cache, preload and its CSS/JavaScript optimizations.
- Redis owns persistent WordPress object cache. A Redis flush is not a page-cache purge and is not a routine content-update step.
- Cloudflare and the Moscow/Novosibirsk proxy paths own external delivery and can retain stale responses after origin caches are correct.
- Perfmatters owns only the optimizations deliberately assigned to it. Audit overlap before enabling minify, delay, lazy-load or asset removal.
- `manacost-cache-purge` coordinates content-driven invalidation. Extend and test it rather than adding unrelated broad purge hooks.
- All in One SEO owns SEO metadata and generated sitemap behavior; Redirection owns intentional redirects; domain mirror code owns canonical/noindex host policy.
- Wordfence owns WAF and security scanning. Cache or performance work must not bypass its protection.

## Non-negotiable rules

- Prefer a targeted purge of the changed URL and known dependent archives over purge-all. Never use global cache clearing as the first diagnostic action.
- Do not flush Redis unless stale object data has been demonstrated and the blast radius is understood.
- Do not disable Wordfence, Cloudflare protection, cache correctness, article counters, personalization or ads for a synthetic performance score.
- Do not update all plugins together. Update one plugin family on staging, record the prior version, test its owned flows and prepare rollback before promotion.
- Never directly modify bundled/vendor plugin source for configuration behavior. Use documented settings, filters, MU-plugin integration or a pinned source update.
- Treat firewall rules, redirects, robots, canonical, sitemap and proxy configuration as production behavior requiring regression coverage.
- Preserve bypass rules for authenticated editors, previews, AJAX, REST writes and other personalized requests; public cache must never expose private content.

## Incident decision rules

- If origin is correct but a public edge is wrong, inspect and purge only that outer cache layer.
- If HTML is current but assets are stale, version the asset URL or purge the exact asset; do not clear unrelated article pages.
- If only authenticated requests fail, compare cache bypass, cookies, nonce lifetime and Wordfence before changing public cache policy.
- If a request is blocked, use Wordfence diagnostics/log evidence and narrowly safelist the verified action. Never blanket-disable the WAF.
- If an SEO URL changes, define the `.com` canonical and one-hop legacy redirect first, then purge affected HTML/sitemap URLs and verify on `.com`, `.ru` and staging.

## Hard stops

- Do not edit `wp-config.php`, the Wordfence optimized-firewall bootstrap, production nginx or Cloudflare account settings without explicit task scope and a rollback.
- Do not run destructive database, cache, plugin reset, update-all or deactivate-all commands.
- Do not promote when any proxy serves a different canonical, robots policy, image, article body or status code from the intended production result.
- Do not declare success from one browser request; verify a cold request, a warm request and the required regional routes.

## Completion report

Report the owning layer, evidence before and after, exact invalidation scope, cold/warm and proxy results, SEO/security impact, staging result, deployed commit and rollback path. Separate measured results from assumptions.
