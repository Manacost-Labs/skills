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

if $skillctl resolve missing/skill >/dev/null 2>&1; then
  printf '%s\n' 'expected missing skill to fail' >&2
  exit 1
fi

printf 'skillctl smoke tests passed.\n'
