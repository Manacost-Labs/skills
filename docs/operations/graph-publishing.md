# Graph publishing

`graph.kolodahearthstone.com` is a static, native canvas portal for the 11
reviewed repositories listed in `ops/graph-portal/repositories.tsv`. It serves
one file/symbol map per repository and an aggregate `whole-server` file map.
“Whole server” means this approved source-code manifest; it does not describe
OS services, hosts, or runtime dependencies.

## Data boundary

The builder archives each repository at Git `HEAD` into a temporary snapshot,
quarantines sensitive filenames and Gitleaks findings, and runs Graphify in
code-only mode with one worker. Untracked files, task worktrees, uploads,
caches, source text, extraction context, credentials, and absolute server paths
are not public inputs. SQL extraction is not part of this release: the host
does not have the required `tree_sitter_sql` support, so the documented scope is
source-code maps only.

`export_graph.py` emits the small public schema: relative file paths, labels,
line numbers, node kinds, repository IDs, and allowlisted edge relations. The
raw Graphify `graph.json` files remain in the private sibling directory
`<release>.private/`, which is mode `0700`; never copy that sibling into the
web root or publish it as an adjacent asset.

The public release contains exactly these assets:

```text
index.html
app.js
styles.css
graph-model.mjs
layout-worker.js
repositories.tsv
built-at.txt
graphs/<11 repository slugs>.json
graphs/whole-server.json
```

The validator and publisher reject missing or extra files, duplicate or unsafe
manifest entries, symlinks, dangling graph edges, and unexpected public node or
edge fields. Public graph metadata is navigation data, not an authorization
boundary; review the manifest before adding a repository.

## Build

Build a new immutable release at low system priority:

```bash
release=/srv/graphify/maps/graph-native-$(date -u +%Y%m%d-%H%M)
ionice -c3 nice -n 19 ops/graph-portal/build-graph-portal.sh --output "$release"
```

The build is intentionally serial and should run only when host pressure
permits. A current rebuild produced 3,144 files, 38,401 symbols, and 77,622
aggregate symbol relations (`stats.links`) across all 11 repositories; its
aggregate public file graph contains 5,565 file edges. Validate before any
privileged operation:

```bash
ops/graph-portal/publish-graph-portal.sh --check "$release"
```

## Origin and publication

The nginx origin is defined in
`ops/nginx/graph.kolodahearthstone.com.conf`. HTTP redirects to HTTPS. The
origin serves only the static release and `/healthz`, uses `try_files`, and
sends restrictive headers. The native module has an explicit
`application/javascript` MIME location. The CSP permits same-origin scripts and
workers only, disallows child frames, and contains no CDN, `unsafe-eval`, or
inline script allowance. `style-src 'unsafe-inline'` remains because the UI
sets a small CSS custom property for cluster colors; this is a residual
hardening item, not a script execution dependency.

The Gate B review in `docs/operations/graph-ui-review.md` found and then
verified fixes for the publisher's content-integrity and reload-rollback risks.
Run the check-only validation before the privileged publication. Once the
release passes it:

```bash
ops/graph-portal/publish-graph-portal.sh "$release"
```

The publisher validates the exact release, copies it into a new versioned
directory, validates nginx, and switches the `current` symlink. Releases are
immutable; retain the previous version for rollback. After publication, verify
the HTTPS endpoint, `/healthz`, the module MIME type, CSP, and the desktop and
mobile graph flow. Offline browser tests do not verify live nginx response
headers or production routing.

Cloudflare proxies the DNS A and AAAA records and presents the public edge
certificate; nginx uses the dedicated Cloudflare Origin CA certificate. DNS,
authentication, and Cloudflare cache configuration are outside this task.
