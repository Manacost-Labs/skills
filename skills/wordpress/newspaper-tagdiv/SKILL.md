---
name: newspaper-tagdiv
description: Safely develop, review, update, debug, and optimize the tagDiv Newspaper theme and its coupled plugins in the hs-manacost.ru repository. Use for any change touching Newspaper_new, tagDiv Composer, tagDiv Standard Pack, Cloud Library templates, tagDiv blocks/modules/API, theme CSS, child-theme overrides, header/footer/single/category/search templates, or Newspaper-specific MU-plugin compatibility.
---

# Newspaper + tagDiv

Protect the production publishing surface while changing Newspaper 12.7.3 and its tagDiv plugins. Treat the theme, Composer, Standard Pack, Cloud Library, WordPress options, generated Cloud Templates, caches, and Manacost MU-plugins as one coupled system.

## Project invariants

- Work only in `/srv/projects/wordpress/hs-manacost.ru`.
- The active theme is `wordpress/themes/Newspaper_new` (Newspaper 12.7.3).
- Prefer a scoped MU-plugin, public hook, Cloud Template, or child-theme override over editing vendor code.
- Never edit production runtime first. Deploy to `test.hs-manacost.ru`, verify, then promote the exact tested commit.
- Preserve `.ru` as canonical, `.com` as the noindex mirror, and `test` as noindex.
- Preserve article view counting, S3 media URLs, ads, cache invalidation, editor workflows, and both RU proxy paths.
- Do not update the theme and tagDiv plugin family as an incidental part of another change.

## Required workflow

1. Run `python3 .agents/skills/newspaper-tagdiv/scripts/audit_newspaper_change.py --repo . --base HEAD --include-untracked` before editing to see the protected surface.
2. Read only the relevant guide:
   - ownership, update survival, visual regression, and rollback: [change-safety.md](change-safety.md)
   - Composer pages and editor behavior: [composer.md](composer.md)
   - Cloud Templates and assignment: [cloud-templates.md](cloud-templates.md)
   - `td_api_*` registration and overrides: [theme-api.md](theme-api.md)
   - module rendering: [modules.md](modules.md)
   - block/shortcode containers: [blocks.md](blocks.md)
   - CSS and responsive changes: [css-rules.md](css-rules.md)
   - speed, cache, images, and counters: [performance.md](performance.md)
   - update-safe PHP/template overrides: [child-theme.md](child-theme.md)
3. Identify the narrowest supported extension point. Search dependencies before changing a `td_*` class, hook, shortcode, option, template, module, or block.
4. Add a reproducible check before behavioral code. For visual work, capture desktop and mobile baselines.
5. Make the smallest source change. Do not modify minified output alone.
6. Stage the intended diff and run the audit again with `--staged --strict`.
7. Run `make check`, the project security check, staging deploy, and staging smoke-check.
8. Verify homepage, article, category, search, editor/Composer save flow, mobile layout, console/network errors, images, ads, and view-counter behavior when affected.

## Extension decision

Use this order:

1. Existing Manacost MU-plugin for site-specific behavior.
2. WordPress/tagDiv public hook or `td_api_*` registration from a site plugin.
3. Cloud Template or Composer setting for layout/content structure.
4. Child theme for supported template/module/block overrides.
5. Direct parent-theme or tagDiv plugin edit only when no supported extension exists and the user explicitly accepts the upgrade burden.

## Hard stops

- Do not copy the parent `functions.php` into a child theme.
- Do not mix tagDiv Composer with another builder on the same page.
- Do not edit serialized Cloud Template content using unsafe SQL or blind search/replace.
- Do not change `TD_THEME_OPTIONS_NAME`, template IDs, shortcode IDs, or module IDs without a migration and rollback.
- Do not deactivate `td-composer` or `td-standard-pack` on production to test an idea.
- Do not purge all caches on every request or bypass cache/security/canonical rules for a synthetic speed gain.
- Do not promote if staging has PHP warnings, JavaScript errors, missing images, empty grids, broken menus, failed Composer saves, or unexpected canonical/robots output.

## Version compatibility

The project currently runs WordPress 6.9.7, while the installed official WordPress agent skills target WordPress 7.0+. Their general security and architecture guidance applies, but every version-sensitive API must be verified against the installed core and theme/plugin source before use.

Official tagDiv documentation is linked inside each guide. Treat forum replies as secondary; prefer the documentation pages and the exact source version committed in this repository.
