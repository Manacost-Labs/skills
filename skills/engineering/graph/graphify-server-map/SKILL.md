---
name: graphify-server-map
description: Use when explicitly asked to build, refresh, query, or visualize a safe Graphify map of server source repositories; do not activate for ordinary codebase questions without an existing map.
---

# Safe Graphify server map

Graphify is the visual, cross-file knowledge map. Use the narrower `codegraph`
index for symbol-level questions inside one already-indexed project. This skill
keeps the expensive and privacy-sensitive operation explicit.

## Scope

- Approved roots: `/srv/projects` and `/home/debian/server`, including their
  source subdirectories.
- Never index `/`, `/etc`, `/root`, `/var/www`, production copies, databases,
  uploads, backups, or home-directory caches.
- Keep generated maps outside source trees, by default under
  `/srv/graphify/maps`.
- Do not expose the graph over HTTP or push it to Neo4j/FalkorDB without a
  separate explicit request and reviewed authentication.

## Privacy and token rules

Before a real run, confirm that each project uses `.gitignore` and, where
needed, a `.graphifyignore`. Graphify merges those files and evaluates
`.graphifyignore` last. At minimum exclude:

```gitignore
.git/
.env*
*.pem
*.key
*credentials*
*.p12
*.pfx
*.sqlite
*.db
*.dump
*.sql.gz
node_modules/
vendor/
dist/
build/
target/
.cache/
.codex/
uploads/
backups/
```

For a server-wide inventory, use code-only extraction first. It is local AST
work and avoids sending documentation, PDFs, images, or secrets to a model.
Do not select deep semantic extraction or a remote backend unless the user
names the exact source scope and accepts the token/privacy trade-off.

## Workflow

1. Check current load before a broad run. If Codex/Serena is already CPU-hot or
   swap is growing, defer the map or run one small project first.
2. Preview the scope without writing anything:

   ```bash
   /srv/projects/tools/skills/skills/engineering/graph/graphify-server-map/scripts/graphify-server-map.sh \
     --dry-run --root /srv/projects
   ```

3. Run an explicit code-only map when the preview is correct:

   ```bash
   /srv/projects/tools/skills/skills/engineering/graph/graphify-server-map/scripts/graphify-server-map.sh \
     --root /srv/projects
   ```

   The helper uses an installed `graphify` binary or the official package via
   `uvx --from graphifyy graphify`; it never installs hooks or a server.
4. Open the generated per-root `graph.html` and read the compact
   `GRAPH_REPORT.md`. Query the JSON from its map directory when a question is
   narrower than the report:

   ```bash
   graphify query "what connects the deployment service to its data store?" \
     --graph /srv/graphify/maps/<root>/graphify-out/graph.json
   ```

5. Refresh only changed code with `--update`. Do not enable post-commit hooks
   across all projects until CPU, disk, and map freshness are measured.

## Outputs and rollback

Each root gets an isolated output directory with `graph.json`, a visual HTML
map, and Graphify's report. Delete only that generated map directory to roll
back; source repositories and project configuration remain unchanged.

## What not to claim

Graphify's relationships can be extracted, inferred, or ambiguous. Report the
map as an index for navigation, not as proof of runtime behavior. Use tests,
logs, and `codegraph`/source inspection to validate important conclusions.

Source inspiration: [Graphify](https://github.com/Graphify-Labs/graphify),
revision tracked in `inventory/external-skills.tsv`.
