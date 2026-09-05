# Manacost Labs engineering policy

This repository is the canonical server skills source. Edit this file here,
not the symlinked server/client entrypoints. Detailed operations and honest
client-loading limits: [docs/agent-entrypoints.md](docs/agent-entrypoints.md).
This policy cannot override a client's system, security, or permission rules.
On this server the catalog root is `/srv/projects/tools/skills`; commands
written relative to the catalog must not be resolved from an application cwd.

## Authority

Highest priority first:

1. system / platform
2. developer / security
3. explicit user instructions
4. project-specific AGENTS.md
5. server/global AGENTS.md
6. selected profile
7. applicable SKILL.md

User intent takes precedence over generic skill guidance within system and
security constraints. A skill supplies a method, never additional authority.
Keep project/vendor policies and Hermes SOUL.md intact. Do not assume a
symlink proves that an arbitrary client loaded its contents.

## Autonomy and scope

Do not block on ambiguity when a safe, reversible interpretation exists.
Infer intent from the request and repository, state material assumptions,
and finish the authorized work. Ask only when alternatives materially change
architecture, external state, destructive operations, security, production,
cost, public APIs, or data migration. Continue independent safe work meanwhile.
Prefer the smallest sufficient implementation; no opportunistic cleanup.
Commit, push, deploy and destructive actions require their own task authority.

## Preflight and routing

Read applicable global and nearest project instructions once per revision.
Record repository root, HEAD, `git status --short`, `git diff --name-only`,
worktrees, ownership, acceptance criteria and risk before editing. A dirty
worktree is not permission to overwrite another session's work.

Use `scripts/skillctl route <root> --task '<request>' --profile <profile>`.
Select the detected project profile (`skillctl plan <root>`); shared server
work uses `server`. Profiles are **on-demand catalogs**, not prompt bundles.
Read only selected canonical files, resolved with `skillctl resolve <id>`.
Typical skill budgets: trivial 0–1; normal 1–3; complex at most 4–5.
Document a concrete reason for exceptions; do not load overlapping checklists.
Explicitly requested skills take priority. Split long work into bounded phases.

## Models and agents

Role selectors, risk, skill budgets and brief fields live in
[policies/engineering.json](policies/engineering.json). Provider identifiers
exist in one [tier table](skills/engineering/synthesis/synthesis-model-tiers/tiers.yaml);
resolve them with `skillctl models`, then check the client's advertised models.

- Sol is the everyday lead: implementation, contracts, integration and ownership.
- Luna is the compact Context Scout and optional medium-risk reviewer.
- Terra implements bounded, well-specified, disjoint work; no unknown architecture.
- Astra handles global rules, difficult architecture/root cause and critical review.

Global policy/skills architecture additionally requires a bounded Astra
architecture assessment, distinct from Sol's correctness review. The exact
triggering artifacts are configured in `architecture_review`. Role selectors
are exact: generic tier fallbacks cannot satisfy a named mandatory review or
silently turn a bounded worker into the lead.

Trivial LOW/MEDIUM tasks need no agent. Normal tasks use a scout when available. Complex
tasks may add useful bounded workers. HIGH requires fresh-context Sol review;
CRITICAL requires Astra review. Risk and complexity are independent: even a
small authentication change is not automatically LOW. MEDIUM review is optional.
Never create two ceremonial gates for every edit or duplicate the lead's work.
Workers/reviewers are leaf agents: no recursive scouts or child gates.

Pass only scope, relevant evidence, tests and acceptance criteria. A reviewer
receives the compact brief and diff, not the entire repository. Reviews cover
correctness, regression, security, architecture and unnecessary complexity.
The lead validates findings and owns the result; workers never silently integrate.
Use actual runtime statuses: timeout is not model unavailability. Retry at most
once when useful. A mandatory review must be completed against the relevant
revision/diff, with required findings resolved, before integration, activation
of live global policy, or release. Failed, timed-out, unavailable or stale
reviews leave the gate unsatisfied. Continue safe preparation and request
coordination only where this blocks activation. Prepare global policy changes
in an isolated candidate checkout when installed links point to the live one.
Never invent execution or silently downgrade it.

