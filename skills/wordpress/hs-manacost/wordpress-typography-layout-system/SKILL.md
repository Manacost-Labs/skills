---
name: wordpress-typography-layout-system
description: Define, implement, audit, and test the typography, font loading, containers, grids, spacing, and vertical rhythm of hs-manacost.ru WordPress and Newspaper/tagDiv interfaces. Use for font or text changes, redesigns, headings, article readability, layout width, columns, gaps, alignment, responsive spacing, CLS, or visual consistency.
---

# WordPress Typography and Layout System

Create one coherent visual system for long-form Russian editorial content, not a collection of page-specific values. Pair this skill with `hs-manacost-project`, `newspaper-tagdiv`, `wordpress-responsive-experience`, `wordpress-accessibility`, `wordpress-redesign-system`, `playwright`, and `web-perf` when relevant.

## Required workflow

1. Audit computed styles on anonymous production-like pages and authenticated/editor surfaces. Inspect runtime additions, especially the anonymous homepage style tagged `manacost-font-trim`; do not assume Newspaper or wp-admin settings are the final font source.
2. Inventory semantic type roles, font families and weights, line heights, container widths, article measure, columns, gaps, spacing, alignment, icons, ads, embeds, and component states. Use real long Cyrillic titles and body copy.
3. Read the focused references for the surface being changed, then create or update a redacted contract based on `config/typography-layout-contract.json`. Validate it:

```bash
python3 .agents/skills/wordpress-typography-layout-system/scripts/validate_visual_system.py config/typography-layout-contract.json
```

4. Assign each value to a semantic role and a supported owner. Prefer Newspaper Website Manager/Composer or Cloud Template settings when stable; otherwise use a scoped first-party MU plugin or child theme. Follow [references/newspaper-ownership.md](references/newspaper-ownership.md).
5. Implement shared tokens before page exceptions. Keep the spacing scale, type scale, line-height policy, grid, and containers from the contract; document any deliberate exception next to its user need.
6. Validate font files, license, Cyrillic coverage, fallbacks, `font-display`, weight budget, preload scope, and computed rendering using [references/font-loading.md](references/font-loading.md) and [references/cyrillic-quality.md](references/cyrillic-quality.md).
7. Test the required responsive widths and 200% zoom. Inspect visual rhythm, wrapping, article readability, truncation, alignment, overflow, font swap, layout shifts, and long/short/empty states.
8. Measure CLS and font payload before and after. Review visual diffs rather than automatically accepting new baselines.
9. Verify the `.ru` canonical, `.com` noindex mirror, and noindex staging remain behaviorally consistent. Release only the exact staging-tested commit.

## System rules

- Use semantic roles from [references/typography-roles.md](references/typography-roles.md), not selectors as the design vocabulary.
- Preserve a readable article measure and deliberate editorial hierarchy; do not make every heading large or bold.
- Use the approved spacing scale and vertical rhythm in [references/spacing-vertical-rhythm.md](references/spacing-vertical-rhythm.md).
- Respect the Newspaper container grid in [references/container-grid-system.md](references/container-grid-system.md); do not compensate for one breakpoint with arbitrary negative margins.
- Use system fonts or licensed local assets with proven Cyrillic coverage. External remote fonts require explicit approval and privacy/performance review.
- Preload only a font used immediately above the fold. Avoid synthetic weights and duplicate formats.
- Keep font fallback metrics close enough to avoid visible CLS; reserve media and ad geometry independently.
- Avoid global `!important`. If an existing runtime override makes it necessary, narrow the selector and document why the owner cannot be changed.

## Hard stops

- Do not edit Newspaper parent/theme vendor files, generated CSS, cache, minified output, or uploaded font files as source.
- Do not introduce an unlicensed font, missing Cyrillic glyphs, arbitrary one-off spacing, or a second competing token system.
- Do not approve a type change from a design screenshot alone; verify computed styles and real browser font loading.
- Do not hide overflow globally or reduce zoom to conceal a broken grid.
- Do not update visual baselines until every intended difference has been inspected.

## Evidence required

- Valid visual-system contract and ownership map.
- Computed-style evidence for anonymous and authenticated surfaces, including `manacost-font-trim` review.
- Cyrillic specimen, fallback/font-loading evidence, payload and CLS comparison.
- Screenshots at 320, 390, 768, 1024, and 1440 px plus 200% zoom.
- Article, homepage, category, editor/admin, ad, embed, slow-image, missing-image, and long-title results.
- Staging smoke evidence and rollback source/template assignment.

Use [references/acceptance-matrix.md](references/acceptance-matrix.md) as the final gate.
