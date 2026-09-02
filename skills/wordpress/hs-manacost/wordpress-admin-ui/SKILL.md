---
name: wordpress-admin-ui
description: Design, build, review, and improve secure, fast, accessible WordPress administration interfaces for hs-manacost.ru. Use for wp-admin pages, plugin settings, dashboards, list tables, filters, forms, media fields, notices, bulk actions, modals, editor sidebars, AJAX or REST-backed admin workflows, responsive admin screens, and any request to make an internal interface more convenient or visually professional.
---

# WordPress Admin UI

Build task-focused administration screens that feel native to WordPress and remain usable on a phone. Treat usability, permissions, data integrity, accessibility, and perceived performance as one feature.

## Project invariants

- Work only in `/srv/projects/wordpress/hs-manacost.ru`; never treat `/var/www` as source.
- Target the installed WordPress 6.9.7 APIs and verify version-sensitive behavior against committed or staging core.
- Preserve existing editor workflows, roles, media/S3 behavior, caching, article counters, and Newspaper integrations.
- Use `newspaper-tagdiv` as well when the change touches tagDiv Composer, Newspaper panels, Cloud Templates, theme CSS, blocks, or modules.
- Deploy to `test.hs-manacost.ru` first. Promote only the exact commit that passed staging checks.
- Keep admin assets and CSS scoped to the owned screen. Never restyle global WordPress administration unintentionally.

## Required workflow

1. Discover the current screen, entry hook, data source, user roles, record count, build tooling, and existing UI conventions. Inspect the real interface at desktop and mobile widths before proposing a replacement.
2. Define the operator's primary task in one sentence. Record the shortest successful path, secondary actions, destructive actions, and the required `loading`, `empty`, `error`, success, permission-denied, and partial-data states.
3. Read only the relevant guide:
   - WordPress page/API selection: [architecture.md](references/architecture.md)
   - visual hierarchy and tokens: [design-system.md](references/design-system.md)
   - forms, tables, filters, notices, and mobile patterns: [patterns.md](references/patterns.md)
   - capability, nonce, validation, escaping, uploads, AJAX, and REST: [security.md](references/security.md)
   - browser, accessibility, performance, and release checks: [testing.md](references/testing.md)
   - project pattern contract and live showcase: [../../../docs/admin-ui-pattern-library.md](../../../docs/admin-ui-pattern-library.md), implemented by `hs-admin-ui-patterns`
4. Choose the smallest architecture that supports the workflow. Prefer native WordPress markup and APIs; use an isolated JavaScript application only for interaction-heavy screens and only with an existing supported build pipeline.
5. Add a failing behavioral test or reproducible browser scenario before implementation. For visual changes, capture representative desktop and mobile baselines.
6. Implement the narrowest change. Keep data access separate from rendering, paginate server-side, enqueue assets only on the owned screen, and retain usable HTML for failures where practical.
7. Verify keyboard operation, focus order, labels, screen-reader announcements, 320 px mobile layout, 768/1024/1440 px layouts, slow responses, empty datasets, validation failures, and permission failures.
8. Run `make check`, the project security check, deploy to staging through Git, then perform the relevant browser flow on `test.hs-manacost.ru` before promotion.

## Architecture decision

Use this order:

1. Existing WordPress edit, list, taxonomy, media, or settings screen with a scoped extension.
2. Native submenu under an existing top-level menu for one focused tool or settings page.
3. Dedicated top-level menu only for a multi-screen daily workflow used by several roles.
4. Server-rendered page with small progressive JavaScript enhancements.
5. Isolated React/WordPress-components application only when dense client state, drag-and-drop, or live multi-step interaction justifies it.

Do not add a new framework for a single form, table, toggle, or modal. Do not use private WordPress classes as a long-term public API without isolating the dependency and adding regression coverage.

## Non-negotiable implementation rules

- Check the narrowest applicable `capability` on page access and again inside every write handler.
- Use a purpose-specific `nonce` for state-changing forms, links, AJAX, and REST requests; never treat a nonce as authorization.
- Validate safelisted values before acting, sanitize input by type, use prepared queries, and escape late for the exact output context.
- Provide a `permission_callback` for every REST route and argument schemas for writable fields.
- Use semantic controls: real buttons, links, labels, fieldsets, headings, tables, and dialogs. Support full keyboard operation and visible focus.
- Keep filters and pagination in the URL when users need refresh, back/forward, bookmarking, or sharing.
- Paginate large datasets and request only visible fields. Never load every post, applicant, media item, or log row into the browser.
- Show immediate feedback, but use optimistic updates only for reversible actions with automatic rollback on error.
- Require explicit confirmation for destructive actions and explain the exact target. Never hide deletion behind an icon without an accessible name.
- Avoid horizontal page scrolling at 320 px. Convert dense tables to priority columns plus row details or a deliberate mobile list.
- Use real Russian interface copy for this project; make labels action-oriented, errors actionable, and empty states explain the next step.

## Professional quality bar

- Make the primary action obvious without making every action prominent.
- Reduce navigation and decoration that do not support the current task.
- Use a consistent spacing, typography, radius, and semantic color system; avoid arbitrary values, excessive gradients, shadows, giant headings, and card grids.
- Preserve WordPress admin chrome unless an isolated full-screen workflow is justified.
- Prefer inline validation near the field and retain entered values after errors.
- Make success, saving, stale data, background work, and unsaved changes visible.
- Keep common actions within one tap on mobile and make touch targets at least 44 by 44 CSS pixels when space permits.

## Hard stops

- Do not change production first or test destructive flows with production data.
- Do not expose privileged data through page HTML, localized scripts, REST preload, logs, or client-side permission checks.
- Do not enqueue a framework or global stylesheet across every wp-admin screen.
- Do not replace a familiar native control with a custom control that loses keyboard, focus, or screen-reader behavior.
- Do not ship a blank screen, endless spinner, silent save, lost form input, inaccessible modal, or table that only works on desktop.
- Do not declare an interface complete from screenshots alone; run the actual create, edit, filter, paginate, save, fail, retry, and delete flows.

## Completion report

Report the operator workflow improved, permissions covered, state matrix tested, mobile and keyboard results, performance impact, staging evidence, and any remaining limitation. Separate measured facts from design judgement.
