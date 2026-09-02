---
name: wordpress-external-integrations
description: Design, change, audit, and recover external integrations used by hs-manacost.ru WordPress, including Telegram bots, APIs, webhooks, OAuth callbacks, embeds, analytics proxies, S3, and third-party publishing. Use for credentials, contracts, timeouts, retries, idempotency, signatures, queues, monitoring, failure isolation, regional delivery, and safe disablement.
---

# WordPress External Integrations

Make external dependencies bounded, observable and safe to disable. Pair this skill with `hs-manacost-project`, `wordpress-privacy-consent`, `wordpress-runtime-stack`, and the relevant API, Cloudflare, media or release skill.

## Workflow

1. Create or update an integration contract using [references/contract-schema.md](references/contract-schema.md). Record owner, purpose, data classes, endpoints, authentication type, timeout, retry policy, idempotency, rate limits, observability, degradation and disable switch.
2. Resolve the source boundary. Keep credentials only in the approved secret store/environment; commit names and setup contracts, never values, fingerprints, cookies, private keys or OAuth tokens.
3. Validate inbound requests with signature, timestamp/replay protection, schema and bounded body size. Authorize the resulting WordPress action separately.
4. Bound outbound calls with connect/read timeouts, safe retry rules, idempotency keys where supported and strict response validation. Never retry an unsafe write blindly.
5. Keep slow or optional providers off the page-render and editor-save critical path. Queue work when appropriate and expose retry/dead-letter state without leaking payloads.
6. Test success, timeout, DNS/TLS failure, 401/403, 429 with `Retry-After`, 5xx, malformed response, duplicate delivery, recovery and provider disablement on staging.
7. Verify observability and regional behavior using [references/failure-matrix.md](references/failure-matrix.md). Report correlation IDs and aggregate outcomes with credentials and personal data redacted.

Validate a redacted machine-readable contract with:

```bash
python3 .agents/skills/wordpress-external-integrations/scripts/validate_integration_contract.py contract.json
```

## Project-specific rules

- Telegram notifications contain a minimal summary and authenticated admin link; delivery failure must not lose or reject the underlying application/content action.
- S3 writes require content integrity and retrievable object verification before any local cleanup.
- Analytics proxy failure must not break article rendering. Mirror delivery must not double-submit events or webhooks.
- OAuth callback and webhook URLs must use the intended public host and remain consistent with provider configuration; staging credentials/callbacks stay isolated.

## Hard stops

- Do not print, commit, paste into PRs, or encode secrets in URLs or client-side bundles.
- Do not disable TLS verification, signature checking, WAF, Turnstile or permission callbacks.
- Do not test destructive provider actions or real Telegram recipients without explicit scope.
- Do not couple publishing, form persistence or page rendering to an optional provider's immediate success.
