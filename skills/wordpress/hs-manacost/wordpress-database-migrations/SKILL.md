---
name: wordpress-database-migrations
description: Design, test, execute, verify, and roll back safe WordPress data migrations for hs-manacost.ru. Use for changes to posts, postmeta, options, attachment metadata, URLs/domains, custom tables, capabilities, cron state, serialized data, bulk editorial content, or schema/data contracts across staging and production.
---

# WordPress Database Migrations

Treat WordPress data as production state, not source code. Make every migration bounded, resumable, observable and reversible.

## Required context

1. Use `hs-manacost-project`, `wp-wpcli-and-ops` and the relevant plugin/editor skill.
2. Read [migration-contract.md](references/migration-contract.md) before implementation.
3. Read [verification.md](references/verification.md) before approving a run.
4. Inspect `config/wordpress-contracts.json`; regenerate it when a contract changes.

## Workflow

1. Define the exact rows/objects in scope, invariant after migration and explicit exclusions.
2. Produce a read-only count and representative redacted sample. Never dump personal data into logs or prompts.
3. Detect serialized values, multisite prefixes, attachment relationships, revisions and plugin-owned data before selecting a tool.
4. Implement the migration as versioned source with dry-run, batch limit, checkpoint/resume, idempotence and structured counts.
5. Write tests for no-op, repeated run, partial failure, malformed value and rollback behavior.
6. Take a fresh verified database backup. For media-linked changes, also protect the exact S3 objects and local files.
7. Run against the isolated integration database, then a disposable restore or the isolated `test.hs-manacost.ru` staging copy.
8. Compare before/after counts and application flows. Verify editor save/autosave/revision when post content or metadata changes.
9. Schedule production with a precise command, operator, expected duration, resource limits and rollback threshold.
10. Run bounded batches, stop on invariant failure, verify the application and retain the audit record.

## WordPress-specific rules

- Use WordPress APIs or WP-CLI commands that understand serialized data; do not use blind SQL string replacement.
- Preserve unknown keys in serialized arrays and plugin-owned option structures.
- Keep revisions and attachment relationships unless deletion is explicitly part of the approved scope.
- Use prepared SQL for any custom query and validate table prefixes instead of assuming `wp_`.
- Do not autoload large migration state. Keep checkpoints compact and remove them only after verified completion.
- Keep `.ru` canonical; `.com` must remain a noindex mirror and staging must remain noindex.

## Hard stops

- No production write without a successful restore-tested backup and dry-run counts.
- No unbounded update/delete, direct production import, broad `search-replace --all-tables`, or replacement inside GUIDs without a documented requirement.
- No destructive test against the live database.
- Stop when affected counts differ materially from the approved estimate, data shape is unknown, disk space is unsafe, or rollback cannot be executed.
- Never commit dumps, credentials, salts, user data or generated migration output containing content.

## Completion evidence

Report migration version, dry-run and applied counts, batch/checkpoint state, backup and restore-test identity, invariant checks, affected contracts, staging/application results, production state, commit/PR and rollback command.
