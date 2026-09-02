---
name: wordpress-audit-handoff
description: Produce a self-contained WordPress audit, release-readiness, or SRE handoff from verified evidence. Use when packaging kolodahearthstone.com testing findings, staging results, plugin/core compatibility evidence, rollout gates, monitoring, rollback, or confidential security acknowledgments for another operator or stakeholder.
---

# WordPress Audit Handoff

Adapted from `courtneyr-dev/wp-release-audit-method` for a standalone project installation. Use with `wordpress-release-manager`; do not substitute documentation for an actual staging gate.

## Choose the audience

- Use a coworker handoff when the recipient needs to reproduce a finding and implement a fix.
- Use an SRE release brief when the recipient needs a go/hold decision, rollout gates, blast radius, monitoring, and rollback.

## Evidence rules

- State the exact commit, WordPress/PHP/Blocksy versions, environment, route, host, date, and test command.
- Separate observed facts, inferred risks, untested gaps, and cleared cases.
- Link only public authoritative sources. Verify a GitHub link is public before including it.
- Never expose private repository URLs, tokens, cookies, personal data, logs with identifiers, or vulnerability details under coordinated disclosure.
- Describe a private security issue only as: “A separate security issue was identified and responsibly disclosed through a private channel; details withheld.”
- Label every tool or skill as used, staged, or merely available.

## Coworker handoff

Deliver one self-contained document with:

1. Outcome and scope.
2. Environment and exact build tested.
3. Findings ordered by severity, each as mechanism → evidence → user impact → fix → verification.
4. Tested and cleared scenarios.
5. Untested gaps and why they remain.
6. Reproduction commands or browser steps with secrets removed.
7. Rollback and the next owner/action.
8. Public authoritative sources.

## SRE release brief

Start with one posture:

- `READY`: no operational gate remains.
- `READY WITH CONDITIONS`: numbered gates must close before promotion.
- `HOLD`: a gate cannot close safely in the release window.

Then include:

1. Conditions that would move the posture.
2. Operational changes: configuration, compatibility, capacity, observability, security, deployment, rollback, and support.
3. Variance matrix for PHP, image stack, Redis/object cache, page/edge cache, proxies, cron, plugins, and update policy.
4. Confirmed findings with reproduction, blast radius, affected routes/tiers, and whether the owner is WordPress upstream or project configuration.
5. Risk areas still under test; never present them as passes.
6. Numbered pre-release gates with owner and due condition.
7. Monitoring signals, rollback mechanics, RPO/RTO implications, and expected support symptoms.

## KolodaHearthstone release minimum

- Name the single commit already deployed to `test.kolodahearthstone.com`.
- Include `.ru`, `.com`, origin, Moscow, and Novosibirsk evidence for production-affecting changes.
- Confirm `.com` canonical, `.ru` legacy redirect, staging noindex, S3/media integrity, article views, banners/analytics, and targeted cache invalidation when affected.
- Treat a restore-from-backup as different from a code rollback and state the most recent successful restore drill.
- Never claim production success from a staging result or one HTTP response.

## Done when

The recipient can decide, reproduce, roll out, monitor, or roll back without asking where the evidence came from or which condition remains open.
