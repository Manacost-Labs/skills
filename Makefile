.PHONY: check security refresh-inventory

check:
	./scripts/validate-registry.sh

security:
	/home/debian/server/tools/ai-quality/bin/ai-security-check

refresh-inventory:
	./scripts/refresh-sources-inventory.sh
