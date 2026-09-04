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
	/home/debian/.dsh/AGENTS.md
	/home/debian/.hermes/AGENTS.md
	/home/debian/.cursor/rules/AGENTS.md
)
adapters=(
	"/home/debian/.cursor/rules/manacost-global.mdc|$repo_root/integrations/cursor/manacost-global.mdc"
)

failures=0
check_link() {
	local entrypoint=$1
	local link_target=$2

	if [[ -L "$entrypoint" && "$(readlink -- "$entrypoint")" == "$link_target" ]]; then
		printf 'OK %s -> %s\n' "$entrypoint" "$link_target"
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
}

for entrypoint in "${entrypoints[@]}"; do
	check_link "$entrypoint" "$target"
done

for adapter in "${adapters[@]}"; do
	IFS='|' read -r entrypoint link_target <<<"$adapter"
	if [[ -L "$entrypoint" && "$(readlink -- "$entrypoint")" == "$link_target" ]]; then
		printf 'OK %s -> %s\n' "$entrypoint" "$link_target"
	elif [[ -L "$entrypoint" ]]; then
		printf 'ERROR: adapter points elsewhere: %s -> %s\n' "$entrypoint" "$(readlink -- "$entrypoint")" >&2
		failures=$((failures + 1))
	elif [[ -e "$entrypoint" ]]; then
		printf 'ERROR: adapter is not a symlink: %s\n' "$entrypoint" >&2
		failures=$((failures + 1))
	else
		printf 'ERROR: adapter is missing: %s\n' "$entrypoint" >&2
		failures=$((failures + 1))
	fi
done

if ((failures > 0)); then
	exit 1
fi
