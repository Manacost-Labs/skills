---
name: wordpress-responsive-experience
description: Design, implement, audit, and test responsive WordPress and Newspaper/tagDiv interfaces for hs-manacost.ru without losing desktop content or behavior. Use for mobile adaptation, breakpoint changes, navigation, cards, articles, ads, embeds, overflow, touch targets, viewport zoom, device-specific rendering, or visual regressions across 320–1440 px.
---

# WordPress Responsive Experience

Preserve functional parity across screen sizes while adapting hierarchy and geometry to the device. Pair this skill with `hs-manacost-project`, `newspaper-tagdiv`, `wordpress-accessibility`, `wordpress-typography-layout-system`, `playwright`, and the performance/SEO skills selected by `config/ai-skills.json`.

## Required workflow

1. Audit the real page before editing. Record its content, actions, navigation, ads, analytics, view counting, embeds, images, states, Newspaper template ownership, server-side mobile branches, cache variants, and longest real Russian content.
2. Read [references/parity-contract.md](references/parity-contract.md) and create or update a redacted contract based on `config/responsive-experience-contract.json`. Validate it:

```bash
python3 .agents/skills/wordpress-responsive-experience/scripts/validate_responsive_contract.py config/responsive-experience-contract.json
```

3. Choose an update-safe ownership layer using [references/newspaper-mobile-surfaces.md](references/newspaper-mobile-surfaces.md). Do not edit the Newspaper parent theme, tagDiv vendor packages, generated CSS, cache, uploads, or minified output as source.
4. Implement the smallest vertical slice. Keep the same information and capabilities; change order, density, grouping, disclosure, and component geometry only when the user task benefits.
5. Exercise the real-content cases in [references/content-test-cases.md](references/content-test-cases.md). Include long Cyrillic titles, missing and slow images, ads, embeds, authenticated admin bar, empty/error/loading states, and touch-only use.
6. Run the viewport matrix at 320, 390, 768, 1024, and 1440 px plus intermediate widths. Test portrait and landscape, keyboard, touch, reduced motion, 200% zoom, browser text enlargement, and back/forward navigation.
7. Inspect every screenshot and overflow report. A horizontal white gutter, clipped control, hidden focus ring, accidental layout jump, or unreachable action fails the change.
8. Verify `hs-manacost.ru`, the functional `hs-manacost.com` noindex mirror, and the fully noindex staging host keep their canonical, analytics, view-count, ad, media, and cache contracts.
9. Release only the exact commit verified on staging. Keep the previous template assignment or source commit as rollback.

## Implementation rules

- Treat desktop and mobile as one product with functional parity, not identical pixels.
- Prefer intrinsic layout, `min()`, `max()`, `clamp()`, grid/flex wrapping, logical properties, and container-aware components over device-name media queries.
- Use breakpoints where content fails, while respecting Newspaper boundaries documented in [references/responsive-patterns.md](references/responsive-patterns.md).
- Keep touch targets at least 44 by 44 CSS px unless a larger native control contains the target.
- Reserve image, ad, embed, and asynchronous module space to prevent CLS.
- Wrap tables, code, deck strings, and third-party embeds locally; never force page-level horizontal scrolling.
- Keep viewport zoom enabled. Do not use `user-scalable=no` or a restrictive `maximum-scale`.
- Do not fork markup by user agent unless the cache key and parity contract are explicit and tested.
- Do not hide content, controls, ads, headings, or navigation merely to make a mobile screenshot cleaner.

## Evidence required

- Valid contract and ownership decision.
- Before/after screenshots at all required widths with real content.
- Automated responsive overflow sweep and inspected visual diffs.
- Keyboard, touch, 200% zoom, landscape, slow/missing image, and authenticated-state results.
- Cold/warm performance and CLS comparison for affected pages.
- Staging smoke evidence and explicit confirmation that production was not changed unless promotion was separately authorized.

Use [references/acceptance-matrix.md](references/acceptance-matrix.md) as the final gate.
