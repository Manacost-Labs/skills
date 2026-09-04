---
name: requesting-code-review
description: Use after a meaningful implementation slice, before merging, or when a fresh read-only review can catch regressions that the author may miss.
---

# Requesting a focused review

Give the reviewer the smallest complete context: change summary, requirements
or plan, protected paths, diff/commit range, and the tests that were run. Do
not hand over the whole session transcript.

Ask for findings by severity:

- **Critical:** security, data loss, broken deployment, or correctness failure;
  blocks delivery.
- **Important:** likely regression, missing required behavior, or meaningful
  test/performance gap; resolve before merge where in scope.
- **Minor:** clarity, naming, or follow-up improvement; record without hiding
  delivery status.

The reviewer should inspect the diff, edge cases, tests, dependency and secret
handling, performance impact, and whether the implementation matches the plan.
Verify each finding against the source before changing code. A disagreement is
resolved with evidence or a documented follow-up, never by ignoring the issue.

On this server, combine this skill with the mandatory post-implementation Luna
review gate when the client exposes it. A missing reviewer is a reported
verification gap, not an unqualified pass.

Adapted from [obra/superpowers](https://github.com/obra/superpowers); revision
and license are tracked in `inventory/external-skills.tsv`.
