---
name: using-agent-skills
description: Select a small canonical skill set for a concrete engineering task; use for routing unfamiliar or multi-phase work, not as an instruction to load the entire catalog.
---

# Task-scoped skill routing

The user's task and higher-priority instructions determine the work; a skill
describes a useful method. Safe, reversible ambiguity does not require a
STOP → ask → wait cycle. Continue independent work and ask only when the
interpretation materially changes authority, risk, cost or architecture.

## Select, do not bundle

1. Read applicable AGENTS.md once per revision. Identify root, profile, scope,
   risk and complexity. Use the existing Context Brief if still fresh.
2. From the catalog root run `scripts/skillctl route <root> --task '<request>'`
   with the project profile and complexity. The result contains IDs and paths,
   not the skill bodies. Validate suggested skills against the actual task.
3. Resolve and read only selected files. Explicitly requested skills come
   first; then one canonical skill per concrete need. A profile's
   `available:` list and `include:` expand discovery, never prompt loading.
4. Trivial: 0–1 skill. Normal: 1–3. Complex: usually at most 4–5. For more,
   explain why and split phases where possible. Do not read every reference
   linked by a selected skill; follow its mode-specific routing.
5. Apply what was selected, verify the relevant outcome, and state actual
   skill use in the compact handoff. Installed or listed is not executed.

The executable source is
[engineering policy](../../../../policies/engineering.json).
Use `skillctl list <profile>` only for an explicit catalog inspection, not
as mandatory preflight output. Missing tools need an honest fallback/result,
not invented coverage. Risk determines tests/review; trivial work has no
mandatory subagents. Workers are leaves, not recursive orchestration roots.

## Verification

Exercise the router with a typo, ordinary bug, API change, and complex
cross-system task. Check that explicit selections are preserved, unknown IDs
fail, budgets hold and a high-risk path cannot receive a low-risk gate.
Run `make verify` at the catalog root after changing routing behavior.
