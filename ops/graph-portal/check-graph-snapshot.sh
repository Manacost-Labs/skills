#!/usr/bin/env bash
set -euo pipefail

fail() {
	printf 'graph snapshot security: %s\n' "$1" >&2
	exit 1
}

quarantine=0
if [[ "${1:-}" == '--quarantine' ]]; then
	quarantine=1
	shift
fi
(($# == 1)) || fail 'usage: check-graph-snapshot.sh [--quarantine] PATH'
snapshot=$(realpath -e -- "$1") || fail "snapshot does not exist: $1"
[[ -d "$snapshot" ]] || fail "snapshot is not a directory: $snapshot"
command -v gitleaks >/dev/null 2>&1 || fail 'gitleaks is unavailable'
command -v jq >/dev/null 2>&1 || fail 'jq is unavailable'

while IFS= read -r -d '' risky_file; do
	if ((quarantine)); then
		unlink "$risky_file"
		printf 'Quarantined sensitive filename: %s\n' "${risky_file#"$snapshot"/}"
	else
		fail "blocked sensitive filename: ${risky_file#"$snapshot"/}"
	fi
done < <(find "$snapshot" -type f \( \
	-iname '.env' -o -iname '.env.*' -o -iname '*.pem' -o -iname '*.key' \
	-o -iname '*.p12' -o -iname '*.pfx' -o -iname 'id_rsa*' \
	-o -iname '.npmrc' -o -iname '.pypirc' -o -iname 'credentials.json' \
	-o -iname 'service-account*.json' -o -iname '*.kdbx' \
	\) -print0)

if ((quarantine)); then
	report=$(mktemp "${TMPDIR:-/tmp}/graph-gitleaks.XXXXXX.json")
	trap 'unlink "$report" 2>/dev/null || true' EXIT
	gitleaks detect --no-git --source "$snapshot" --no-banner --redact=100 \
		--report-format json --report-path "$report" --exit-code 0 >/dev/null
	while IFS= read -r finding; do
		[[ -n "$finding" ]] || continue
		resolved=$(realpath -e -- "$finding") || fail 'gitleaks reported a missing file'
		case "$resolved" in
		"$snapshot"/*) ;;
		*) fail 'gitleaks reported a file outside the snapshot' ;;
		esac
		unlink "$resolved"
		printf 'Quarantined gitleaks finding: %s\n' "${resolved#"$snapshot"/}"
	done < <(jq -r '.[].File' "$report" | sort -u)
fi

gitleaks detect --no-git --source "$snapshot" --no-banner --redact=100 --exit-code 1
