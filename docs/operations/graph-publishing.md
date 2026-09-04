# Graph publishing

The current Graphify pilot is a static, code-only map of the canonical skills
repository. Its source graph and report stay under `/srv/graphify/maps`; only
the generated HTML is copied to `/var/www/graph.kolodahearthstone.com`.

The nginx origin is defined in
`ops/nginx/graph.kolodahearthstone.com.conf`. It serves the HTML and `/healthz`
only, denies directory traversal by `try_files`, and sends restrictive browser
headers. `graph.json`, `GRAPH_REPORT.md`, source files, and map internals are
not placed in the public web root.

The DNS zone is hosted by Cloudflare. Add an A record for
`graph.kolodahearthstone.com` pointing to `151.80.21.140` (and an AAAA record
to `2001:41d0:c:c8c::` only if that address is intended to serve this site).
After DNS resolves, issue a dedicated certificate with Certbot and add an HTTPS
server block before redirecting HTTP to HTTPS. The existing root-domain
certificate does not cover this subdomain.

To publish a refreshed pilot map:

```bash
sudo install -d -o root -g root -m 0755 /var/www/graph.kolodahearthstone.com
sudo install -o root -g root -m 0644 \
  /srv/graphify/maps/srv-projects-tools-skills/graph.html \
  /var/www/graph.kolodahearthstone.com/index.html
sudo nginx -t && sudo systemctl reload nginx
```

Before expanding to all projects, run a dry-run and check resource pressure.
The public map is navigation metadata, not an authorization boundary; do not
publish a graph containing secrets, production paths, or private source
details.
