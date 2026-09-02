---
name: deckview-render-benchmark
description: Benchmark Deckview rendering before claiming Rust, NumPy, Pillow, caching, resizing, encoding, or composition is faster. Use for every renderer performance optimization or latency comparison.
---

# Deckview Render Benchmark

Compare equal work and accept an optimization only when visual output remains acceptable.

## Matrix

Measure cold and warm runs for:

- Pillow legacy;
- Pillow fast/current;
- Rust.

Fail the run when a requested backend silently falls back. Benchmark the same deck payloads, style, assets, output limits, JPEG settings, process state, and machine load.

## Metrics

Record median and tail samples for:

- total render;
- `deck_resolve`, `card_sources`, `art_prepare`, `card_index`, `dust_cost`, and `image_compose` telemetry;
- decode, prepare, compose, and JPEG encode;
- peak RSS and Python allocations where applicable;
- output dimensions and bytes;
- pixel/perceptual difference from the accepted reference.

Separate first-ever source download, cold local cache, warm prepared-card cache, and warm final-render cache. Report regressions as well as wins; do not extrapolate a single total timer into stage conclusions.

Use `scripts/benchmark_render_backends.py` for Python/Rust composition comparisons and store generated artifacts outside Git.
