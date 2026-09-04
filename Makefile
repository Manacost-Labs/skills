.PHONY: check security refresh-inventory test entrypoints

check:
	./scripts/validate-registry.sh

test: check
	./tests/skillctl.test.sh

entrypoints:
	./scripts/check-agent-entrypoints.sh

security:
	/home/debian/server/tools/ai-quality/bin/ai-security-check

refresh-inventory:
	./scripts/refresh-sources-inventory.sh
