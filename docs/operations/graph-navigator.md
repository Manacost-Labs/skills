# Graph navigator v1

## Scope and status

This release adds a deterministic local navigator to the existing Graphify
portal. It searches the reviewed catalog of 11 repositories by normalized
names, aliases, domains, capabilities, and stack terms. Results include the
matched terms (`reasons`) and an ambiguity flag. This is label/token matching,
not LLM semantic search or remote AI. Catalog entries are `unverified` until
their repository ownership and role are confirmed.

The browser uses the reviewed passport labels (including Deckview and OpenBot)
for the sidebar and project cards. It can prepare allowlisted graph metadata,
not source text, with a hard serialized UTF-8 byte limit. The public UI reports
HEAD freshness as unknown; it has no local repository access. The private CLI
can verify Git HEAD from the fixed repository manifest and reports `current`,
`stale`, or `unknown` against the graph snapshot commit.

Existing graphs are immutable snapshots. A stale graph is not refreshed
automatically, and this release does not index, deploy, publish source, add a
service, or call remote AI. Offline preview tests are not production
deployment or live HTTPS/header verification.

## Local CLI

Run from the repository root:

```bash
node ops/graph-portal/navigate.mjs find-project QUERY
node ops/graph-portal/navigate.mjs context QUERY --repo SLUG --max-bytes 8000
```

`find-project` returns ranked projects, reasons, fixed local roots, and entry
points. If a query is ambiguous, pass `--repo SLUG` to `context`; an unknown
project or missing graph fails closed. `context` reads the selected exported
graph under the release directory (override with `--release DIR`) and returns
only project/file metadata, symbol labels and line numbers, plus real one-hop
directed file relationships. It never reads application source text, starts an
HTTP listener, uses the network, or refreshes an index.

The default context ceiling is exactly 8000 serialized UTF-8 bytes, not tokens.
The CLI accepts 512–32000 bytes and returns at most 8 files; the shared function
also accepts a 1–8 file limit. The output marks
`truncated` when the selected metadata cannot fit. Sensitive, absolute,
traversal, and unsafe metadata paths are excluded; always verify the suggested
paths against current source before acting.

## Build and rollout

`build-graph-portal.sh --check` validates the manifest and catalog compatibility
before any indexing. A normal build projects only code-only Graphify metadata;
raw extraction output remains outside the public release. The release
validator accepts the reviewed `projects.json` catalog and rejects extra or
unexpected public assets. No build, index refresh, deployment, or push is
performed by this document or by the reviewer.

Catalog, browser, CLI and publication-contract integration are implemented in
this first release. Later roadmap phases remain separate work: richer typed
relationships and provenance, incremental indexing, an authenticated private
retrieval service/MCP, verified cross-repository links and advanced graph views.
No automatic client/MCP registration was added. No SQLite or embedding service
is needed for this 11-project in-memory catalog.

## Gate B review brief

Review target: `/srv/projects/tools/skills-graph-navigator`, branch
`feat/graph-navigator-v1`, baseline `1f48047`. The reviewer changed only this
document. No child agent, secret, application-source read, commit, push,
deployment, or external state change was used.

### Reviewed finding and lead resolution

The reviewer initially raised P1 because the catalog lists
`boosty-api` entry point `openapi/openapi.json`, but that path is absent from
the existing public projected graph
`/srv/graphify/maps/graph-native-20260904-2315/graphs/boosty-api.json`.
`app` is present, so context is not empty. The lead validated the suggested
entry point against current Git: `git ls-tree HEAD openapi/openapi.json`
returns tracked blob `759343622e680f5afefbcfc7557efa472dee7d82`; the repository
README documents it as the API contract. Absence from an older AST projection
does not mean absence from source. The valid source-navigation entry point is
retained. This is an index-coverage limitation, not a required release fix.

No other Critical or Required correctness, security, performance, architecture,
or cleanliness findings remain after the final edge-before-symbol packing,
catalog path updates, sidebar label update, and context-size assertion.

### Evidence and gaps

- Reviewer checks: Node navigator/model tests 14/14; exporter tests 4/4;
  publisher tests 5/5; builder `--check` passed; catalog validation was
  read-only and left its input unchanged; offline synthetic browser preview
  passed with zero console errors, including 320, 390, 768, 1024, and desktop
  coverage.
- Lead-reported: the final all-11-real-map offline browser preview had zero
  errors; initial readiness was 1.03 seconds locally (not a network SLA).
  Scoped Semgrep covered 442 rules across 4 files with
  0 findings. History Gitleaks has 5 pre-existing matches, so no full security
  green status is claimed. Full repository gates are recorded by the lead below.
- Browser fixtures apply the tracked nginx CSP, but remain offline and do not
  verify live nginx, HTTPS, MIME, production routing or deployment. The UI cannot
  verify Git HEAD. Concurrent lead paths remain protected.

## Execution handoff

Profile: server. Planning/context skills kept the first release bounded; the
Graphify skill reused existing safe maps without indexing. TDD added failing
routing/context cases and reproduced edge starvation at 512 bytes before the
fix. Frontend/browser skills covered keyboard, retry, responsive cards and
offline CSP. Git/CI and security skills preserved disjoint work, private/public
allowlists and exact response limits. No runtime dependency was added.

Initial shared checkout was clean at 80251bb. A concurrent README commit
1f48047 and branch switch to main triggered isolation. Work continued in
feat/graph-navigator-v1 at 1f48047; original checkout changes were preserved.
Luna Context Scout and independent Luna Gate B both executed. The read-only
Serena call timed out; source navigation used a narrow Graphify query and
targeted local reads. Chrome DevTools blocked the domain by allowlist, so all
browser testing was offline. GitHub MCP confirmed origin/main at 1f48047.

Checks not applicable here: TS/React/Go/SQL/API runners (plain JS/Python/Bash,
no typed app or database changes), OSV/Trivy dependency/container scans (no
dependency or container changes), CodeQL (no configured analysis database),
infrastructure MCPs (no deployment). The quick security wrapper stopped on
five pre-existing history matches before OSV; this is not a complete pass.

Final lead verification (2026-09-05): HIGH-risk `make verify` passed all
10 configured checks; `make test` passed including the 324-skill catalog,
Graphify smoke checks, 14 Node tests (50 curated routing examples), 4 exporter
and 5 publisher tests. Latest offline synthetic and all-11-real-map browser
checks passed, with responsive coverage at 320/390/768/1024/1440 widths.
Biome, Ruff, ShellCheck, shfmt and whitespace checks passed. Scoped Gitleaks
found zero new matches; the full-history debt above is unchanged. Dedicated
CLI RSS measurement was skipped because /usr/bin/time is unavailable.

Fresh-context Sol HIGH-risk review completed with no Required findings and
approved the authorized commit/push. Browser graph identity checking remains
optional defense-in-depth: the publication validator already checks identity
before activation and verifies the copied release. Gate B's OpenAPI concern
was resolved by the lead's source evidence above. Neither reviewer deployed.
The implementation is delivered on feat/graph-navigator-v1; main and the live
graph-native-20260904-2315 release remain unchanged. Git commit/push identifiers
are recorded in the task's final handoff.
