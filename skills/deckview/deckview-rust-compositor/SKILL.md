---
name: deckview-rust-compositor
description: Implement or review Deckview's native Rust image compositor. Use for every change under rust/deckview_core/, including resizing, masks, alpha blending, text, allocation, thread pools, image decoding, caching, and native output.
---

# Deckview Rust Compositor

Apply the Deckview render contract and Rust FFI safety together.

## Safety and correctness

- Do not use `unwrap` or `expect` on Python input, files, decoded images, fonts, dimensions, or allocations.
- Do not allow a panic to cross FFI. Convert failures into typed Python exceptions at the boundary.
- Validate integer ranges, multiplication/overflow, maximum card count, paths, and canvas dimensions before allocation.
- Accept only validated Deckview asset/card paths; reject arbitrary traversal and unexpected file types.
- Preserve aspect ratio and fixed-cell baselines. Match Python straight-alpha composition and rounding.
- Bound Rayon threads per worker and native cache memory. Four workers must not each consume the whole CPU.
- Use `$deckview-render-contract`, `$deckview-pyo3-boundary`, `$deckview-render-benchmark`, and `$deckview-visual-regression` for payload, FFI, performance, and pixel changes.

## Required commands

Run from `rust/deckview_core`:

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo build --release
maturin build --release
```

Then run a Python import smoke test and strict Pillow/Rust visual parity test. A release build is not production activation.
