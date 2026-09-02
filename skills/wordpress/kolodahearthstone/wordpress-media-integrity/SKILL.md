---
name: wordpress-media-integrity
description: Audit, debug, recover, migrate, and safely change the KolodaHearthstone WordPress image pipeline across uploads, attachment metadata, duplicate filenames, WebP/AVIF sidecars, image optimizers, Nginx negotiation, cache, legacy-domain delivery, staging, and regional proxies. Use for missing, wrong, overwritten, heavy, stale, or regionally unavailable images.
---

# WordPress Media Integrity

Preserve the original attachment and prove every transition from WordPress upload to visitor response. Never optimize by overwriting a source image.

## Start here

1. Use `kolodahearthstone-project`, `wordpress-article-editor` when editor insertion is involved, and `wordpress-runtime-stack` for cache/S3/proxy behavior.
2. Run `scripts/media-pipeline-status.sh` for a non-secret server snapshot.
3. Read [media-pipeline.md](references/media-pipeline.md) before changing optimization or delivery.
4. Read [recovery.md](references/recovery.md) before repairing, replacing or deleting any object.

## Integrity workflow

1. Capture attachment ID, parent post, `_wp_attached_file`, `_wp_attachment_metadata`, visible URL and the exact broken request.
2. Inventory the source, every WordPress size, adjacent `.webp`/`.avif`, legacy `uploads-webpc` variant and S3 object without modifying them.
3. Record byte size, dimensions, MIME, modification time and SHA256 for each available representation. Do not compare only filenames.
4. Verify duplicate uploads with the same filename produce a unique WordPress path; test this in the isolated integration stack.
5. Identify the first mismatch: database metadata, local source, optimized sidecar, S3 copy, Nginx negotiation, cache or HTML reference.
6. Reproduce on `test.kolodahearthstone.com`; keep originals byte-for-byte unchanged and generate candidates atomically.
7. Verify modern and legacy `Accept` requests, `.ru`, `.com`, origin, Moscow and Novosibirsk. Confirm content type, dimensions and checksum of the intended representation.
8. Purge only affected image/article URLs, then repeat cold/warm checks.
9. Run `make integration`, applicable visual tests, `make check`, security check and staging smoke checks.

## Existing optimizer contract

- `/srv/projects/wordpress/hs-local-image-optimizer` owns local compression and must remain an independent source repository.
- It supports JPEG/PNG attachments and writes adjacent WebP/AVIF sidecar files; the source image is never replaced.
- Deck/text graphics use high-quality WebP; transparent UI PNG uses lossless WebP; editorial photos/art may add AVIF.
- A candidate is published atomically only when dimensions match and required savings are achieved.
- Imagify auto-optimization is disabled only for attachments owned by the local pipeline; `uploads-webpc` remains a legacy delivery fallback.
- `hs-manacost-s3-offload.timer` independently verifies/copies uploads and optimized variants to OVH Object Storage every five minutes.
- Do not edit the optimizer repository when it has unrelated uncommitted changes. Coordinate a separate branch and release when its behavior must change.

## Hard stops

- Never overwrite, recompress in place or delete the source image to save space.
- Never use filename equality as proof that two objects contain the same image; use SHA256 plus dimensions/MIME.
- Never delete local media until S3 verification and tested restoration prove every required file/sidecar is recoverable.
- Never regenerate all thumbnails or sidecars on production without a bounded batch, CPU/IO limits and rollback.
- Never change Nginx content negotiation without testing AVIF, WebP and original fallbacks and rotating the relevant cache namespace.
- Never expose S3 credentials, rclone configuration or signed URLs.

## Completion evidence

Report affected attachments/posts, inventory counts, checksum/dimension results, optimizer and offload state, recovered source/version, modern/legacy request results, cache scope, staging/proxy verification, commit/PR and rollback.
