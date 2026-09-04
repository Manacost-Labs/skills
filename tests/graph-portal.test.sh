#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
portal_dir="$repo_root/ops/graph-portal"
manifest="$portal_dir/repositories.tsv"
builder="$portal_dir/build-graph-portal.sh"
scanner="$portal_dir/check-graph-snapshot.sh"
publisher="$portal_dir/publish-graph-portal.sh"
nginx_conf="$repo_root/ops/nginx/graph.kolodahearthstone.com.conf"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

[[ -x "$builder" ]]
[[ -x "$scanner" ]]
[[ -x "$publisher" ]]
[[ -f "$manifest" ]]
[[ -f "$portal_dir/index.html" ]]
[[ -f "$portal_dir/app.js" ]]
[[ -f "$portal_dir/styles.css" ]]

repo_count=$(awk -F '\t' '!/^#/ && NF { count++ } END { print count + 0 }' "$manifest")
[[ "$repo_count" -ge 10 ]]

awk -F '\t' '
  /^#/ || !NF { next }
  NF != 4 { exit 1 }
  $1 !~ /^[a-z0-9][a-z0-9-]*$/ { exit 1 }
  $3 !~ /^\/srv\/projects\// { exit 1 }
  seen[$1]++ { exit 1 }
  END { if (!seen["skills"] || !seen["heartpulse"] || !seen["kolodahearthstone"]) exit 1 }
' "$manifest"

"$builder" --check
if "$builder" --output /srv/projects >/dev/null 2>&1; then
	printf '%s\n' 'expected source-root output to be rejected' >&2
	exit 1
fi

if command -v gitleaks >/dev/null 2>&1; then
	mkdir -p "$tmp_dir/safe" "$tmp_dir/leaky"
	printf '%s\n' 'def answer(): return 42' >"$tmp_dir/safe/example.py"
	"$scanner" "$tmp_dir/safe"
	token_prefix=$(printf '%b' '\x73\x6b\x5f\x6c\x69\x76\x65\x5f')
	fixture_tail=$(printf '%s%s' '51MxNAK123456789' 'abcdefghijklmnop')
	printf 'token="%s%s"\n' "$token_prefix" "$fixture_tail" >"$tmp_dir/leaky/example.py"
	if "$scanner" "$tmp_dir/leaky" >/dev/null 2>&1; then
		printf '%s\n' 'expected snapshot secret scan to fail' >&2
		exit 1
	fi
fi

mkdir -p "$tmp_dir/release/graphs"
printf '%s\n' '<!doctype html>' >"$tmp_dir/release/index.html"
printf '%s\n' '/* app */' >"$tmp_dir/release/app.js"
printf '%s\n' '/* styles */' >"$tmp_dir/release/styles.css"
printf '%s\t%s\t%s\n' '# slug' 'label' 'group' 'sample' 'Sample' 'Test' >"$tmp_dir/release/repositories.tsv"
printf '%s\n' '2026-09-04T00:00:00Z' >"$tmp_dir/release/built-at.txt"
printf '%s\n' '<!doctype html>' >"$tmp_dir/release/graphs/sample.html"
printf '%s\n' '<!doctype html>' >"$tmp_dir/release/graphs/whole-server.html"
"$publisher" --check "$tmp_dir/release"

grep -q 'id="repository-select"' "$portal_dir/index.html"
grep -q 'id="graph-frame"' "$portal_dir/index.html"
grep -q 'URLSearchParams' "$portal_dir/app.js"
grep -q 'textContent = repository.label' "$portal_dir/app.js"
grep -q 'mermaid@11.17.2' "$builder"
grep -q 'loading="lazy"' "$portal_dir/index.html"
grep -q 'X-Frame-Options "SAMEORIGIN"' "$nginx_conf"
grep -q ':443 ssl' "$nginx_conf"
grep -q 'return 301 https://graph.kolodahearthstone.com' "$nginx_conf"
grep -q '/etc/ssl/cloudflare-origin/graph.kolodahearthstone.com.pem' "$nginx_conf"
grep -q 'root /var/www/graph.kolodahearthstone.com/current;' "$nginx_conf"

printf 'graph portal contract tests passed.\n'
