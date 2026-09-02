---
name: wordpress-redesign-system
description: Plan, design, implement, review, and release distinctive production-quality redesigns for kolodahearthstone.com WordPress and Blocksy/Blocksy surfaces. Use for visual direction, information architecture, design systems, tokens, typography, page templates, headers, navigation, article/category/search layouts, responsive behavior, component states, motion, design critique, and staged redesign rollouts on frontend, editor, or wp-admin.
---

# WordPress Redesign System

Create a recognizable Manacost product, not a generic AI template. Pair this skill with `kolodahearthstone-project`, `frontend-design`, `agent-frontend-ui-engineering`, `blocksy-theme`, `wordpress-responsive-experience`, `wordpress-typography-layout-system`, `wordpress-accessibility`, `playwright`, and the performance/SEO skills for affected pages.

## Required workflow

1. Audit the current product before proposing visuals. Capture the actual audience, page jobs, navigation, editorial hierarchy, real Cyrillic content, longest titles, images, ads, embeds, deck widgets, empty/error states, mobile constraints, analytics and SEO contracts.
2. Write a compact problem brief. Separate business goals, reader tasks, editorial tasks and aesthetic preferences. Do not treat “modern” or “clean” as an actionable direction.
3. Propose two or three materially different art directions. For each, provide a thesis, type system, palette, layout logic, signature element, risks and a small wireframe. Reject any direction that could be reused unchanged for an unrelated media site.
4. Obtain approval for one direction before implementing a broad visual change unless the user already selected an explicit direction. Record the decision and rejected alternatives.
5. Create a redacted JSON design contract following [references/design-contract.md](references/design-contract.md), then validate it:

```bash
python3 .agents/skills/wordpress-redesign-system/scripts/validate_redesign_contract.py redesign-contract.json
```

6. Build an inventory of reusable patterns and states using [references/component-system.md](references/component-system.md). Define tokens once; do not scatter raw color, spacing, radius, shadow, type or motion values across selectors. Validate the project responsive and typography/layout contracts before implementing shared geometry or type.
7. Select an update-safe Blocksy ownership layer with [references/blocksy-implementation.md](references/blocksy-implementation.md). Implement one vertical slice at a time on staging: navigation, homepage, article, taxonomy/search, then secondary surfaces.
8. Validate every slice with real content and the [references/acceptance-matrix.md](references/acceptance-matrix.md). Compare screenshots at 320, 390, 768, 1024 and 1440 px; test 200% zoom, keyboard, reduced motion, slow images, missing images, loading, empty, error and authenticated states.
9. Review the result twice: first for task clarity and hierarchy, then for craft. Remove visual noise, inconsistent tokens, accidental novelty, generic card grids and decoration that does not encode content.
10. Release only the exact staging-tested commit. Preserve a source rollback and the previous Cloud Template assignments; never use cache clearing as the rollback plan.

## Design quality bar

- Make the hero and homepage hierarchy reflect Hearthstone editorial work rather than a reusable marketing template.
- Use typography, density and image treatment deliberately for long Russian titles and frequent editorial scanning.
- Spend boldness on one defensible signature element. Keep navigation, reading, search and publishing predictable.
- Treat copy, loading, empty, error and destructive confirmations as part of the design.
- Keep `kolodahearthstone.com` canonical, `kolodahearthstone.ru` a one-hop legacy redirect, `test.kolodahearthstone.com` fully noindex, and analytics disabled on staging.
- Preserve ad slots, view counting, S3 media, shortcodes, comments, embeds, structured data and proxy delivery.

## Evidence required

- Current-state audit and approved direction.
- Validated design contract and component/state inventory.
- Before/after screenshots with real content, not lorem ipsum.
- Keyboard/axe results, zoom/overflow evidence and reduced-motion behavior.
- Cold/warm performance comparison and image/CLS evidence.
- Blocksy strict audit, integration tests, visual regression review and rollback commit/template assignment.

## Hard stops

- Do not begin a broad redesign from a single vague adjective or an unapproved generic mockup.
- Do not edit the Blocksy parent theme, Blocksy vendor packages, generated CSS, minified output, cache or uploads as source.
- Do not update visual baselines merely because a diff exists; inspect and approve each intended difference.
- Do not hide content, controls, ads or focus states to obtain a cleaner screenshot or synthetic performance score.
- Do not disable zoom, use hover-only actions, rely on color alone, or accept horizontal white gutters on mobile.
