#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
script="$repo_root/skills/engineering/graph/graphify-server-map/scripts/graphify-server-map.sh"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

help=$($script --help)
grep -q '^Usage:' <<<"$help"
grep -q -- '--dry-run' <<<"$help"

preview=$($script --dry-run --root /srv/projects --output "$tmp_dir/maps")
grep -q 'Root: /srv/projects' <<<"$preview"
grep -q 'extract /srv/projects --code-only --no-cluster' <<<"$preview"
grep -q 'cluster-only /srv/projects --no-label' <<<"$preview"
grep -q 'graph.html' <<<"$preview"
[[ ! -e "$tmp_dir/maps" ]]

multi_preview=$($script --dry-run --root /srv/projects --root /home/debian/server --output "$tmp_dir/multi-maps")
grep -q 'merge-graphs' <<<"$multi_preview"
grep -q 'server-global-graph.json' <<<"$multi_preview"

update_preview=$($script --dry-run --update --root /srv/projects --output "$tmp_dir/update-maps")
grep -q 'update /srv/projects --no-cluster' <<<"$update_preview"

if $script --dry-run --root / >/dev/null 2>&1; then
	printf '%s\n' 'expected an unapproved root to fail' >&2
	exit 1
fi

printf 'graphify server map smoke tests passed.\n'
