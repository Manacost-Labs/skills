---
name: wordpress-seo-editorial
description: Protect the kolodahearthstone.com editorial SEO contract when creating, editing, publishing, auditing, or migrating WordPress articles, categories, landing pages, metadata, schema, canonical URLs, robots directives, sitemaps, internal links, and images. Use for SEO/editorial work across canonical kolodahearthstone.com, the kolodahearthstone.ru legacy redirect, and noindex test.kolodahearthstone.com staging.
---

# WordPress SEO Editorial

Preserve one indexable source of truth while improving the usefulness and discoverability of editorial content. Pair this skill with `kolodahearthstone-project`, `wordpress-article-editor`, `wordpress-content-integrity`, and the relevant official SEO skill.

## Non-negotiable host contract

- Keep `https://kolodahearthstone.com` as the only indexable host and the canonical host for equivalent production content.
- Keep `https://kolodahearthstone.ru` as a one-hop permanent redirect to the matching `.com` URL. Do not emit mirror HTML, sitemap entries, or a competing canonical.
- Keep `https://test.kolodahearthstone.com` `noindex, nofollow, noarchive`, including error and authentication responses. Never place staging URLs in production schema, canonical tags, feeds, sitemaps, OpenGraph, or internal links.
- Do not create hreflang or competing canonicals between `.ru` and `.com`; they are not language variants.

Read [references/host-policy.md](references/host-policy.md) before changing canonical, robots, sitemap, redirects, domain rewriting, or AIOSEO behavior.

## Editorial workflow

1. Identify the content type, intended search intent, canonical URL, primary category, author, publication state, and representative image.
2. Inspect the stored WordPress fields and rendered output. Do not infer stored metadata from a cached page alone.
3. Preserve editorial intent. Improve titles and descriptions without fabricating facts, keywords, dates, authors, ratings, or structured-data properties.
4. Validate the checklist in [references/editorial-checklist.md](references/editorial-checklist.md). Treat SEO scores as advice, not a publishing gate.
5. Check the same path on `.com`, the one-hop `.ru` redirect, and staging. Test anonymous cold and warm responses; add desktop/mobile only when output can vary by device.
6. Invalidate only the owning cache keys after a change. Recheck the primary, mirror, origin, Moscow edge, and Novosibirsk edge when production delivery is affected.

## Source ownership

- Domain/canonical/noindex mirror behavior: `wordpress/mu-plugins/manacost-domain-mirror.php`.
- Project SEO enrichment and fallback schema: `wordpress/mu-plugins/manacost-aioseo-addon.php`.
- AIOSEO runtime settings and editorial post metadata: production data, not Git source. Inspect read-only and change through supported WordPress/AIOSEO APIs.
- Staging robots headers and robots response: `ops/nginx/staging.conf` plus WordPress behavior.
- Theme presentation: use `blocksy-theme`; do not patch the Blocksy parent theme for metadata ownership.

## Deterministic host audit

Run the bundled passive checker against representative public pages:

```bash
python3 .agents/skills/wordpress-seo-editorial/scripts/audit_seo_hosts.py \
  --target primary=https://kolodahearthstone.com/example/ \
  --target mirror=https://kolodahearthstone.ru/example/
```

The checker verifies status, title, canonical count/host, robots directives, mirror marker, schema syntax, and image alt coverage. A clean result proves only these observable contracts; it does not prove rankings, crawl state, or editorial quality.

## Change gates

- Add a regression test for every changed host, metadata, schema, sitemap, or rewrite rule.
- Run `make contracts` when post meta, options, endpoints, cron hooks, or capabilities change.
- Run `make integration` for publication, canonical, media, view, or cache behavior.
- Run `make visual` only when rendered Blocksy/editor UI changes.
- Run `make check` and the staged security check before handoff.

## Hard stops

- Do not make the `.ru` legacy redirect indexable or create a second `.ru` HTML mirror.
- Do not redirect `.com` to `.ru`; `.com` is the canonical production origin and must remain usable independently.
- Do not add schema that is not supported by visible content.
- Do not bulk-rewrite posts, attachment URLs, or AIOSEO data without the database-migration workflow, a dry-run count, backup, and rollback.
- Do not purge all cache layers as the first diagnostic action.
