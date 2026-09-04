# Graph portal rollout

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
