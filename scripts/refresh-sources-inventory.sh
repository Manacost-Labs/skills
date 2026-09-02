#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
inventory="$repo_root/inventory/skills.tsv"
source_inventory="$repo_root/inventory/sources.tsv"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

candidate_list="$tmp_dir/candidates"
rg --files --hidden -g 'SKILL.md' /srv/projects /home/debian/.agents/skills /home/debian/.codex/skills 2>/dev/null \
  | rg -v '/(node_modules|target|\.git)/' \
  | rg -v '^/home/debian/\.codex/skills/\.system/' \
  | rg -v '^/srv/projects/tools/skills/' \
  | sort -u > "$candidate_list"

tmp_output="$tmp_dir/sources.tsv"
printf '%s\n' $'id\tsource_path\tsha256\tselected\tsource_class' > "$tmp_output"

while IFS= read -r source_path; do
  name=$(basename -- "$(dirname -- "$source_path")")
  id=''

  case "$source_path" in
    /srv/projects/wordpress/hs-manacost.ru/*)
      candidate="wordpress/hs-manacost/$name"
      if awk -F '\t' -v wanted="$candidate" 'NR > 1 && $1 == wanted {found=1} END {exit !found}' "$inventory"; then id=$candidate; fi
      ;;
    /srv/projects/wordpress/kolodahearthstone.com/*)
      candidate="wordpress/kolodahearthstone/$name"
      if awk -F '\t' -v wanted="$candidate" 'NR > 1 && $1 == wanted {found=1} END {exit !found}' "$inventory"; then id=$candidate; fi
      ;;
  esac

  if [[ -z "$id" ]]; then
    id=$(awk -F '\t' -v wanted="$name" 'NR > 1 {n=split($3, parts, "/"); if (parts[n-1] == wanted && $2 !~ /hs-manacost|kolodahearthstone/) {print $1; exit}}' "$inventory")
  fi
  [[ -n "$id" ]] || { printf 'Unmapped source: %s\n' "$source_path" >&2; exit 1; }

  canonical_path=$(awk -F '\t' -v wanted="$id" 'NR > 1 && $1 == wanted {print $3; exit}' "$inventory")
  hash=$(sha256sum "$source_path" | awk '{print $1}')
  canonical_hash=$(sha256sum "$repo_root/$canonical_path" | awk '{print $1}')
  selected=no
  [[ "$hash" == "$canonical_hash" ]] && selected=yes
  source_class=project-local
  [[ "$source_path" == /home/debian/* ]] && source_class=user-managed
  printf '%s\t%s\t%s\t%s\t%s\n' "$id" "$source_path" "$hash" "$selected" "$source_class" >> "$tmp_output"
done < "$candidate_list"

mv -- "$tmp_output" "$source_inventory"
printf 'Refreshed %s source rows.\n' "$(tail -n +2 "$source_inventory" | wc -l)"
