---
name: test-driven-development
description: Build meaningful regression and test-first protection for bug fixes and medium/high-risk behavior, using focused verification for low-risk reversible edits.
---

# Risk-based test-driven development

User intent, project rules and the canonical engineering policy take precedence
over this method. Tests establish observable behavior, not compliance with a
ritual. Never delete existing implementation merely because it predates a test.

## Choose the protection

- Bug regression: add the smallest reproducer and confirm it fails because of
  the bug before fixing it. Existing behavior may need a test seam first.
- Complex business logic: test-first, including invalid, boundary and accepted
  inputs and important state transitions.
- MEDIUM/HIGH behavior: prefer test-first where it provides meaningful
  protection; include risk-appropriate integration/contract coverage.
- LOW reversible change: a focused check may be sufficient. A typo or
  formatting edit does not require ceremonial failing tests or an agent team.
- Refactor: establish behavioral protection before changing structure.
  Preserve unrelated work and do not rewrite code merely to improve a metric.

## Small cycle

1. State the observable acceptance criterion and the regression being prevented.
2. Add one focused test. Run it and inspect the failure: an unrelated import,
   dependency or environment error is not proof that the test reproduces a bug.
3. Make the smallest task-scoped change and rerun the focused test.
4. Refactor only when it improves the changed code, keeping protection green.
5. After review, run the project's canonical verification entrypoint at the
   selected risk. Do not repeat an unchanged full suite without a reason.

Use real behavior rather than assertions about mock calls or copied source
text. Mock only an understood external boundary; keep test-only facilities in
test utilities. Test the failure path as well as the accepted path. Never run
integration tests against production or private data by inference.

When adding tests to existing code, preserve the implementation, establish
evidence, then change it safely. Do not ask for a procedural exception when a
safe reversible testing approach exists. Ask only when the test itself needs
new authority, unavailable infrastructure or a material product decision.

## Verification and handoff

Record the reproducer, the observed RED and GREEN where applicable, focused
command, final gate, and any skipped coverage with its actual reason. Never
invent RED evidence, label an environment error a reproduced bug, disable a
failing test, or claim a partial scan as a full pass.
