.PHONY: verify check security refresh-inventory test test-portable entrypoints

verify:
	PYTHONDONTWRITEBYTECODE=1 ./scripts/skillctl verify .

check:
	./scripts/validate-registry.sh

test-portable: check
	./tests/skillctl.test.sh

test: test-portable
	./tests/graphify-server-map.test.sh
	./tests/graph-portal.test.sh

entrypoints:
	./scripts/check-agent-entrypoints.sh

security:
	/home/debian/server/tools/ai-quality/bin/ai-security-check

refresh-inventory:
	./scripts/refresh-sources-inventory.sh
