#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
target="$repo_root/AGENTS.md"
entrypoints=(
	/home/debian/.codex/AGENTS.md
	/home/debian/.config/opencode/AGENTS.md
	/home/debian/.claude/CLAUDE.md
	/home/debian/.gemini/GEMINI.md
)

adopt_existing=false
if [[ "${1:-}" == "--adopt-existing" ]]; then
	adopt_existing=true
elif [[ $# -gt 0 ]]; then
	printf 'Usage: %s [--adopt-existing]\n' "$0" >&2
	exit 2
fi

for entrypoint in "${entrypoints[@]}"; do
	if [[ -L "$entrypoint" ]]; then
		if [[ "$(readlink -- "$entrypoint")" == "$target" ]]; then
			continue
		fi
		printf 'Refusing to replace symlink pointing elsewhere: %s\n' "$entrypoint" >&2
		exit 1
	elif [[ -e "$entrypoint" ]]; then
		if [[ "$adopt_existing" != true ]]; then
			printf 'Refusing to replace existing path; use --adopt-existing after review: %s\n' "$entrypoint" >&2
			exit 1
		fi
		if [[ ! -f "$entrypoint" ]]; then
			printf 'Refusing to adopt non-file path: %s\n' "$entrypoint" >&2
			exit 1
		fi
	fi
	parent=$(dirname -- "$entrypoint")
	if [[ ! -d "$parent" ]]; then
		printf 'Parent directory does not exist: %s\n' "$parent" >&2
		exit 1
	fi
	if [[ ! -w "$parent" ]]; then
		printf 'No write access to %s. Run this script with the privileges needed for that path.\n' "$parent" >&2
		exit 1
	fi
done

for entrypoint in "${entrypoints[@]}"; do
	if [[ -L "$entrypoint" ]]; then
		printf 'Already installed %s -> %s\n' "$entrypoint" "$target"
		continue
	fi
	if [[ -e "$entrypoint" ]]; then
		backup="$entrypoint.legacy-$(date -u +%Y%m%dT%H%M%SZ)-$$"
		mv -- "$entrypoint" "$backup"
		printf 'Preserved %s as %s\n' "$entrypoint" "$backup"
	fi
	ln -s "$target" "$entrypoint"
	printf 'Installed %s -> %s\n' "$entrypoint" "$target"
done