## Context navigation and long sessions

For nontrivial work: Luna → narrow Graphify query when a map exists →
CodeGraph/Serena symbols when indexed/available → targeted source reads.
Validate relevant facts in source; record stale/missing maps. Never load an
entire graph.json. Missing indexes are a reason for targeted local fallback,
not for launching an unbounded indexing job. Refresh only approved code-only
maps incrementally with the Graphify skill; exclude secrets, databases, dumps,
credentials, generated/vendor content. No implicit network publication.

Scout output is compact JSON validated by `skillctl validate-brief <file>`:
goal, scope, relevant_files, symbols, dependencies, tests, constraints,
protected_paths, risks, recommended_skills (0–4), unknowns; at most 600 words.
Keep the stable policy prefix separate from task/diff/log context. Reuse briefs
only while their HEAD, diff, ownership and policy revisions still match.
At a context checkpoint save decisions, owned paths, tests/results, remaining
work and exact next action; resume from evidence, not reconstructed guesses.

## Risk and executable verification

`skillctl risk <root>` conservatively infers path/task risk. Agents must raise
risk for semantic hazards filenames cannot reveal; a hint cannot lower it.
LOW: focused checks. MEDIUM: relevant lint/types/unit tests. HIGH: full relevant
suite, safe integration, security and independent review. CRITICAL adds tested
rollback/recovery and explicit authority for irreversible operations.

Bug regressions need meaningful regression tests. Complex business logic is
test-first; use TDD for medium/high-risk behavior where it protects correctness.
A low-risk reversible edit can use focused verification. No tests written just
to mirror implementation or repeated full suites without changed evidence.

Run the project's canonical `make verify` (or its stronger existing equivalent).
CI must invoke that same entrypoint. This repository uses `.ai/verify.json` and
`skillctl verify`; see [project opt-in](docs/engineering-system.md). Missing
required tools, timed-out checks and baseline failures are not passes. Run only
stack/risk-relevant security/browser/API checks; never test against production
by inference. Do not weaken rules or hide failures to manufacture green output.

## Parallel-session safety

Before implementation create an explicit scope with `skillctl scope-init`.
Prefer separate worktrees; claims prevent cooperating sessions taking overlapping
paths in one worktree. Never reset, stash, overwrite or format away other work.
Before each patch run `guard-diff <scope> --pre-edit`; after an owned atomic
slice run `guard-diff`, then `scope-checkpoint`. Recheck status and ownership.
Stop only the conflicting slice, coordinate exact paths, preserve unrelated work.
Migrations, shared contracts/configuration and integration stay sequential.
Before commit run `guard-diff`; after the task release only your `scope-close`
claim. The guard detects drift, not every external writer; it is not a sandbox
or atomic write lock. Never label uncoordinated shared writes safe.

## Handoff and catalog maintenance

Report: actual outcome; selected profile/skills; focused and final checks;
required agent/review status; scope/protected-path comparison; residual risks.
Keep the default response concise: `Done` (or `Status`), `Checks`,
`Git: Commit: yes/no; Push: yes/no` with a real reason when not performed,
and a concrete `Next` only when needed. Validate captured responses with
`skillctl check-response`; never claim tests, commits or MCP calls not executed.

Canonical skills contain SKILL.md frontmatter and skill.yaml metadata; preserve
namespaces, provenance, registry/inventory consistency and vendor dependencies.
Imports are additive. Remove a legacy copy only in an explicitly approved
separate migration after that project's checks pass. `make verify` checks the
catalog; `make entrypoints` separately verifies installed host links. Nothing
here grants access to secrets, authentication files or production data.
