---
name: wordpress-accessibility
description: Design, review, and test accessible WordPress frontend, Blocksy/Blocksy, article editor, and wp-admin interfaces for kolodahearthstone.com. Use for navigation, forms, dialogs, tables, media, keyboard behavior, focus, headings, contrast, zoom, responsive layout, screen-reader names, error states, and WCAG-oriented regression checks on desktop and mobile.
---

# WordPress Accessibility

Treat accessibility as functional behavior, not a visual afterthought. Pair this skill with `kolodahearthstone-project`, `wordpress-admin-ui` or `blocksy-theme`, and `playwright` for browser evidence.

## Workflow

1. Identify the user journey and component states: initial, loading, empty, validation error, success, disabled, modal open/closed and session expiry.
2. Preserve semantic HTML and native controls. Use ARIA only to provide a missing accessible name, relationship, state or live announcement.
3. Follow [references/test-matrix.md](references/test-matrix.md) for keyboard, focus, headings, landmarks, names, errors, contrast, zoom, reduced motion and touch targets.
4. Run the passive HTML auditor for fast structural findings, then test the actual hydrated page with Playwright/axe and manual keyboard use:

```bash
python3 .agents/skills/wordpress-accessibility/scripts/audit_accessibility_html.py saved-page.html
```

5. Test at 320, 768, 1024 and 1440 CSS pixels, 200% zoom, and phone orientation changes. Require no trapped focus, hidden focused controls, clipped actions, horizontal page scroll or white gutters.
6. Test wp-admin with the least privileged supported role. Verify notices are announced, field errors identify the field and resolution, tables have a usable phone representation, and destructive actions require a clear confirmation.
7. Record automated violations, manual keyboard path, viewport/zoom, screenshots and remaining limitations. Automated scans do not replace manual checks.

Read [references/blocksy-admin-patterns.md](references/blocksy-admin-patterns.md) before changing Blocksy navigation, article layouts, Composer blocks, editor panels or admin tables.

## Hard stops

- Do not disable user zoom or use viewport rules that prevent scaling.
- Do not use color, hover, placeholder text, icons, position or animation as the only carrier of meaning.
- Do not add positive `tabindex`, keyboard-only shortcuts without alternatives, or focus removal without a visible replacement.
- Do not accept an axe score alone as proof that the workflow is usable.
