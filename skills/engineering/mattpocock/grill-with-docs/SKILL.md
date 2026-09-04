---
name: grill-with-docs
description: Use when a plan or design still has ambiguous domain terms, ownership, invariants, or failure modes and durable decision notes would help future agents.
---

# Grilling a design into durable context

Interview the request one question at a time. Probe the purpose, actors,
domain terms, invariants, boundaries, failure modes, operational constraints,
and how success will be observed. Prefer concrete examples and counterexamples
over abstract agreement.

Keep a decision ledger while asking:

- confirmed facts;
- assumptions still needing validation;
- terms that need a shared definition;
- decisions and rejected alternatives;
- open risks and the owner of the next check.

When a decision is durable, record the smallest useful ADR and glossary entry
in the project's existing documentation location. Do not create documents for
temporary exploration, and do not claim a term is settled until the user or
authoritative project source confirms it. Use the existing `domain-modeling`
skill for bounded contexts and relationships rather than invoking a missing
vendor-specific helper.

Adapted from [mattpocock/skills/grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs); revision and license are tracked in `inventory/external-skills.tsv`.
