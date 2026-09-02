---
name: wordpress-editorial-publish-gate
description: Run the hs-manacost.ru pre-publication gate for WordPress articles and landing pages, including stored content, preview, links, images and S3, shortcodes, SEO, advertising, analytics, accessibility, mobile rendering, cache behavior, and rollback evidence. Use before publishing, scheduling, republishing, or approving editorial material on test.hs-manacost.ru or production.
---

# WordPress Editorial Publish Gate

Require one compact evidence bundle before an editorial release. Pair this skill with `hs-manacost-project`, `wordpress-article-editor`, `wordpress-content-integrity`, `wordpress-media-integrity`, `wordpress-seo-editorial`, and the specialist skill for every changed surface.

## Workflow

1. Identify the post ID, content type, author, target host, intended state, canonical URL, primary category, representative image, ad slots, and rollback revision.
2. Use staging for any active action. Verify draft save, autosave, revision restore, preview, schedule/publish transition, and unchanged `post_content` after a no-op save.
3. Inspect stored values and the rendered preview. Check links, shortcodes, embeds, captions, image dimensions/MIME/alt text, responsive variants, and S3 object availability.
4. Apply the host contract: `.ru` is canonical/indexable, `.com` is a functional `noindex, follow` mirror with `.ru` canonical, and staging is fully noindex.
5. Verify keyboard/mobile presentation, the current banner, staging analytics suppression, and targeted cache invalidation. Never create production views, paid clicks, or analytics events for a gate.
6. Record every check in a gate manifest following [references/gate-matrix.md](references/gate-matrix.md). Run the deterministic evaluator:

```bash
python3 .agents/skills/wordpress-editorial-publish-gate/scripts/evaluate_publish_gate.py evidence.json
```

7. Publish only when every blocking check is `pass`. A `not_applicable` result must include a reason. Preserve the evidence and rollback revision in the PR or release handoff without personal data or secrets.

Read [references/evidence-contract.md](references/evidence-contract.md) when building the manifest or deciding whether evidence is sufficient.

## Result states

- `READY`: every blocking check passed and rollback evidence exists.
- `BLOCKED`: a required check failed, is missing, or lacks evidence.
- `READY_WITH_NOTES`: only non-blocking observations remain; do not use this state to waive a required check.

## Hard stops

- Do not publish from an unverified preview or from cached HTML alone.
- Do not accept screenshots as proof of stored content, S3 integrity, canonical output, analytics request count, or cache correctness.
- Do not replace original media, rewrite production data, purge all caches, or publish a disposable test article on production.
- Do not weaken `.com` or staging noindex policy to make a check pass.
