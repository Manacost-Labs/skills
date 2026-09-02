---
name: deckview-render-cache
description: Safely change Deckview prepared-card, memory card-cell, final render, or Telegram file_id caches. Use for image_creator/prepared_card_cache.py, renderer caches, cache keys, invalidation, pruning, atomic files, corruption recovery, or cache performance.
---

# Deckview Render Cache

Make cache correctness part of the render contract.

## Required invariants

- Include source revision and renderer/contract version in every derived-image key.
- Version the `.rgba` format. Do not change it without a new version plus migration or safe fallback.
- Include all pixel-affecting style, layout, font, background, art, output, and source fields in final-render keys.
- Validate cached raw RGBA dimensions and byte length before use.
- Treat corruption as a miss; never let a broken entry fail rendering.
- Write to a same-filesystem temporary file, flush, and atomically replace the destination.
- Coordinate workers so two writers cannot expose a partial file.
- On a hit, do not decode or prepare the source again.
- Prune only closed, old entries and never delete the file just produced.
- Bound memory caches and expose hit/miss/corruption/eviction telemetry.

## Verification

Cover source-revision invalidation, corrupt-cache fallback, signed offsets, pruning, concurrent writers, RGBA-size validation, and repeated-decoding prevention. Run `$deckview-render-benchmark` for latency claims and `$deckview-visual-regression` for cached/uncached parity.
