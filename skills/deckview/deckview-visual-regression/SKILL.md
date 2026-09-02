---
name: deckview-visual-regression
description: Verify Deckview rendered-image correctness. Use for every change that can affect pixels, layout, image dimensions, renderer parity, card placement, sideboards, LOCATION cards, backgrounds, styles, class art, mana curve, or JPEG output.
---

# Deckview Visual Regression

Extend the two-Reno gate in `$deckview-maintainer`; do not replace or duplicate it.

## Required matrix

Render representative fixtures covering:

- 30-card Reno and 40-card Reno/XL;
- a sideboard deck and LOCATION cards;
- card frames with different source proportions and transparent artifacts;
- classic, parchment, and custom-background styles;
- both Python and Rust when the Rust path is touched.

Prefer `scripts/render_regression_decks.py` for the mandatory Reno pair. Add targeted fixtures or parity scripts only for cases it does not cover.

## Inspect

Open every required output at full useful detail and check:

1. No missing cards, clipping, overlap, stretch, or unexpected placeholders.
2. Identical card baselines, cell sizes, row gaps, and column gaps.
3. Correct sideboard placement and LOCATION-frame handling.
4. Correct class art, mana curve, title, transparency, and custom background colour.
5. Longest side is at most `MAX_OUTPUT_SIDE`.
6. JPEG byte size did not grow without a measured explanation.
7. Python/Rust differences are measured; optimization is rejected if visual parity is not acceptable.

Record output dimensions, bytes, and paths. Show the 30- and 40-card images to the user when supported.
