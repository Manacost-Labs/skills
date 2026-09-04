#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat <<'EOF'
Usage:
  graphify-server-map.sh [options]

Options:
  --root PATH       Approved source root; repeat for multiple roots.
                    Default: /srv/projects
  --output PATH     Output parent outside source trees.
                    Default: /srv/graphify/maps
  --update          Refresh changed files instead of starting extraction.
  --dry-run         Preview commands and paths without writing or executing.
  -h, --help        Show this help.

The helper performs code-only extraction, clustering, and HTML call-flow export.
It does not install hooks, expose HTTP, or push a graph to an external store.
EOF
}

fail() {
	printf 'graphify-server-map: %s\n' "$1" >&2
	exit 1
}

roots=()
output_root=${GRAPHIFY_MAP_OUTPUT_ROOT:-/srv/graphify/maps}
dry_run=0
update=0

while (($#)); do
	case "$1" in
	--root)
		(($# >= 2)) || fail "--root needs a path"
		roots+=("$2")
		shift 2
		;;
	--output)
		(($# >= 2)) || fail "--output needs a path"
		output_root=$2
		shift 2
		;;
	--update)
		update=1
		shift
		;;
	--dry-run)
		dry_run=1
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		fail "unknown option: $1"
		;;
	esac
done

if ((${#roots[@]} == 0)); then
	roots=(/srv/projects)
fi

resolved_roots=()
for root in "${roots[@]}"; do
	resolved=$(realpath -e -- "$root") || fail "root does not exist: $root"
	case "$resolved" in
	/srv/projects | /srv/projects/* | /home/debian/server | /home/debian/server/*) ;;
	*) fail "root is outside the approved source scope: $resolved" ;;
	esac
	resolved_roots+=("$resolved")
done

output_root=$(realpath -m -- "$output_root")
case "$output_root" in
/srv/projects | /srv/projects/* | /home/debian/server | /home/debian/server/*)
	fail "output must be outside approved source trees: $output_root"
	;;
esac

if ((dry_run)); then
	graphify_cmd=(graphify)
elif command -v graphify >/dev/null 2>&1; then
	graphify_cmd=(graphify)
elif command -v uvx >/dev/null 2>&1; then
	graphify_cmd=(uvx --from graphifyy graphify)
else
	fail "graphify is not installed and uvx is unavailable"
fi

shell_join() {
	local part
	for part in "$@"; do
		printf '%q ' "$part"
	done
}

graphs=()
for root in "${resolved_roots[@]}"; do
	slug=${root#/}
	slug=${slug//\//-}
	slug=$(printf '%s' "$slug" | sed -E 's/[^A-Za-z0-9._-]+/-/g; s/-+/-/g; s/^-//; s/-$//')
	[[ -n "$slug" ]] || fail "could not derive an output name for $root"
	map_dir="$output_root/$slug"
	graph_out="$map_dir/graphify-out"
	if [[ -f "$root/.graphifyignore" ]]; then
		ignore_note='project .graphifyignore found'
	else
		ignore_note='no root .graphifyignore; existing per-project .gitignore files still apply'
	fi

	printf 'Root: %s\nOutput: %s\nIgnore policy: %s\n' "$root" "$map_dir" "$ignore_note"
	if ((update)); then
		action=(update "$root" --no-cluster)
	else
		action=(extract "$root" --code-only --no-cluster)
	fi
	printf '  GRAPHIFY_OUT=%q ' "$graph_out"
	shell_join "${graphify_cmd[@]}" "${action[@]}"
	printf '\n  GRAPHIFY_OUT=%q ' "$graph_out"
	shell_join "${graphify_cmd[@]}" cluster-only "$root" --no-label
	printf '\n  GRAPHIFY_OUT=%q ' "$graph_out"
	shell_join "${graphify_cmd[@]}" export callflow-html --output "$map_dir/graph.html"
	printf '\n'

	if ((dry_run)); then
		graphs+=("$graph_out/graph.json")
		continue
	fi

	mkdir -p -- "$map_dir"
	GRAPHIFY_OUT="$graph_out" "${graphify_cmd[@]}" "${action[@]}"
	GRAPHIFY_OUT="$graph_out" "${graphify_cmd[@]}" cluster-only "$root" --no-label
	GRAPHIFY_OUT="$graph_out" "${graphify_cmd[@]}" export callflow-html --output "$map_dir/graph.html"
	graphs+=("$graph_out/graph.json")
	[[ -f "$graph_out/graph.json" ]] || fail "Graphify did not produce $graph_out/graph.json"
	[[ -f "$map_dir/graph.html" ]] || fail "Graphify did not produce $map_dir/graph.html"
done

if ((${#graphs[@]} > 1)); then
	if ((dry_run)); then
		printf '  '
		shell_join "${graphify_cmd[@]}" merge-graphs "${graphs[@]}" --out "$output_root/server-global-graph.json"
		printf '\n'
	else
		"${graphify_cmd[@]}" merge-graphs "${graphs[@]}" --out "$output_root/server-global-graph.json"
	fi
fi

if ((dry_run)); then
	printf 'Dry run only: no files were written.\n'
else
	printf 'Graphify maps written under %s.\n' "$output_root"
fi
