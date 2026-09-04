# Graph publishing

`graph.kolodahearthstone.com` is a static portal for the important server
repositories listed in `ops/graph-portal/repositories.tsv`. It includes one
code map per repository and an aggregate “whole server” map.

The builder exports every repository from Git `HEAD` into a temporary snapshot
before Graphify runs. Untracked files, task worktrees, uploads, caches, and
common secret/key filenames are therefore not indexed. Only generated HTML and
the public repository label manifest are deployed; graph JSON and reports stay
outside the web root. The generated Mermaid runtime is pinned to a reviewed
exact version during the build.

The nginx origin is defined in
`ops/nginx/graph.kolodahearthstone.com.conf`. It serves the HTML and `/healthz`
only, denies directory traversal by `try_files`, and sends restrictive browser
headers. `graph.json`, `GRAPH_REPORT.md`, source files, and map internals are
not placed in the public web root.

The DNS zone is hosted by Cloudflare. The A and AAAA records point to the nginx
origin and are proxied. The origin uses a dedicated Cloudflare Origin CA
certificate, while browsers receive Cloudflare's publicly trusted edge
certificate. HTTP redirects to HTTPS.

To build a release at low system priority:

```bash
release=/srv/graphify/maps/releases/$(date -u +%Y%m%dT%H%M%SZ)
ionice -c3 nice -n 19 ops/graph-portal/build-graph-portal.sh --output "$release"
```

Validate and atomically publish it with:

```bash
ops/graph-portal/publish-graph-portal.sh "$release"
```

The publisher verifies that every manifest entry has a map, synchronizes into
a versioned release with stale files deleted, validates nginx, and atomically
switches the `current` symlink. The previous release remains available for
rollback but is not reachable from the web root. The public map is navigation
metadata, not an authorization boundary; review the repository manifest before
adding a project.
