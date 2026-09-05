---
name: synthesis-model-tiers
description: Resolve judgment, routine and bulk model roles from the canonical provider table; use for model orchestration, escalation policy or verified model-table updates.
license: "CC0-1.0"
metadata:
  author: "Rajiv Pant"
  version: "2.2.0"
  source_repo: "github.com/synthesisengineering/synthesis-skills"
  source_type: "public"
---

# Model roles, not scattered identifiers

[tiers.yaml](tiers.yaml) is the single provider-ID source. Skills, memory and
project policies refer to roles. Provider preference lists may share a model:
a balanced lead can also be a judgment fallback. Preserve other providers'
mappings and verification dates when updating one provider.

- judgment: difficult architecture, global rules, unresolved complex root
  causes, security-sensitive cross-system decisions and critical review.
- routine: everyday engineering leadership and well-specified implementation.
- bulk: compact context scouting, bounded classification and advisory review.

A small task can carry high risk, but an unfamiliar symptom alone does not
force escalation. The lead first performs bounded diagnosis. Escalate when
complexity, uncertainty or blast radius exceeds its adequate capability.
Do not make every skill/script edit an expensive-model task.

## Server orchestration

Resolve `scripts/skillctl models` at the repository root. Role selectors in
[engineering.json](../../../../policies/engineering.json) choose lead, scout,
worker, architect and risk-specific reviewers; identifiers are not repeated.

Use the native client's advertised identifiers and model-selection mechanism.
A configuration entry or label does not prove account access or execution.
A request that timed out is `timed_out`, not `unavailable`; report the actual
status. At most one bounded retry when useful. Do not recursively spawn gates.
If mandatory review cannot run, report the missing gate, continue safe work,
and request coordination before a high-risk release; never quietly downgrade.

Agents cannot assume they can change their own model. When native delegation
is supported and authorized, delegate a bounded decision with compact evidence.
Otherwise request a client-side selection only when it genuinely blocks safe
progress. Do not ask the user to re-tier every ordinary diagnosis.

## Table updates and verification

Verify exact API identifiers against current official provider documentation
before changing the table. Record the provider verification date; preserve
unknowns and distinguish documentation from actual client/account availability.
No automatic model/API probes, key installation or external writes.

Run `skillctl models`, `skillctl validate-policy`, and focused routing tests.
A wrong identifier must not be masked as a lower-tier fallback. Consumer
catalogs may contain additional models, but shared roles must remain consistent.
Other vendor dependencies and legacy copies are not silently rewritten.

For the naming history only, see
[references/naming-rationale.md](references/naming-rationale.md).
CC0-1.0; adapted from synthesis-skills for the Manacost server policy.
