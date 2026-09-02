---
name: wordpress-privacy-consent
description: Protect privacy, consent, and personal-data handling on hs-manacost.ru WordPress flows involving Plausible, cookies, comments, forms, recruitment, Telegram notifications, embeds, anti-spam, logs, exports, retention, and deletion. Use when creating, changing, auditing, or debugging any user-input or tracking surface on the primary, mirror, or staging host.
---

# WordPress Privacy Consent

Minimize personal data and make every collection, transmission, retention, export, and deletion path explicit. Pair this skill with `hs-manacost-project`, `wordpress-runtime-stack`, `wordpress-external-integrations`, and `wordpress-admin-ui` for forms or internal screens.

## Workflow

1. Build a data-flow entry using [references/data-map.md](references/data-map.md): fields, purpose, lawful/consent basis, storage, recipients, retention, roles, export and deletion path.
2. Classify scripts, cookies, pixels, embeds, comments, forms, Telegram messages, anti-spam signals, logs, and backups with [references/consent-matrix.md](references/consent-matrix.md).
3. Collect only fields needed for the stated purpose. Keep secrets out of the browser, URLs, analytics properties, Telegram links, logs, Git and error messages.
4. Require explicit, understandable consent where a non-essential action needs it. Refusing consent must not block essential reading or security controls.
5. Enforce server-side capability, nonce/permission, validation, sanitization, escaping, rate limits, retention and deletion. A hidden field or JavaScript check is not authorization.
6. Verify anonymous, authenticated, accepted, refused, expired and deletion scenarios on staging. Test `.com` without duplicating identity, analytics or form submissions.
7. Report the data inventory, observed requests/cookies, retention owner, deletion proof and remaining third-party risks with personal values redacted.

## Project rules

- Plausible remains one first-party-proxied tracker per production page and stays disabled on staging unless an explicit isolated test requires it.
- Telegram alerts contain the minimum useful summary and an authenticated admin URL; never include a full application, message body, IP, cookie, token, or private attachment URL.
- Anti-spam may permit a legitimate repeat submission and a submission to another vacancy; rate-limit behavior must be scoped and recoverable.
- Backups inherit retention and deletion obligations. Never claim erasure until live storage, queues, exports, caches and scheduled backup expiry are accounted for.

## Hard stops

- Do not introduce fingerprinting, consent-by-default, preselected marketing consent, or dark patterns.
- Do not inspect or export production personal data merely to test a UI.
- Do not send real personal data to third-party sandboxes or AI prompts.
- Do not weaken Wordfence, Turnstile, rate limiting, or access controls to make a test pass.
