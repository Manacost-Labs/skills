---
name: brainstorming
description: Use when a request introduces a new feature, subsystem, behavior, or ambiguous design whose success criteria need to be clarified before implementation.
---

# Brainstorming before implementation

Turn a rough request into a small, testable design. The goal is shared intent,
not ceremony.

## Choose the lightest path

- **Spike:** answer a feasibility question; define a cheap probe and label any
  code as throwaway.
- **Bounded:** an existing flow is understood and the change is small; present
  a short design with files, risks, and tests.
- **Architectural:** a new subsystem, interface, data flow, or migration; map
  the context, compare two or three options, and write down the chosen design.

When uncertainty could change the implementation, use the heavier path. If a
bounded request grows new interfaces or hidden dependencies, reclassify it.

## Conversation pattern

1. State the classification and the current understanding of the goal.
2. Ask only the next question that can change the design; prefer one question
   at a time.
3. Separate goals, non-goals, constraints, acceptance criteria, and rollback.
4. For architectural choices, show the recommended option and at least one
   viable alternative with cost, risk, complexity, and reversibility.
5. Present the design before editing when the scope is architectural or a
   material assumption remains. Treat explicit user approval as the checkpoint.

Do not let a short request bypass an important assumption. Do not create a
specification file for a trivial bounded change unless it will be reused by
another agent or reviewer.

## Handoff shape

End with a compact decision record:

```text
Goal:
Non-goals:
Chosen approach:
Files or interfaces:
Acceptance criteria:
Risks and rollback:
Verification:
```

After approval, use the repository's planning, TDD, and review workflows. Do
not invent implementation details that the design did not settle.

Adapted from [obra/superpowers](https://github.com/obra/superpowers); revision
and license are tracked in `inventory/external-skills.tsv`.
