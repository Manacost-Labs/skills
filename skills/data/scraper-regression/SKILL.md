---
name: scraper-regression
description: Detect and explain scraper breakage caused by a site changing — lost fields, moved JSON paths, SSR turning into CSR, extractor source drift, coverage drops between runs. Use when a parser that used to work now returns fewer or emptier records, after a site redesign, when a field suddenly becomes null, when comparing a saved fixture against the live page, or to gate CI on "did the site change under us". Also trigger on Russian requests such as "парсер сломался", "сайт изменился", "поля стали пустыми", "почему упало покрытие".
---

# Scraper regression

A scraper rarely fails loudly. It keeps returning `200 OK` while the data quietly
moves, and coverage drops before anyone notices. This skill answers one question:
**given the response recorded when the profile worked, what is different now, and
does it explain the drop?**

Do not eyeball two HTML files. Run the detector — it compares the same three
layers every time and produces a machine-checkable verdict.

## Run it

```bash
# One saved fixture vs the live page (uses the profile's extractors and fields):
ws-regress --fixture tests/fixtures/success --profile profiles/example.yaml

# Every fixture in a directory (batch, e.g. nightly):
ws-regress --fixtures-dir tests/fixtures --profile profiles/example.yaml --json

# Fully offline: two saved bodies:
ws-regress --baseline old.html --current new.html --url https://site/page \
           --profile profiles/example.yaml
```

Exit code is **1 on a critical regression**, so it gates CI directly.

## What it compares

| Layer | Signals |
|---|---|
| Response | verdict (`OK` → `SOFT_BLOCK`…), HTTP status, rendering class, canonical URL |
| Structure | JSON-LD `@type` lost, embedded app state gone, declared feed gone, **JSON path lost + suggested replacement** |
| Extraction | field lost / gained / value changed, and **source drift** (a field that came from JSON-LD now coming from a CSS selector) |

## Reading the result

- **critical** — data we used to collect is gone: a tracked field is unextractable,
  a JSON path disappeared, SSR became CSR, or the verdict regressed from `OK`.
  The profile needs a fix before the next production run.
- **warning** — the value still arrives but the ground moved: source drift, a
  canonical change, a changed value. Source drift is an early warning that the
  stable source was removed and only the fragile selector is left.
- **none** — nothing actionable changed.

`json_path_lost` carries a `replacement_hint`: a current path whose leaf key
matches the lost one. When the hint is present, the data usually moved rather
than disappeared, and the fix is a one-line profile edit
(`$data.players[].name` → `$pageProps.players[].name`).

## Then what

1. **Critical, with a replacement hint** — update the profile's extractor path or
   selector, re-run `ws-regress`, then refresh the fixture from the new response.
2. **Critical, rendering became CSR** — the HTML route stopped carrying data. Run
   browser reconnaissance (`ws-probe --browser`) to find the JSON API the page now
   uses, and move the route to L0. Do not answer this with a paid provider.
3. **Critical, verdict regressed to a block** — this is a *fetching* problem, not
   a profile problem: hand it to the `scraper-debugger` skill instead.
4. **Warning, source drift** — schedule a profile fix. Falling back to CSS means
   the next redesign will break it outright.

## Rules

- A regression is never a reason to escalate to a paid provider. Paid levels
  answer proven blocking (`BLOCKED`/`SOFT_BLOCK`), never a changed selector.
- Refresh the baseline fixture only after the new response has been validated —
  otherwise a broken page silently becomes the new "correct" baseline.
- Keep fixtures redacted: they are stored responses and must never carry cookies,
  tokens, or query-string secrets.
