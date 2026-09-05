# Graph portal rollout

## Extension: navigator first release (2026-09-05)

User approved starting the navigator plan and pushing source. Scope: reviewed
passports for the existing 11 repositories, local intent routing with reasons
and ambiguity, browser project cards and snapshot indicators, read-only local
CLI returning allowlisted graph metadata within a strict UTF-8 byte budget.
No deployment, raw source publication, external AI, index refresh, new service,
dependency, automatic hooks or cross-repository edge inference in this release.

Sequence and acceptance:
1. Tests first: natural-language routing, unknown/ambiguous queries, deterministic
   ordering, budget boundaries, directed relationships, stale/unknown revisions.
2. Add reviewed catalog and shared pure search/context functions; keep all 11
   projects available and route without depending on the drawing cap.
3. Connect browser search/cards and local CLI, using existing exported graphs.
   Source roots come only from the fixed manifest; CLI never reads source text.
4. Update exact publication asset validation and builder contract sequentially;
   preserve current release compatibility and do not activate any release.
5. Verify focused Node/Python tests, offline Chromium at desktop/mobile sizes,
   make check/verify, applicable lint/security; independent Luna micro-review.
6. Commit and push owned source paths only, preserve concurrent README edits.

Owned files: ops/graph-portal, graph-specific tests, this plan/checklist,
docs/operations/graph-navigator.md. Profile server. Skills: using-agent-skills,
planning-and-task-breakdown, context-engineering, graphify-server-map, TDD;
frontend/browser and Git/CI skills applied in their respective phases. This
exceeds the usual five-skill budget because explicit user policy requires each
phase's verification, not because all catalog skills are needed.

No parallel writers: contracts, implementation and integration remain with the
lead; read-only scout/review are independent. Baseline HEAD 80251bb was clean;
README.md changed subsequently and is protected. Existing graph commit 60a57c0
is stale relative to skills HEAD: a navigation hint, not current-code evidence.
Serena initial instructions timed out; targeted local reads are the fallback.
Chrome DevTools denied the domain by allowlist; browser checks will use only
offline project fixtures. GitHub MCP verifies the authorized push. Context7,
CodeGraph and remote infrastructure MCPs are unnecessary: no new external API,
no .codegraph index and no deployment.

## Goal

Publish `graph.kolodahearthstone.com` as a lightweight portal that can switch
between Graphify maps for each important repository and an aggregate server
view, then commit and push the source-controlled implementation.

## Scope

- Add a reviewed manifest of important repositories under `/srv/projects`.
- Build every map from a clean archive of Git-tracked files.
- Merge the repository graphs into one server-level graph.
- Add a static, responsive portal that lazy-loads the selected map.
- Track and install the nginx configuration.
- Create Cloudflare DNS records, enable HTTPS, and verify the public site.

## Non-goals

- Index task worktrees, uploads, caches, secrets, or untracked files.
- Modify any application repository.
- Run Graphify continuously or add a background watcher in this change.

## Dependencies and order

1. Add a failing contract test for the manifest, build script, portal, and nginx.
2. Implement the portal and deterministic build pipeline.
3. Generate maps serially with low CPU and I/O priority.
4. Deploy files atomically, install nginx, then configure DNS/TLS.
5. Run focused tests, repository/security gates, and browser checks.
6. Review, commit, and push only this repository's task-scoped changes.

Map generation and deployment stay sequential because they share staging and
publication paths. Read-only validation may run in parallel after deployment.

## Acceptance criteria

- The portal lists every repository in the reviewed manifest plus “Весь сервер”.
- Selecting an item updates the visible map and the URL without a page reload.
- The aggregate graph contains nodes from all successfully indexed repositories.
- Public HTTP redirects to HTTPS and HTTPS returns the portal with a valid TLS chain.
- No source application worktree or protected baseline path is changed.
- Focused tests, `make check`, security checks, and browser smoke checks pass.
