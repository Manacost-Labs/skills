#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
skillctl="$repo_root/scripts/skillctl"

server_listing=$($skillctl list server)
grep -q '^profile: server$' <<< "$server_listing"
grep -q $'^  core/agent-roster\tskills/core/agent-roster/SKILL.md$' <<< "$server_listing"

resolved=$($skillctl resolve core/botforge)
[[ "$resolved" == "$repo_root/skills/core/botforge/SKILL.md" ]]

grep -q '^id: core/botforge$' <($skillctl show core/botforge)
grep -q '^--- SKILL.md ---$' <($skillctl show core/botforge)

tmp_project=$(mktemp -d)
trap 'rm -rf "$tmp_project"' EXIT
mkdir -p "$tmp_project/work.kolodahearthstone.com/.claude/skills/demo"
touch "$tmp_project/work.kolodahearthstone.com/.claude/skills/demo/SKILL.md"
plan=$($skillctl plan "$tmp_project/work.kolodahearthstone.com")
grep -q '^profile: openbot$' <<< "$plan"
grep -q '^legacy_skill_files: 1$' <<< "$plan"
grep -q '^migration: dry-run$' <<< "$plan"

mkdir -p "$tmp_project/work.kolodahearthstone.com/.agents/skills/botforge"
cp "$repo_root/skills/core/botforge/SKILL.md" "$tmp_project/work.kolodahearthstone.com/.agents/skills/botforge/SKILL.md"
audit=$($skillctl audit "$tmp_project/work.kolodahearthstone.com")
grep -q $'^  .agents/skills/botforge/SKILL.md\tcanonical\tcore/botforge$' <<< "$audit"
grep -q '^  canonical: 1$' <<< "$audit"

if $skillctl resolve missing/skill >/dev/null 2>&1; then
  printf '%s\n' 'expected missing skill to fail' >&2
  exit 1
fi

printf 'skillctl smoke tests passed.\n'
