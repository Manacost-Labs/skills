# Risk-based engineering system

## Scope and ownership

Baseline: `60a57c0`, branch `feat/central-skills-catalog`, clean worktree.
Preserve the existing Graph portal, its deployment, and `tasks/plan.md` and
`tasks/todo.md` belonging to that rollout. No application repositories,
production state, authentication, or user-home configuration changes.

Main: policy, router, model mapping, verification, profiles, CI, documentation.
Bounded Terra worker: `scripts/scope_guard.py`, `tests/test_scope_guard.py`.
Native Luna scout: read-only, completed. No recursive agent gates.

## Sequence and acceptance

1. Audit the policy, graph relationships, profiles and executable gates.
   Confirm model identifiers against official documentation and client metadata.
2. Add failing tests for risk/role routing, bounded skill selection, brief
   validation, scope isolation, and local/CI parity.
3. Implement a small standard-library CLI and declarative policy. Preserve
   existing inventory commands and vendor catalogs. Make profiles on-demand.
4. Introduce `make verify`, shared with CI, and a project opt-in mechanism;
   do not rewrite other projects' existing gates or runtime managers.
5. Shorten global instructions, reconcile the router/model guidance, and
   document Graph navigation, long-session checkpoints and honest limitations.
6. Focused tests, fresh-context independent review, full relevant verification,
   server-entrypoint checks, security scan and final scope comparison.

Risk: HIGH (global execution policy and concurrency tooling), complexity:
complex. Independent review is required, deployment is not part of the task.
Shared policy/registry/configuration changes remain sequential; the scope
worker has two disjoint paths. Git status/diff are checked before each slice.

## Applied methods and navigation

Server profile; task-scoped routing, planning, Graphify navigation and dev-team
ownership. CI/versioning guidance applies to the delivery slice, subordinate
to the user's risk-based policy and explicit commit/push requirement.
Existing Graphify map queried narrowly; its source revision predates HEAD and
is navigation evidence only. No local CodeGraph index. Serena timed out;
targeted local source reads are the fallback. OpenAI documentation MCP search
returned results; exact official model pages were also checked directly.

Success is executable behavior, not merely installed tools: unsafe scope and
malformed policy must fail; high-risk changes cannot select low-risk gates;
low-risk tasks must avoid mandatory subagents/full unrelated suites.

## Audit and verification record — 2026-09-04

The original policy had 443 lines / 3,305 whitespace-separated words. The final
global entrypoint has 155 lines / 1,166 words (about 65% fewer words, not a claim
about billed tokens). The router and canonical TDD skill now use task/risk
selection instead of unconditional skill chains or deleting pre-existing code.
Profiles use one unambiguous on-demand activation key. Provider identifiers
remain centralized and verified; no runtime managers or application caches moved.

### Context and review briefs

- **CONTEXT BRIEF — Luna completed.** Scope, profile parsing, inventory,
  validator and Graphify wrapper identified; baseline clean at `60a57c0`.
  Main validated source and corrected the brief's missing-map assumption:
  an existing Graphify map was queried narrowly, but was older than HEAD.
- **Terra — completed.** Two exclusively owned files implement scope checking
  and real temporary-Git regressions. No child agents, commits or integration.
- **REVIEW BRIEF — Sol CLEAR.** Five required findings were reproduced/fixed:
  contextual/binary secret gaps, ignored protected paths, mutable scope
  ownership, weak policy floors and duplicate profile activation. Follow-up
  confirmed current postimage/index scans and all 33 focused Python tests.
- **Architecture brief — Astra CLEAR.** Confirmed bounded global architecture
  review, exact role selection without implicit fallback, and revision/diff-bound
  completed review before integration/live activation. No further findings.

Observed assertion RED→GREEN covers removed risk safeguards, accidental skill
keyword substrings, binary/oversized postimages and a staged secret hidden by a
clean working tree. Initial scaffolding also failed because the new module did
not exist; that import error is not presented as behavioral regression evidence.
Git/Gitleaks integration tests use synthetic fixtures, not production data.

The isolated HIGH gate completed all 10 configured checks: 324-skill catalog,
legacy skillctl contracts, 15 engineering + 12 scope + 6 scanner tests, Ruff,
ShellCheck, Actionlint, whitespace and redacted Gitleaks. Scope initialization,
pre-edit checkpoint, diff guard and checkpoint were exercised on the clean
projection, not retroactively claimed for the original bootstrap edits.
The host's existing Graphify and graph-portal contract suites also passed.
All 10 direct policy links plus the Cursor adapter resolve correctly.

### Ownership and limits

During this task another session committed its 18 graph-portal/operations/test
paths as `3d0ba2e`; a read-only comparison confirmed no overlap with our owned
paths. They were preserved and never staged, reset, reformatted or integrated
by this task. The original `tasks/plan.md` and `tasks/todo.md` remain untouched.
Our final diff consists only of the explicitly owned engineering-system paths.

No commit or push was performed for this redesign; the latest request requires
separate explicit authority. No production deployment, application migration,
authentication change, cache deletion or additional listener was performed.

The stronger canonical `make verify` replaces the need to invoke the older
all-stack host `ai-check` for this catalog. Server installation checks stay
explicit. GitHub Actions is configured/linted but was not run remotely. Other
projects retain their existing gates until an explicit opt-in. CodeGraph had
no index; Serena timed out; targeted source was the fallback. Official model
documentation was checked. No browser/API behavior, application dependency
manifest, container image or CodeQL database changed, so unrelated browser,
API, OSV/Trivy/Semgrep/CodeQL and production checks were not claimed.

Historical full-scan baseline findings remain documented separately in
`docs/engineering-skills.md`; changed-postimage scanning is not a full-history
scan. Scope Guard is advisory for cooperating sessions, not a hostile same-UID
sandbox; ignored content under pruned opaque trees is outside its coverage.
Installed links track the live checkout, so future policy edits must be prepared
in a candidate checkout and reviewed before activation. Arbitrary clients cannot
be forced to load policy merely by creating a symlink; Hermes discovery limits
and this distinction remain explicit in the entrypoint documentation.
