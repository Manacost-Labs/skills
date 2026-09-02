---
name: deckview-pyo3-boundary
description: Maintain Deckview's Python/Rust boundary. Use for PyO3 bindings, Python payload construction, Rust parsing, GIL handling, exception mapping, fallback policy, maturin configuration, wheel packaging, ABI/import behavior, or native renderer activation.
---

# Deckview PyO3 Boundary

Treat Python and Rust as one versioned API.

## Boundary rules

- Cross FFI once per render, not once per card or pixel.
- Release the GIL around decode, resize, composition, text, and encoding.
- Wrap the exported render boundary so Rust panic becomes a controlled Python exception.
- Use a dedicated input/contract exception for invalid payloads; preserve useful context for operational failures.
- Parse a versioned payload through `$deckview-render-contract`; reject unsupported schema versions explicitly.
- Never return references or buffers whose Rust owner can be dropped before Python finishes.
- Production may fall back to Pillow. Tests, CI, and benchmarks must set strict/required mode and fail on unexpected fallback.
- Build and smoke-test the wheel in the supported Python version before delivery.

## Completion gate

Run the Rust commands from `$deckview-rust-compositor`, build with Maturin, import `deckview_core`, verify `renderer_info()`, force the Rust backend for a real render, and assert the reported backend is Rust.
