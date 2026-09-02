---
name: kolodahearthstone-project
description: Provide the authoritative architecture, domain policy, source/runtime boundaries, and delivery workflow for the KolodaHearthstone WordPress project. Use for every WordPress, Blocksy, plugin, editor, media, SEO, cache, proxy, CI, or production task.
---

# KolodaHearthstone project

This repository is the source of code and safe configuration for the WordPress site served at `kolodahearthstone.com`. The active theme is Blocksy; `kolodahearthstone.ru` is a legacy domain that redirects to `.com`; `test.kolodahearthstone.com` is the isolated staging target.

## Start every task

1. Read the repository `AGENTS.md` and run `git status --short`.
2. Run `.agents/skills/kolodahearthstone-project/scripts/context-snapshot.sh`.
3. Run `wordpress-change-impact` before code, theme, plugin, CI, nginx, or configuration changes.
4. Select only the specialist skills required by `config/ai-skills.json`.
5. Keep source, runtime, database, uploads, S3 objects, caches, backups, and secrets in separate ownership zones.

## Invariants

- `kolodahearthstone.com` is canonical and indexable.
- `kolodahearthstone.ru` remains a one-hop redirect to `.com`.
- `test.kolodahearthstone.com` is isolated and `noindex`.
- The Moscow/Novosibirsk proxy paths serve the same origin; they do not hold independent WordPress copies.
- Blocksy parent files, generated CSS, caches, uploads, database rows, and runtime plugin backups are not source files.
- Shared first-party plugins, especially `hs-tooltip`, use one pinned source commit and verified SHA256 in every consuming site repository.

## Change workflow

1. Capture a failing test or reproducible baseline.
2. Make the smallest supported child-theme/plugin/config change.
3. Run code quality, contract, integration, visual, accessibility, and security checks appropriate to the changed surface.
4. Deploy the exact commit to staging, verify anonymous/authenticated flows and both domains, then promote manually.
5. Keep a backup and executable rollback for plugin/theme/runtime changes.

## Data and security

Never commit `wp-config.php`, `.env`, credentials, Telegram/S3/Cloudflare tokens, license keys, cookies, personal data, database dumps, uploads, caches, logs, or backups. Export theme/plugin settings only through an explicit allowlist with secret redaction. Do not use production as a destructive test fixture.

## Blocksy boundary

Use `$blocksy-theme` for parent/child theme, Customizer, `theme.json`, header/footer, dynamic CSS, template, or responsive layout work. Prefer child-theme and documented Blocksy extension points; never patch the Blocksy parent.

## Completion evidence

Report changed source paths, tests, staging commit/URL, production promotion state, cache/SEO/security impact, regional checks, and rollback target. Separate observed facts from assumptions and state explicitly when production was not changed.
