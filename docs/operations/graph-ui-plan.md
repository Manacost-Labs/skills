# Native graph workspace — 2026-09-04

## Scope and acceptance

Replace the report iframe with a real canvas node-link workspace. The approved
11-repository manifest is the scope of “whole server”, not an inventory of OS
services. File/symbol links come from Graphify AST output; do not infer cross-repo
dependencies. Public data contains relative navigation metadata, never source
text, credentials, raw extraction context, or absolute server paths.

Desktop: repository rail | graph + search/view/zoom controls | node inspector.
Mobile: repository select, graph, collapsible detail sheet. GitHub-inspired dark
neutrals, blue focus, distinct cluster colors; the graph occupies the workspace.
Tokens: background #0d1117, panel #161b22, border #30363d, text #e6edf3,
muted #8b949e, focus #58a6ff. System fonts, 8px spacing rhythm. No decorative
animation. File-level overview first; symbols on demand, bounded drawing with
an explicit displayed count and full-index search. Keyboard-accessible node list.

## Sequential plan

1. RED tests for the sanitized exporter, graph model, and browser interaction.
2. Export compact file/symbol JSON from secret-quarantined Git snapshots. Keep
   raw Graphify output outside the web root, in a private cache. Rebuild serially
   at low priority only when host pressure permits; no application repo edits.
3. Implement native canvas UI and finite worker layout without runtime/CDN
   dependencies. Frontend and exporter have disjoint files; shared contracts and
   publication remain sequential.
4. Focused tests, responsive screenshots, independent Luna review, project and
   staged security gates. Publish a new immutable release, check HTTPS, push.

## Preflight / tools

Profile: server. Canonical using-agent-skills, planning-and-task-breakdown,
context-engineering, graphify-server-map, test-driven-development,
frontend-ui-engineering, performance-optimization, git-workflow-and-versioning,
ci-cd-and-automation plus frontend-design guide the implementation.

Gate A: gpt-5.6-luna completed read-only (Franklin the 2nd). Its brief validated
the iframe limitation, missing persisted public graph data, and need for bounded
canvas rendering. Correction: manifest has 11 repositories, not 10.

Baseline HEAD 60a57c0, feat/central-skills-catalog. Protected untracked paths:
tests/test_scope_guard.py, tests/__pycache__/. During preflight another session
added docs/engineering-system-plan.md, scripts/scope_guard.py,
tests/test_engineering.py; these are disjoint and also protected. Do not stage
or modify any of them. No .codegraph directory. Recheck status before patches.

MCP: Chrome DevTools rejects local navigation by allowlist; do not use it to
claim live browser coverage. Local synthetic Playwright fixtures can test our
own assets without navigating the protected site. Cloudflare is only needed
for scoped cache invalidation; DNS/auth stay unchanged. Serena is unnecessary
for standalone asset/exporter changes with no semantic refactor. Existing
Graphify CLI provides AST evidence. No new library/API dependency requires
Context7. Public endpoint gets read-only HTTP smoke checks.

## Verification record

- RED: missing public exporter/model and absent native canvas reproduced before
  implementation. GREEN: 3 exporter tests, 4 graph-model tests, native Chromium
  flow. The initial all-repository test then caught a file/symbol transition
  race (`neighbors.size` against stale positions); distinct symbol IDs reproduce
  it in the small fixture. Cleared positions and versioned workers fix it.
- Rebuilt all 11 quarantined Git snapshots serially at nice 19 / idle I/O after
  host memory pressure subsided: 3,144 files, 38,401 symbols, 77,622 symbol
  relations; 5,565 collapsed directed file edges. Cap is 1,800 drawn nodes,
  search covers the active full index. No external LLM or new dependency.
- Offline Chromium uses local route fulfillment, including the actual release
  JSON and the tracked nginx CSP. All 11 repositories, file/symbol transitions,
  inspector, search, neighbors, zoom, keyboard pan, URL/back, error/retry and
  1440×960 / 390×844 viewports pass with zero runtime/console errors. Latest
  full-index overview ready in 0.73 seconds locally; not a live network SLA.
- `make check` and `make test` passed (324 canonical skills). Focused tests
  repeated after changes. Biome, Ruff, ShellCheck, shfmt and diff whitespace
  checks pass. No TypeScript/React/package manifest changes: tsc, ESLint, Knip,
  Vitest and dependency scanners are not applicable to this standalone UI.
- Gitleaks public release (14.14 MB) and staged changes pass; Semgrep scoped
  security audit found no issues. Common `ai-security-check quick` is NOT green:
  five pre-existing matches in repository history stop it before OSV. No secret
  values were printed. No CodeQL database was built; no CodeQL coverage claimed.
- Gate B on gpt-5.6-luna identified publisher reload rollback and mutable-copy
  risks. Fixed with root-owned post-copy validation plus SHA-256 integrity,
  validation before activation, checked rollback/recovery. Four isolated
  publication tests cover success/immutability, failed validation, reload
  failure/recovery and tampered content; no production actions in those tests.
- Unrelated concurrent AGENTS, Makefile, registry, profile, policy, script,
  inventory and non-graph test edits remain protected and outside our staged
  set. App task coordination did not return; no overlapping paths were edited.
  Only the reviewer owns graph-publishing.md / graph-ui-review.md while active.

Delivery: Luna re-review APPROVED both publisher fixes. The previous live nginx
config hash matched the committed baseline before installation; a private
root-owned backup was retained. Published immutable release
`graph-native-20260904-2315` at 23:33 UTC. HTTPS and health return 200; public
JSON confirms 11 repositories / 3,144 files / 38,401 symbols. Module MIME is
application/javascript, CSP is same-origin scripts/workers with no iframe,
and HSTS is present. Cloudflare MCP successfully purged only this portal's 20
asset URLs. GitHub MCP verified the remote branch baseline 60a57c0 before push.
Nginx syntax/reload succeeded with pre-existing global hash-size warnings;
unrelated global tuning was not changed. Previous release remains recoverable.

Only scoped commit and authorized push remain at this checkpoint. SQL remains excluded because the host
has no tree_sitter_sql dependency. No auth/DNS/certificate or application-source
changes are part of this UI redesign.
