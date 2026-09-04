# Gate B REVIEW BRIEF — Graph Portal

Date: 2026-09-04
Baseline: `60a57c0` on `feat/central-skills-catalog`
Scope: `ops/graph-portal/*` graph UI/export/build/publish assets, the scoped
`ops/nginx/graph.kolodahearthstone.com.conf`, related graph tests, and
`docs/operations/graph-ui-plan.md` only.
Review mode: read-only independent micro-review; no commit, push, deploy, or
changes to concurrent policy/release/authentication paths.

## Context

Gate A’s Luna brief identified the iframe limitation, loss of raw graph data on
each build, the real scale (about 39k nodes and 80k edges), and the need for a
sanitized AST projection with a finite canvas cap. The reviewed release has 11
repositories, 3,144 files, 38,401 symbols, and 77,622 aggregate symbol
relations (`stats.links`); its aggregate public file graph has 5,565 edges.
The approved scope is source code, not OS services. SQL extraction is omitted
because `tree_sitter_sql` is unavailable on the host.

## Strengths

- The iframe/Mermaid surface is replaced with a dependency-free canvas UI and a
  bounded deterministic worker layout. The UI supports repository selection,
  file/symbol views, zoom/pan/pinch, search, URL selection, node inspection,
  neighbors, and a mobile layout.
- The exporter keeps source text and raw extraction context private, rejects
  traversal/absolute/sensitive paths, namespaces per-repository IDs, collapses
  file edges without self-links, and does not invent cross-repository edges.
- The publisher has an exact public-asset allowlist, immutable release names,
  manifest/map consistency checks, symlink rejection, and nginx validation.
- DOM-facing labels use `textContent`/created elements rather than HTML sinks.
  The nginx change removes CDN/eval script policy, permits same-origin workers,
  denies child frames, and adds the required module MIME mapping.
- Layout transitions clear stale positions and use a per-layout version plus a
  captured worker reference, so stale worker messages cannot overwrite a new
  file/symbol view.
- Focused Python, Node, shell, and offline Chromium checks pass. The actual
  rebuilt release passed the offline Chromium desktop/mobile flow for all 11
  repositories in both file and symbol modes, including inspection, with no
  console errors. Public-schema validation also passes.

## REVIEW BRIEF

### Resolved during review

- The previously reproduced file-to-symbol transition race is resolved in
  `ops/graph-portal/app.js:176-259`: `positions` and hover state are cleared
  before re-indexing, and both worker handlers require the repository ticket and
  layout version while operating on the captured worker. All-repository actual
  data browser coverage passed after this fix.

### Resolved during follow-up review

1. **Reload failure rollback is now failure-safe.** In
   `ops/graph-portal/publish-graph-portal.sh`, `current` is switched
   only after `nginx -t`; a failed reload restores the previous symlink and
   performs a checked recovery validation/reload. The new sandboxed publication
   tests cover reload failure/recovery and validation failure without touching
   production.

2. **Privileged release copying is now integrity-checked.** The publisher
   fingerprints the exact source file set before validation, copies into a new
   root-owned immutable destination with fixed modes, reruns full release
   validation there, and verifies the copied SHA-256 contents before activation.
   The tampered-copy regression fails closed, and repeated publication of the
   same release is rejected.

## Test gaps and residual risk

- The browser harness fulfills requests locally, including actual release JSON;
  it does not exercise live HTTPS, nginx routing, response MIME, CSP, HSTS, or
  the production symlink. Run a safe read-only HTTP/header smoke test after the
  nginx config is installed and before publication.
- Current tests cover actual all-repository transitions and inspection, plus
  reload failure/recovery, validation failure, copied-file tampering, and
  immutable destination behavior. They do not serialize two simultaneous
  publishers competing for the fixed `current.next` link; keep publication
  single-flight operationally.
- The UI intentionally uses `style-src 'unsafe-inline'` for a CSS custom
  property. No inline script or eval dependency was found; moving cluster color
  state to classes would allow a tighter style policy later.
- There is no metrics export or runtime telemetry by design. Operational
  visibility is nginx access/error logging plus the health endpoint.

## Verdict

**APPROVED for production publication from this Gate B review.** The layout,
rollback, and privileged-copy findings are resolved; focused tests, all-11
actual-release browser flows under the nginx CSP fixture, and public-schema
validation pass with no console errors. Publication remains subject to the
operator's final read-only HTTPS/header smoke check and normal deployment
authority. No production state, commit, or push was changed by this review.
