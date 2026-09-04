---
name: writing-plans
description: Use when requirements describe a multi-step implementation and the worker needs exact scope, dependencies, acceptance criteria, and verification before editing.
---

# Writing implementation plans

Make the work executable by an engineer who knows the language but not the
local context. Keep the plan proportional: a short bounded task can stay in
chat; a cross-file or cross-project change needs a durable plan.

## Required contents

- Goal and non-goals.
- Repository root, protected paths, and relevant policy files.
- Files to create or modify, each with one clear responsibility.
- Dependencies, interfaces, migration order, and sequential checkpoints.
- Acceptance criteria that can be observed.
- Focused test first, expected RED/GREEN result, then the project gate.
- Rollback and unresolved assumptions.

## Task sizing

Split at a reviewer boundary, not by arbitrary file count. Each task should
produce a coherent, independently verifiable slice. Use exact paths and names;
never write placeholders such as “handle errors” or “add appropriate tests”.
For code behavior, make the smallest failing test explicit before the minimal
implementation.

## Self-review

Before handing off, check that every requirement maps to a task, later tasks use
the names and interfaces defined earlier, no task overwrites another session's
paths, and every verification command is safe in the stated environment.

Prefer the current repository plan mechanism or the task plan tool. Do not
force a vendor-specific `docs/superpowers` directory onto a project that has a
different documentation convention.

Adapted from [obra/superpowers](https://github.com/obra/superpowers); revision
and license are tracked in `inventory/external-skills.tsv`.
