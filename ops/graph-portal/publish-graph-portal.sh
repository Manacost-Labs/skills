#!/usr/bin/env bash
set -euo pipefail

fail() {
	printf 'graph portal publish: %s\n' "$1" >&2
	exit 1
}

check_only=0
if [[ "${1:-}" == '--check' ]]; then
	check_only=1
	shift
fi
(($# == 1)) || fail 'usage: publish-graph-portal.sh [--check] RELEASE_PATH'

release=$(realpath -e -- "$1") || fail "release does not exist: $1"
[[ -d "$release" ]] || fail "release is not a directory: $release"
case "$release" in
/srv/projects | /srv/projects/* | /home/debian/server | /home/debian/server/*)
	fail 'release must be outside source repositories'
	;;
esac

integrity_file=$(mktemp)
trap 'rm -f -- "$integrity_file"' EXIT
# Fingerprint before validation, then verify the root-owned copy before use.
(cd "$release" && find . -type f -print0 | sort -z | xargs -0 sha256sum) >"$integrity_file"

for asset in index.html app.js styles.css graph-model.mjs layout-worker.js repositories.tsv built-at.txt graphs/whole-server.json; do
	[[ -s "$release/$asset" ]] || fail "required release asset is missing: $asset"
done
[[ -z "$(find "$release" -type l -print -quit)" ]] || fail 'release must not contain symlinks'

repo_count=$(awk -F '\t' '!/^#/ && NF == 3 { count++ } END { print count + 0 }' "$release/repositories.tsv")
map_count=$(find "$release/graphs" -maxdepth 1 -type f -name '*.json' | wc -l)
((repo_count >= 1)) || fail 'public manifest has no repositories'
((map_count == repo_count + 1)) || fail "expected $((repo_count + 1)) maps, found $map_count"

while IFS=$'\t' read -r slug label group extra; do
	[[ -z "$slug" || "$slug" == \#* ]] && continue
	[[ -n "$label" && -n "$group" && -z "${extra:-}" ]] || fail "invalid public manifest row: $slug"
	[[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid public slug: $slug"
	[[ -s "$release/graphs/$slug.json" ]] || fail "map is missing for manifest entry: $slug"
done <"$release/repositories.tsv"
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$script_dir/export_graph.py" "$release" --validate

if ((check_only)); then
	printf 'graph portal release valid: %d repositories, %d maps.\n' "$repo_count" "$map_count"
	exit 0
fi

command -v rsync >/dev/null 2>&1 || fail 'required command is unavailable: rsync'
nginx_bin=$(command -v nginx 2>/dev/null || true)
[[ -n "$nginx_bin" ]] || nginx_bin=/usr/sbin/nginx
[[ -x "$nginx_bin" ]] || fail 'required command is unavailable: nginx'
sudo -n true 2>/dev/null || fail 'passwordless sudo is required'

release_id=$(basename -- "$release")
[[ "$release_id" =~ ^[A-Za-z0-9._-]+$ ]] || fail "unsafe release name: $release_id"
web_root=/var/www/graph.kolodahearthstone.com
destination="$web_root/releases/$release_id"
current="$web_root/current"
previous=$(sudo -n readlink "$current" 2>/dev/null || true)
[[ ! -e "$destination" ]] || fail 'release already exists; choose a new immutable release name'

sudo -n install -d -o root -g root -m 0755 "$web_root/releases"
sudo -n mkdir -- "$destination"
sudo -n rsync --archive --chown=root:root --chmod=D755,F644 "$release/" "$destination/"
"${BASH_SOURCE[0]}" --check "$destination"
(cd "$destination" && sha256sum --check --status "$integrity_file") || fail 'release changed during publication; active release unchanged'
sudo -n "$nginx_bin" -t || fail 'nginx validation failed; active release unchanged'
sudo -n ln -sfn "releases/$release_id" "$web_root/current.next"
sudo -n mv -Tf "$web_root/current.next" "$current"

if ! sudo -n systemctl reload nginx; then
	if [[ -n "$previous" ]]; then
		sudo -n ln -sfn "$previous" "$web_root/current.next"
		sudo -n mv -Tf "$web_root/current.next" "$current"
	else
		sudo -n unlink "$current"
	fi
	if sudo -n "$nginx_bin" -t && sudo -n systemctl reload nginx; then
		fail 'nginx reload failed; previous release restored and recovery reload verified'
	fi
	fail 'nginx reload failed; previous release link restored but service recovery needs attention'
fi

printf 'graph portal release active: %s\n' "$release_id"
