---
name: wordpress-clean-code
description: Enforce clean, secure, maintainable first-party WordPress code in hs-manacost.ru. Use for every PHP, JavaScript, CSS, MU-plugin, hook, REST/AJAX, cron, WP-CLI, theme integration, refactor, review, or static-analysis change; pair with newspaper-tagdiv whenever Newspaper or tagDiv behavior is involved.
---

# WordPress Clean Code

Keep new code simple and verifiable without rewriting legacy, vendor, commercial plugin, or Newspaper parent-theme code as collateral work.

## Required workflow

1. Read the owning source, its callers/hooks, tests, and the relevant WordPress contract before editing.
2. Add a failing behavioral test or reproducible check. Preserve runtime behavior during refactors.
3. Change the smallest first-party extension point. Keep orchestration, validation, persistence, and rendering separable.
4. Treat request, option, meta, REST, AJAX, shortcode, upload, remote response, and LLM data as untrusted.
5. Require capability and nonce checks for browser writes; sanitize and validate input; prepare SQL; escape output for its exact context.
6. Run WPCS, PHPCompatibilityWP, and PHPStan through `make code-quality`. Do not edit generated caches, vendor packages, commercial plugins, or the Newspaper parent theme to satisfy a tool.
7. Review for correctness, clarity, coupling, security, performance, and rollback. Run `make check` and the project security check before commit.

Read [php-wordpress.md](references/php-wordpress.md) for implementation rules. Read [review-gates.md](references/review-gates.md) before committing or when introducing/suppressing analyzer findings.

## Design rules

- Prefer descriptive names, guard clauses, bounded queries, explicit types and one responsibility per function.
- Reuse the canonical project helper instead of creating a near-duplicate.
- Keep hooks thin and move testable behavior into focused functions or classes.
- Scope admin/frontend assets and avoid work on every request when a narrower hook exists.
- Add or update `config/wordpress-contracts.json` through `make contracts` when changing options, post meta, shortcodes, REST/AJAX endpoints, cron hooks, or capabilities.
- Use `newspaper-tagdiv` before any Newspaper, tagDiv Composer, Cloud Template, module, block, Theme API, parent-theme, or theme CSS change.

## Static-analysis policy

- Analyze only first-party code. The current automated scope is `wordpress/mu-plugins`.
- Treat `composer.lock` as part of the security boundary and install with `composer install`.
- Do not add blanket exclusions, broad `ignoreErrors`, disabled rules, or inline suppressions to make a gate green.
- Keep the legacy PHPStan baseline frozen. Fix a touched finding when practical; never baseline a new finding.
- Changed first-party PHP must also pass PHPStan level 7, complexity/nesting limits and the file-growth ratchet. New PHP files over 500 lines and growth of an existing file already over 1,000 lines require decomposition rather than a suppression.
- Run compatibility for PHP 8.2 through 8.4. Verify version-sensitive WordPress APIs against the installed WordPress 6.9.7 source.

## Hard stops

- Do not mix unrelated formatting or refactoring into a behavioral change.
- Do not replace capability checks with nonces or treat a nonce as authorization.
- Do not concatenate untrusted SQL, render unescaped values, or trust file extensions/MIME headers alone.
- Do not patch `wordpress/themes/Newspaper_new` or `td-*` plugin internals as the default solution.
- Do not weaken a quality gate without a narrow documented reason, owner, and removal condition.
