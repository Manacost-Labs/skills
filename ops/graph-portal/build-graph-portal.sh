#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
manifest="$script_dir/repositories.tsv"
snapshot_checker="$script_dir/check-graph-snapshot.sh"
output=''
check_only=0

usage() {
	cat <<'EOF'
Usage: build-graph-portal.sh [--check] [--output PATH] [--manifest PATH]

Builds one code-only Graphify map per reviewed repository and an aggregate
server map. Source snapshots contain Git-tracked files only; public output
contains the native graph UI and allowlisted navigation JSON. Raw AST data
is retained in a private sibling directory, never inside the public release.
EOF
}

fail() {
	printf 'graph portal: %s\n' "$1" >&2
	exit 1
}

while (($#)); do
	case "$1" in
	--check)
		check_only=1
		shift
		;;
	--output)
		(($# >= 2)) || fail '--output needs a path'
		output=$2
		shift 2
		;;
	--manifest)
		(($# >= 2)) || fail '--manifest needs a path'
		manifest=$2
		shift 2
		;;
	-h | --help)
		usage
		exit 0
		;;
	*) fail "unknown option: $1" ;;
	esac
done

[[ -r "$manifest" ]] || fail "manifest is not readable: $manifest"

declare -A seen=()
repo_count=0
while IFS=$'\t' read -r slug label repository group extra; do
	[[ -z "$slug" || "$slug" == \#* ]] && continue
	[[ -n "$label" && -n "$repository" && -n "$group" && -z "${extra:-}" ]] || fail "invalid manifest row for $slug"
	[[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid slug: $slug"
	[[ -z "${seen[$slug]:-}" ]] || fail "duplicate slug: $slug"
	seen[$slug]=1
	resolved=$(realpath -e -- "$repository") || fail "repository does not exist: $repository"
	case "$resolved" in
	/srv/projects/*) ;;
	*) fail "repository is outside /srv/projects: $resolved" ;;
	esac
	[[ "$(git -C "$resolved" rev-parse --show-toplevel 2>/dev/null)" == "$resolved" ]] || fail "not a repository root: $resolved"
	((repo_count += 1))
done <"$manifest"

((repo_count >= 1)) || fail 'manifest has no repositories'
for command_name in awk git graphify tar realpath install python3; do
	command -v "$command_name" >/dev/null 2>&1 || fail "required command is unavailable: $command_name"
done
for asset in index.html app.js styles.css graph-model.mjs layout-worker.js; do
	[[ -r "$script_dir/$asset" ]] || fail "portal asset is missing: $asset"
done
[[ -x "$snapshot_checker" ]] || fail 'snapshot security checker is missing or not executable'

if ((check_only)); then
	printf 'graph portal manifest valid: %d repositories.\n' "$repo_count"
	exit 0
fi

[[ -n "$output" ]] || fail '--output is required unless --check is used'
output=$(realpath -m -- "$output")
case "$output" in
/srv/projects | /srv/projects/* | /home/debian/server | /home/debian/server/*)
	fail 'output must be outside source repositories'
	;;
esac

[[ ! -e "$output" && ! -e "$output.private" ]] || fail 'use a new release path; existing releases are immutable'
mkdir -p -- "$output/graphs"
install -d -m 0700 "$output.private"
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/graph-portal.XXXXXX")
cleanup() {
	rm -rf -- "$work_dir"
}
trap cleanup EXIT

graphs=()
while IFS=$'\t' read -r slug label repository group extra; do
	[[ -z "$slug" || "$slug" == \#* ]] && continue
	printf 'Building %s (%s)\n' "$label" "$slug"
	snapshot="$work_dir/snapshots/$slug"
	graph_dir="$output.private/$slug/graphify-out"
	mkdir -p -- "$snapshot" "$graph_dir"
	revision=$(git -C "$repository" rev-parse HEAD)
	git -C "$repository" archive --format=tar "$revision" | tar -xf - -C "$snapshot" \
		--exclude='.env*' --exclude='*/.env*' --exclude='*.pem' --exclude='*.key' \
		--exclude='*.p12' --exclude='*.pfx' --exclude='id_rsa*' \
		--exclude='.npmrc' --exclude='.pypirc' --exclude='credentials.json' \
		--exclude='service-account*.json' --exclude='*.kdbx'
	"$snapshot_checker" --quarantine "$snapshot"

	GRAPHIFY_OUT="$graph_dir" graphify extract "$snapshot" \
		--code-only --no-cluster --max-workers 1
	[[ -s "$graph_dir/graph.json" ]] || fail "Graphify produced no graph for $slug"
	python3 "$script_dir/export_graph.py" "$output/graphs/$slug.json" "$graph_dir/graph.json" \
		--repo "$slug" "$label" "$group" "$revision"
	graphs+=("$output/graphs/$slug.json")
done <"$manifest"

python3 "$script_dir/export_graph.py" "$output/graphs/whole-server.json" "${graphs[@]}"

for asset in index.html app.js styles.css graph-model.mjs layout-worker.js; do
	install -m 0644 "$script_dir/$asset" "$output/$asset"
done
awk -F '\t' 'BEGIN { OFS="\t"; print "# slug\tlabel\tgroup" } !/^#/ && NF { print $1, $2, $4 }' \
	"$manifest" >"$output/repositories.tsv"
printf '%s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >"$output/built-at.txt"
printf 'Graph portal built at %s with %d repository maps.\n' "$output" "$repo_count"
