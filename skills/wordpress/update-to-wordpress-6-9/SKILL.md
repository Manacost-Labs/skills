---
name: update-to-wordpress-6-9
description: Audit a codebase for WordPress 6.9 upgrade risks using focused, release-specific notes.
---

# Update to WordPress 6.9

Use this skill when a user needs an upgrade audit, migration plan, or compatibility review for WordPress 6.9.

## Source provenance

- These release notes are derived from official WordPress Core dev notes and field guides published on `make.wordpress.org/core`.
- Thank the WordPress contributors and writers for the original release writeups these upgrade notes are built on.
- Treat source URLs as required evidence for every finding; if a finding has no source, mark it incomplete instead of presenting it as settled.

## Workflow

1. Determine project scope first:
   - Plugin repository
   - Theme repository
   - Whole-site/custom stack
2. If scope is unclear, ask one targeted question.
3. Detect whether block editor/Gutenberg features are used.
4. Inspect repository structure before deep analysis:
   - Local WP environment files (for example: `docker-compose.yml`, `.wp-env.json`, `wp-env.json`)
   - Dependency management files (for example: `composer.json`, lockfiles)
5. If local WP environment tooling exists, include required version bump steps for WordPress 6.9.
6. If WordPress is managed via Composer, include required `composer.json` and lockfile update steps.
7. Use the release-note files shipped with this skill.
   - Release notes live in `./release-notes/` (relative to this `SKILL.md`), not in the user's project repo.
   - When referencing or reading a note, treat paths as relative to this `SKILL.md`.
8. Expand to additional files only when findings require it.
9. Produce one primary output: upgrade checklist, TODO list, issue list, or patch recommendations.

## Subagent strategy

- Use subagents (or parallelized area reviews) for independent workstreams when supported.
- Good split examples: `core-api` + `admin` + `database` in parallel for backend-heavy repos, or `frontend` + `editor` + `performance` for theme/UI-heavy repos.
- Keep one coordinator pass to merge duplicate findings, normalize severity, and remove overlap.
- Preserve per-area evidence links so each finding remains traceable to release notes and sources.

## Progressive disclosure routing

- Read first for all audits: `./release-notes/breaking-changes.md`, `./release-notes/deprecated.md`
- If plugin-heavy backend code: `./release-notes/core-api.md`, `./release-notes/admin.md`, `./release-notes/tooling.md`
- If theme/rendering focus: `./release-notes/frontend.md`, `./release-notes/editor.md`, `./release-notes/performance.md`
- If schema/query/storage touched: `./release-notes/database.md`
- Only read remaining files inside `./release-notes/` when the repo indicates impact.

## Evidence and uncertainty handling

- Keep recommendations tied to evidence from code and release-note items.
- If details are unclear or conflicting, look for related WordPress Core GitHub issues and Trac tickets. Then check official WordPress documentation.
- Include those external references when they materially support a recommendation.

## Execution mode

- For research/plan mode: focus on checklists, impact analysis, risk ranking, migration sequencing, and test plan.
- For implementation mode: provide concrete code-level patch recommendations and verification steps.
- When running in GitHub PR automation, use subagent findings to produce PR-ready issue/checklist/patch summaries suitable for a PR description or review comment.

## Output requirements

- Keep findings actionable and code-searchable.
- Prioritize breaking changes and deprecations.
- Reference release-note file paths for each finding.
- Include source URLs from the release-note entries for every finding.
- Preserve and cite relevant Trac/GitHub ticket links when present.
- Suggest concrete patches or tests where possible.

_Generated: 2026-03-18_
