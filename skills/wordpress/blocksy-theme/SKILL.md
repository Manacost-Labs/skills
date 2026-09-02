---
name: blocksy-theme
description: Safely develop, review, and optimize the Blocksy theme and Blocksy Companion in the KolodaHearthstone WordPress project. Use for child-theme code, Customizer settings, theme.json, header/footer builder, archive/single templates, dynamic CSS, responsive layout, or theme updates.
---

# Blocksy theme

Treat Blocksy, Blocksy Companion, the child theme, Customizer options, generated CSS, cache, and Koloda plugins as one coupled publishing surface. Keep the parent theme update-safe and preserve the `.com` canonical domain, `.ru` redirect, media, shortcodes, analytics, and editor workflows.

## Required workflow

1. Read `AGENTS.md`, run the project context snapshot, and inspect the active Blocksy/Companion versions.
2. Run `scripts/audit_blocksy_change.py --repo . --base HEAD --include-untracked` before editing.
3. Identify the narrowest supported extension point in this order: child theme, Blocksy Customizer/`theme.json`, documented Blocksy hook, site plugin, then template override.
4. Never edit the parent `wordpress/themes/blocksy` or generated cache files directly.
5. Add a reproducible unit, integration, or browser check before behavior changes; capture desktop and mobile baselines for visual changes.
6. Stage the diff and run the audit again with `--staged --strict`, then run the repository checks and security scan.
7. Deploy to `test.kolodahearthstone.com` first and verify home, article, archive, search, editor, menus, shortcodes, media, ads, canonical/robots, and view counters.

## Blocksy-specific rules

- Custom PHP/CSS/JS belongs in `wordpress/themes/blocksy-child` or a first-party plugin; do not fork or patch Blocksy parent files.
- Keep `theme.json` tokens and Customizer values consistent; do not introduce a competing global design-token system.
- Scope dynamic CSS to the Blocksy selectors that own the component. Avoid global `!important`, arbitrary negative margins, and layout fixes that hide overflow.
- Preserve Blocksy header/footer builder structure, sidebar behavior, post-content width, featured-image settings, and mobile menu semantics.
- Treat Blocksy Companion as an optional dependency: feature-detect it and degrade without a fatal error when it is unavailable.
- Theme settings exported to Git must be an allowlisted, secret-free snapshot. Tokens, license values, cookies, database values, and private URLs stay outside Git.

## Compatibility matrix

Every theme or shared-plugin change is checked against:

- WordPress 6.9.7 and PHP 8.4;
- Blocksy 2.1.40 and Blocksy Companion 2.1.40;
- Classic Editor/TinyMCE and Gutenberg where enabled;
- `hs-tooltip`, Koloda shortcodes/decks, cache, SEO, Wordfence, and image optimization;
- 320/390/768/1024/1440 CSS pixels, 200% zoom, keyboard navigation, and touch input.

## Hard stops

- Do not replace the Blocksy parent theme with an unreviewed fork.
- Do not edit serialized Customizer values with blind SQL search/replace.
- Do not accept a desktop screenshot as proof of responsive or editor compatibility.
- Do not change canonical/robots, counters, media URLs, or cache behavior as a side effect of a visual change.

## Evidence

Record the active theme/plugin versions, changed extension point, visual screenshots, browser console/network result, `make check`, security result, staging URL/commit, and rollback target.
