#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
target="$repo_root/AGENTS.md"
entrypoints=(
	/home/debian/.codex/AGENTS.md
	/home/debian/.config/opencode/AGENTS.md
	/home/debian/.claude/CLAUDE.md
	/home/debian/.gemini/GEMINI.md
	/home/debian/.dsh/AGENTS.md
	/home/debian/.hermes/AGENTS.md
	/home/debian/.cursor/rules/AGENTS.md
)
adapters=(
	"/home/debian/.cursor/rules/manacost-global.mdc|$repo_root/integrations/cursor/manacost-global.mdc"
)

adopt_existing=false
if [[ "${1:-}" == "--adopt-existing" ]]; then
	adopt_existing=true
elif [[ $# -gt 0 ]]; then
	printf 'Usage: %s [--adopt-existing]\n' "$0" >&2
	exit 2
fi

if [[ -d /home/debian/.cursor && ! -d /home/debian/.cursor/rules ]]; then
	mkdir -p -- /home/debian/.cursor/rules
fi

validate_link() {
	local entrypoint=$1
	local link_target=$2

	if [[ -L "$entrypoint" ]]; then
		if [[ "$(readlink -- "$entrypoint")" == "$link_target" ]]; then
			return 0
		fi
		printf 'Refusing to replace symlink pointing elsewhere: %s\n' "$entrypoint" >&2
		exit 1
	fi
	if [[ -e "$entrypoint" ]]; then
		if [[ "$adopt_existing" != true ]]; then
			printf 'Refusing to replace existing path; use --adopt-existing after review: %s\n' "$entrypoint" >&2
			exit 1
		fi
		if [[ ! -f "$entrypoint" ]]; then
			printf 'Refusing to adopt non-file path: %s\n' "$entrypoint" >&2
			exit 1
		fi
	fi
	local parent
	parent=$(dirname -- "$entrypoint")
	if [[ ! -d "$parent" ]]; then
		printf 'Parent directory does not exist: %s\n' "$parent" >&2
		exit 1
	fi
	if [[ ! -w "$parent" ]]; then
		printf 'No write access to %s. Run this script with the privileges needed for that path.\n' "$parent" >&2
		exit 1
	fi
}

ensure_link() {
	local entrypoint=$1
	local link_target=$2

	if [[ -L "$entrypoint" ]]; then
		if [[ "$(readlink -- "$entrypoint")" == "$link_target" ]]; then
			printf 'Already installed %s -> %s\n' "$entrypoint" "$link_target"
			return 0
		fi
		printf 'Refusing to replace symlink pointing elsewhere: %s\n' "$entrypoint" >&2
		exit 1
	fi
	if [[ -e "$entrypoint" ]]; then
		if [[ "$adopt_existing" != true ]]; then
			printf 'Refusing to replace existing path; use --adopt-existing after review: %s\n' "$entrypoint" >&2
			exit 1
		fi
		if [[ ! -f "$entrypoint" ]]; then
			printf 'Refusing to adopt non-file path: %s\n' "$entrypoint" >&2
			exit 1
		fi
	fi
	local parent
	parent=$(dirname -- "$entrypoint")
	if [[ ! -d "$parent" ]]; then
		printf 'Parent directory does not exist: %s\n' "$parent" >&2
		exit 1
	fi
	if [[ ! -w "$parent" ]]; then
		printf 'No write access to %s. Run this script with the privileges needed for that path.\n' "$parent" >&2
		exit 1
	fi
	if [[ -e "$entrypoint" ]]; then
		local backup
		backup="$entrypoint.legacy-$(date -u +%Y%m%dT%H%M%SZ)-$$"
		mv -- "$entrypoint" "$backup"
		printf 'Preserved %s as %s\n' "$entrypoint" "$backup"
	fi
	ln -s "$link_target" "$entrypoint"
	printf 'Installed %s -> %s\n' "$entrypoint" "$link_target"
}

for entrypoint in "${entrypoints[@]}"; do
	validate_link "$entrypoint" "$target"
done

for adapter in "${adapters[@]}"; do
	IFS='|' read -r entrypoint link_target <<<"$adapter"
	validate_link "$entrypoint" "$link_target"
done

for entrypoint in "${entrypoints[@]}"; do
	ensure_link "$entrypoint" "$target"
done

for adapter in "${adapters[@]}"; do
	IFS='|' read -r entrypoint link_target <<<"$adapter"
	ensure_link "$entrypoint" "$link_target"
done
