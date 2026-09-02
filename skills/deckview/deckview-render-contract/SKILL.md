---
name: deckview-render-contract
description: Define or change the versioned Deckview renderer payload shared by Python and Rust. Use when adding, removing, renaming, validating, or serializing render fields, assets, cards, layout, output options, schema versions, or renderer versions.
---

# Deckview Render Contract

Replace implicit dictionaries with a documented, versioned boundary.

## Shape

Use this top-level structure:

```json
{
  "schema_version": 1,
  "renderer_version": "...",
  "cards": [],
  "layout": {},
  "assets": {},
  "output": {}
}
```

Keep deck metadata and optional feature groups explicit rather than flattening unrelated values.

## Rules

- Document required fields, optional fields, defaults, enum values, units, and numeric limits.
- Validate card count, dimensions, coordinates, quality, blur, strings, and path roots before rendering or allocation.
- Require an exact supported `schema_version`; return a clear contract error otherwise.
- Include a `renderer_version` in cache keys and telemetry, not as permission to accept an unknown schema.
- Preserve backward compatibility deliberately. Add a translator or bump the schema; never silently reinterpret a field.
- Keep Python validation and Rust deserialization equivalent.
- Add a canonical payload snapshot test and invalid/unsupported-version tests.
- Update both renderers, benchmarks, and cache keys in one change.
