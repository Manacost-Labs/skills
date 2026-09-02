---
name: wordpress-article-editor
description: Safely build, change, debug, and review the kolodahearthstone.com article editing experience. Use for Classic Editor, TinyMCE, Gutenberg, editor meta boxes and sidebars, autosave and revisions, article media, S3 uploads, editorial shortcodes, preview and publish flows, or changes to hs-editor-workspace and its integrations.
---

# WordPress Article Editor

Change the editorial workspace without losing drafts, silently rewriting article markup, or breaking the published result. Treat Classic Editor, TinyMCE, optional Gutenberg compatibility, Blocksy, metadata, media and custom editorial plugins as one workflow.

## Project invariants

- Work only in `/srv/projects/wordpress/kolodahearthstone.com`; use Git and deploy to staging before production.
- Target WordPress 6.9.7 and the committed plugin/theme versions. Verify version-sensitive APIs against source.
- Classic Editor and TinyMCE are the current primary writing path. Keep Gutenberg compatibility where the affected post type or extension supports it.
- Preserve autosave, revision history, preview, status transitions, scheduled publishing and the exact stored `post_content` unless an explicit migration is requested.
- Preserve Blocksy/Blocksy rendering, S3 media offload, unique filenames, article views, advertisements and cache invalidation.
- Use `wordpress-admin-ui` for every editor interface change. Also use `blocksy-theme` when Blocksy, Blocksy Composer, Cloud Templates, theme CSS, blocks or modules are involved.

## Required workflow

1. Identify the affected screen, post type, editor mode, roles, rollout rules and save path. Inspect `hs-editor-workspace`, relevant regular/MU-plugins and loaded hooks before editing.
2. Reproduce the complete baseline: open an existing draft, edit, autosave, save draft, preview, restore a revision and publish or update. Record the stored markup and metadata that must remain stable.
3. Read the relevant guide:
   - Installed editor components and ownership: [editor-stack.md](references/editor-stack.md)
   - Supported Classic Editor, TinyMCE and Gutenberg extension points: [extensions.md](references/extensions.md)
   - Article markup, shortcode and S3/media safety: [media-content.md](references/media-content.md)
   - Cross-plugin compatibility and scope: [compatibility.md](references/compatibility.md)
   - Editorial regression matrix: [testing.md](references/testing.md)
4. Choose the smallest public extension point. Prefer a scoped MU-plugin or site plugin over parent-theme, Blocksy or vendor edits.
5. Add a failing regression test or a reproducible browser scenario before behavioral code. Capture desktop and mobile baselines for visual changes.
6. Implement with capability checks, purpose-specific nonces, typed validation, late escaping and assets restricted to the owned editor screen.
7. Verify both the saved database representation and frontend result. Never infer content integrity from the editor preview alone.
8. Run `make check`, the security check, staging deployment and the relevant staging browser flows. Promote only the exact tested commit.

## Data integrity rules

- Never disable autosave or revisions to simplify a feature or hide a conflict.
- Never run blind search/replace over `post_content`, serialized metadata or Blocksy data. Any migration needs a backup, dry run, counted diff, rollback and post-migration validation.
- Preserve registered shortcode names, attributes, inner content and intentional HTML. Unknown shortcodes must round-trip unchanged.
- Do not normalize whitespace or HTML across an entire article merely because TinyMCE and Gutenberg serialize differently.
- Use WordPress attachment APIs for uploads. Keep attachment metadata, alt text, captions, parent relation, generated sizes, unique filenames and S3 object mapping consistent.
- An image upload is not complete until the attachment saves, the S3 URL works anonymously, editor preview works and the published image works through the production proxy paths.
- Keep destructive actions explicit and recoverable. Do not remove a legacy editor control until existing content using it has been inventoried.

## Extension rules

- For Classic Editor/TinyMCE buttons, extend the existing toolbar and editor APIs; do not patch TinyMCE files or replace the editor instance.
- For Gutenberg, use public block-editor packages and plugin slots such as a document settings panel; do not depend on undocumented DOM structure.
- Save handlers must ignore autosaves and revisions when appropriate, verify the current post and capability, and avoid recursive `save_post` updates.
- Keep PHP rendering authoritative for shortcodes and previews. JavaScript enhancements must fail without losing the text being edited.
- Respect the existing limited rollout in `hs-editor-workspace`; widening it to more users or post types is a separate behavior change that needs explicit approval and tests.
- Keep AIOSEO, WP Rocket, tooltip, separator, inline-deck and spoiler controls available when their owning plugins are active. Avoid duplicate panels and duplicate toolbar buttons.

## Hard stops

- Do not edit production content or production runtime as the first test.
- Do not modify the parent Blocksy theme or `td-*` plugins before exhausting supported extension points and running the Blocksy audit.
- Do not expose unpublished text, media or metadata through REST/AJAX without a server-side capability check.
- Do not globally dequeue admin scripts or styles to fix one slow editor screen.
- Do not ship if text disappears after mode switching, save creates malformed markup, preview differs materially from frontend, media is inaccessible, or revisions cannot restore the prior article.

## Completion report

Report which editor modes and roles were tested, the draft/autosave/revision/publish results, content and shortcode integrity, media/S3 result, mobile and keyboard behavior, staging evidence and any compatibility limitation.
