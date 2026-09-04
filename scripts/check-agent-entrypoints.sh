#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
target="$repo_root/AGENTS.md"
entrypoints=(
	/home/debian/AGENTS.md
	/srv/projects/AGENTS.md
	/home/debian/server/AGENTS.md
	/home/debian/.codex/AGENTS.md
	/home/debian/.config/opencode/AGENTS.md
	/home/debian/.claude/CLAUDE.md
	/home/debian/.gemini/GEMINI.md
)

failures=0
for entrypoint in "${entrypoints[@]}"; do
	if [[ -L "$entrypoint" && "$(readlink -- "$entrypoint")" == "$target" ]]; then
		printf 'OK %s -> %s\n' "$entrypoint" "$target"
	elif [[ -L "$entrypoint" ]]; then
		printf 'ERROR: entrypoint points elsewhere: %s -> %s\n' "$entrypoint" "$(readlink -- "$entrypoint")" >&2
		failures=$((failures + 1))
	elif [[ -e "$entrypoint" ]]; then
		printf 'ERROR: entrypoint is not a symlink: %s\n' "$entrypoint" >&2
		failures=$((failures + 1))
	else
		printf 'ERROR: entrypoint is missing: %s\n' "$entrypoint" >&2
		failures=$((failures + 1))
	fi
done

if ((failures > 0)); then
	exit 1
fi
