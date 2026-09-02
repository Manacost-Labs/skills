---
name: deckview-pillow-renderer
description: Maintain Deckview's Pillow and NumPy image renderer. Use for every image layout, alpha composition, resize, crop, typography, JPEG encoding, card alignment, mana-curve, class-art, parchment, classic, or custom-background change under image_creator/.
---

# Deckview Pillow Renderer

Preserve the visual contract before optimizing implementation details.

## Workflow

1. Trace the full render path from deck payload to encoded JPEG. Reuse existing layout and image helpers instead of adding parallel composition logic.
2. Keep image operations off Telegram's event loop. Reuse decoded/prepared assets and do not re-open a source once per card copy.
3. Normalize every card into a fixed transparent cell while preserving aspect ratio. Align cells to the same baseline and use deterministic row/column coordinates.
4. Treat alpha as straight RGBA unless an API explicitly documents premultiplication. Verify masks, transparent pixels, and integer rounding against the existing output.
5. Validate all dimensions before allocation and enforce `MAX_OUTPUT_SIDE` before encoding.
6. Preserve source colour for user backgrounds. Apply parchment tint only to the parchment style.
7. Add a focused test, then use `$deckview-visual-regression` for any visible change and `$deckview-render-benchmark` before claiming a speedup.

## Acceptance

- No card is stretched to fill its cell.
- Grid baselines and gaps are exact and repeatable.
- Sideboards and LOCATION cards do not change neighbouring geometry.
- Custom backgrounds retain their colour and transparency behavior.
- JPEG size and render time are recorded when they materially change.
