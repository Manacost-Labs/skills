#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
target="$repo_root/AGENTS.md"
entrypoints=(/srv/projects/AGENTS.md /home/debian/server/AGENTS.md)

for entrypoint in "${entrypoints[@]}"; do
  if [[ -e "$entrypoint" || -L "$entrypoint" ]]; then
    printf 'Refusing to replace existing path: %s\n' "$entrypoint" >&2
    exit 1
  fi
  parent=$(dirname -- "$entrypoint")
  if [[ ! -w "$parent" ]]; then
    printf 'No write access to %s. Run this script with the server administrator privileges needed for that path.\n' "$parent" >&2
    exit 1
  fi
done

for entrypoint in "${entrypoints[@]}"; do
  ln -s "$target" "$entrypoint"
  printf 'Installed %s -> %s\n' "$entrypoint" "$target"
done
