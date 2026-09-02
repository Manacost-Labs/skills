---
name: wordpress-release-manager
description: Plan, gate, deploy, verify, promote, and roll back hs-manacost WordPress releases across GitHub, isolated CI, test.hs-manacost.ru, hs-manacost.ru, hs-manacost.com, origin, Cloudflare, and Moscow/Novosibirsk proxies. Use for pull requests, staging deployments, production promotions, configuration releases, hotfixes, plugin/theme updates, and release readiness decisions.
---

# WordPress Release Manager

Promote only the exact commit proven on staging. Make release state understandable and rollback executable before production changes.

## Required context

1. Use `hs-manacost-project`, `agent-ci-cd-and-automation`, `agent-shipping-and-launch` and the specialist skill for the changed subsystem.
2. Read [release-gates.md](references/release-gates.md) to select mandatory checks.
3. Read [rollback.md](references/rollback.md) before requesting production promotion.

## Release workflow

1. Confirm a clean source tree and create a short branch from current `main`.
2. State affected domains, users, data/cache/SEO/security impact and acceptance evidence.
3. Add or update the smallest regression check before implementation.
4. Keep code, data migration, proxy/DNS configuration and dependency update as separate reviewable changes when their rollback differs.
5. Run `make check`, security validation and specialist gates such as `make integration` or `make visual`.
6. Commit and push an atomic change, open a PR and require green GitHub checks.
7. Merge to `main`; allow the pipeline to deploy the resulting exact SHA only to `test.hs-manacost.ru`.
8. Verify staging user flows, noindex, editor/admin behavior and task-specific evidence.
9. Promote production only through `Promote production`, explicitly naming the staging-verified commit SHA and only with user authorization.
10. Verify `.ru`, `.com`, origin, Moscow and Novosibirsk after promotion. Record deployed SHA and observation result.

## Plugin/theme releases

- Update one regular plugin per change and produce a compatibility report.
- Newspaper/tagDiv and commercial plugins remain manual-only and require integration plus visual regression review.
- Never enable production auto-update for commercial plugins or Newspaper.
- Preserve active plugin inventory, licenses outside Git and a source/runtime rollback copy.

## Hard stops

- Never deploy a dirty tree, unreviewed runtime copy, failed CI commit or SHA different from staging.
- Never make production the first test environment.
- Never combine a risky data migration with an unrelated code release.
- Never bypass backup/restore gates for DB, media or destructive changes.
- Never promote when canonical/noindex, images, article body, editor, views, cache or any proxy differs from expected behavior.
- An emergency hotfix still requires explicit authority, narrow scope, rollback and immediate source backport.

## Completion evidence

Report PR and commit SHA, check URLs/results, staging deployment and smoke evidence, exact production workflow run if authorized, affected cache/data/SEO/security, regional verification and rollback target. Explicitly state when production was not changed.
