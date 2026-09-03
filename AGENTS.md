# Server Skills Policy

This repository is the canonical source for the skills that are maintained by
Manacost Labs on the Debian server.

The server entrypoints `/srv/projects/AGENTS.md` and
`/home/debian/server/AGENTS.md` are intended to point to this same file. Keep
this file in the repository; do not edit either entrypoint as a separate policy
copy. Install them with `scripts/install-server-entrypoints.sh`.

## Authority and precedence

This file governs skill discovery and maintenance only. It never overrides
system, platform, developer, security, repository, or user instructions.

When several instructions apply, use this order:

1. system and platform instructions;
2. developer and security instructions;
3. `/srv/projects/AGENTS.md` (the server entrypoint, when installed);
4. the nearest project `AGENTS.md`;
5. the selected profile in `profiles/`;
6. the smallest set of skill files needed for the task.

More specific project rules remain authoritative for that project. A skill is
guidance, not permission to access secrets, production data, authentication
flows, or unrelated repositories.

## Mandatory execution contract

This is the server's main AI execution policy. It applies to every coding,
review, debugging, design, infrastructure, and documentation task performed
under `/srv/projects`, `/home/debian/server`, or a project reached through
those entrypoints.

"Always use" means: always evaluate every applicable skill, linter, quality
tool, and MCP listed below, and actually invoke the applicable ones. It does
not mean loading every unrelated skill into every prompt or starting every
MCP server for a task that cannot use it. A tool may be skipped only with a
short reason recorded in the handoff (for example: "not applicable",
"project has no Go code", or "MCP is not configured in this client"). Never
claim that a tool was used when it was only installed or mentioned.

### 0. Reason first, then code

Before implementation, the agent must make its reasoning inspectable and
honest:

- state material assumptions explicitly;
- ask a question when the requirement or context is ambiguous;
- present viable solution options when more than one approach is reasonable;
- explain important trade-offs, including cost, risk, complexity, and
  reversibility;
- say clearly when it does not understand something or lacks evidence.

Do not hide uncertainty behind confident wording or silently choose an
interpretation that can materially change the result.

### 0.1. Simplicity first

Prefer the smallest solution that satisfies the verified acceptance criteria:

- avoid unnecessary functions, abstractions, flexibility, and configuration;
- do not increase architectural complexity without a concrete requirement;
- prefer a clear 50-line solution over a speculative 200-line framework;
- remove complexity only when its behavior and ownership are understood.

### 0.2. Surgical changes

Change only what belongs to the task:

- do not perform opportunistic refactors or unrelated cleanup;
- do not modify neighboring code without a demonstrated need;
- preserve the project's existing style and conventions;
- do not delete old or apparently unused code without explicit permission;
- remove imports or functions only when they became unnecessary because of
  the current change.

### 0.3. Verifiable goals

Every task must have a concrete, testable success criterion:

- bug fix: first add a test that reproduces the failure;
- validation change: test invalid, boundary, and accepted input;
- refactor: prove behavior with tests before and after the change;
- multi-step task: write a plan and verify each stage before continuing.

The required outcome is not merely a plausible explanation or a code diff; it
is a result that can be checked with evidence.

### 1. Mandatory preflight for every task

Before searching code or proposing a patch, the agent must:

1. read `/srv/projects/AGENTS.md` and the nearest project `AGENTS.md`;
2. run the Context Scout gate described below, before selecting skills,
   tools, or MCPs;
3. identify the project root and select its profile with
   `scripts/skillctl plan <project-root>`; use `server` for shared-server
   work and the detected project profile for application work;
4. load the smallest applicable set from the selected profile with
   `scripts/skillctl list <profile>` and resolve each canonical skill with
   `scripts/skillctl resolve <skill-id>`;
5. use `using-agent-skills` to decide applicability and
   `planning-and-task-breakdown` for every non-trivial task. The plan must
   state scope, files, dependencies, acceptance criteria, verification, and
   safe parallel/sequential boundaries;
6. run `git status --short`, `git diff --name-only`, and `git worktree list`
   before any edit. Record the starting changed paths and treat them as
   protected work owned by the user or another session;
7. if the project has `.codegraph/`, run `codegraph explore "<question>"`
   before broad text search. Use Serena for symbol-aware navigation when its
   MCP is available and the task involves a non-trivial code relationship;
8. state the MCP decision before implementation: which applicable MCPs will
   be used, what each will verify, and why an applicable MCP is unavailable if
   it cannot be called.

For a behavior change, canonical skill `data/test-driven-development`
(`test-driven-development`) is mandatory: add or update the smallest failing
test first, make it pass, then refactor. For delivery or
CI changes, `ci-cd-and-automation` is mandatory. For code changes,
`git-workflow-and-versioning` is mandatory. For a large context, long-running
task, or context handoff, also load the relevant context-engineering skill.

### Mandatory 5.6 Luna sub-agent gates

For every task that can change code, configuration, dependencies,
infrastructure, tests, documentation, or release state, use two explicit
sub-agent gates. The required model/alias for both gates is **`5.6 Luna`**.
Use the native sub-agent/thread mechanism exposed by the current client, or
the configured dev-team mechanism when it supports model selection. These
gates are part of execution, not optional background advice.

#### Gate A: context before implementation

Before choosing skills, tools, or MCPs, start one read-only Context Scout on
`5.6 Luna`. It must not edit files, access secrets, commit, push, deploy, or
change external state. Ask it to return a compact `CONTEXT BRIEF` containing:

- task goal, scope, non-goals, and acceptance criteria;
- repository root, applicable `AGENTS.md` files, profile, and active-session
  or worktree ownership signals;
- baseline changed paths and protected paths;
- relevant files, symbols, tests, architecture constraints, and dependencies;
- risks, unknowns, likely regressions, and the smallest useful verification;
- recommended skills, tools, and MCPs with a reason for each.

The main agent must validate this brief against local repository evidence. The
brief never replaces the mandatory `AGENTS.md` read, worktree check, or the
main agent's responsibility for selecting and invoking applicable skills and
tools.

#### Gate B: documentation and micro-review after implementation

After implementation and focused tests, but before the final quality gate,
start a second independent documentation/review sub-agent on `5.6 Luna`.
Give it the implementation diff and the Context Brief. Its code review is
read-only by default; it may write only the explicitly assigned documentation
described below. It must:

- write or update only the task-scoped documentation, ADR, README, or handoff
  notes explicitly assigned to it; never invent behavior that the code does
  not implement;
- review the code for small errors, edge cases, stale context, test gaps,
  dead code, inconsistent naming, and unclear handoff details;
- report architecture, cleanliness, security, and performance concerns even
  when they are outside the requested fix, clearly marked as follow-up;
- return a `REVIEW BRIEF` with documentation changes, findings by severity,
  evidence, test gaps, residual risks, and recommended next actions.

The reviewer must not modify another session's paths, authentication/sign-in
files, secrets, production copies, or unrelated documents. Documentation edits
must be disjoint from concurrent work or explicitly coordinated before the
reviewer writes them. Code findings are advisory until the main agent verifies
and resolves them.

#### Model availability and final ownership

Attempt the exact `5.6 Luna` alias and record the result. Never claim that a
sub-agent ran when the client did not expose or execute it. If the alias is
unavailable, record `5.6 Luna: unavailable`; for low-risk work use the closest
available read-only reviewer only when safe, and for high-risk, production,
authentication, migration, or security-sensitive work stop and request a
model/coordination decision before editing.

The main agent remains accountable for the final result. Before responding it
must inspect both briefs, resolve all Critical/Required findings, and perform
the final checks for correctness, bugs, code cleanliness/readability,
architecture, security, performance, and repository hygiene. Run focused tests
first, then the project gate and applicable browser/API/CI/security checks.
Record skipped checks and the reason; do not turn an unavailable sub-agent or
failed check into an unqualified pass.

### 2. Parallel-session safety protocol

Several Codex sessions may work on the same server. A clean checkout is not a
prerequisite when another session is active, but ownership must be explicit:

- before **each** patch, repeat `git status --short` and compare
  `git diff --name-only` with the recorded baseline;
- after each atomic slice, repeat `git status --short` and
  `git diff --name-only`;
- if a path changed after the baseline, or another session owns an overlapping
  path, stop before applying a patch, inspect the new diff read-only, and
  coordinate through the available Codex task/thread or dev-team mechanism;
- use `dev-team` for broad parallel work: preflight, disjoint claims and
  worktrees, read-only review, dry-run conflict checks, verification, and only
  explicitly authorized integration. Never create blind workers or integrate
  an unreviewed patch;
- keep database migrations, OpenAPI/Protobuf contracts, generated files, and
  shared configuration changes sequential unless the plan explicitly assigns
  ownership and a contract checkpoint;
- do not use `git reset`, `git checkout`, `git stash`, destructive cleanup, or
  mass formatting to hide or overwrite another session's work;
- do not modify authentication/sign-in files, secrets, `.env` files, or
  unrelated task documents while working on another feature;
- if coordination cannot establish ownership, leave the files untouched and
  report the exact conflicting paths.

### 3. Skill activation matrix

The following skills are execution requirements, not a passive catalog:

| Work phase | Required skills to load and apply |
| --- | --- |
| Understand and plan | `using-agent-skills`, `planning-and-task-breakdown`, relevant `context-engineering` |
| Architecture and implementation | `codebase-design`, `domain-modeling`, `clean-architecture`, `incremental-implementation`, and the relevant frontend/API/backend skill |
| UI and frontend | `frontend-ui-engineering`, `ui-design`/design-system skills, `react-patterns`, `performance-optimization`, and browser-testing skills when UI behavior changes |
| Tests and verification | `test-driven-development`, the project test skill, `browser-testing-with-devtools` or Playwright skills for browser behavior, and the API testing skill for API behavior |
| Bugs and regressions | `diagnosing-bugs`, `debugging-and-error-recovery`, focused regression tests, then the full project gate |
| Security and dependencies | `security-and-hardening`, `code-review-and-quality`, `dependency-updater`, and the relevant security scanners |
| CI, releases, and hooks | `ci-cd-and-automation`, `git-workflow-and-versioning`, `documentation-and-adrs` when policy changes |
| Multiple agents/sessions | `dev-team`, `multi-agent-patterns`, `resolving-merge-conflicts`, and `git-workflow-and-versioning` |
| SEO/content | the SEO skill selected for the project; keep `codex-seo` and `claude-seo` as separate vendor options and do not silently mix their rules |

When two skills overlap, choose one canonical rule as the authority, note the
choice, and use the other only for additional checks. Do not make the agent
load the whole engineering profile if a smaller set is sufficient; do make
the selected skills visible in the plan and final handoff.

### 4. Installed tool and MCP routing

Use the installed executable or configured MCP when the task matches its
scope. Start by checking availability with `command -v <tool>` or the MCP
client. If an expected tool is missing, stop the affected check and report
it; do not silently substitute a weaker check.

#### Frontend and TypeScript

- TypeScript: `pnpm tsc --noEmit` (or the project's equivalent script).
- ESLint: `pnpm eslint .`; Next.js projects must use their project
  `eslint-config-next`, not the removed `next lint` command.
- Biome: `pnpm biome check .`.
- Knip: `pnpm knip` for unused files, exports, and dependencies.
- Vitest: `pnpm vitest run` for unit/component tests.
- Playwright: `AI_E2E=1 pnpm exec playwright test` when browser flows,
  accessibility, mobile keyboard, streaming, or responsive behavior changed.
  Use the installed browsers and cover the project's supported viewport
  profiles; do not make E2E silently replace unit tests.
- Dependency Cruiser: `depcruise --validate <project-config>` when an import
  graph or architecture boundary is affected.

#### Go, API, and data

- Go: `gofmt` (check-only unless formatting was explicitly requested),
  `go vet ./...`, `staticcheck ./...`, `golangci-lint run`,
  `go test ./...`, `go test -race ./...`, and `govulncheck ./...` as applicable.
- Go fuzzing is built in: run a scoped, time-bounded
  `go test ./... -fuzz=Fuzz -fuzztime=30s` only where fuzz targets exist and
  the package is safe to execute.
- Go performance diagnostics are built in: use `go tool pprof` and
  `go tool trace` only with a real captured profile/trace and a stated
  hypothesis; do not infer performance from static inspection alone.
- OpenAPI: use Spectral for linting, Schemathesis for safe non-production API
  testing, and `oapi-codegen` when generated Go clients/servers are part of
  the project contract. Keep schemas, config, and generated output consistent.
- Protobuf/gRPC: use Buf when the project contains Buf configuration.
- SQL: use `sqlc` with the project's config and verify generated code plus
  database tests; never regenerate another session's owned files.

#### Security, CI, and maintenance

- Run `/home/debian/server/tools/ai-quality/bin/ai-check` as the common gate
  when the project has no stronger `make check`; if `make check` exists, run
  that project entrypoint first because it is the source of truth.
- Run `/home/debian/server/tools/ai-quality/bin/ai-security-check staged` for
  staged-change checks and the same command with `quick` or `full` according
  to risk. Never print secret values or scan production dumps into the task
  output.
- Use Gitleaks, OSV-Scanner, Trivy, Semgrep, and CodeQL for the languages and
  risk areas they cover. CodeQL requires a project database and build; do not
  report CodeQL coverage without creating/analyzing that database.
- Use `actionlint` for GitHub Actions and the available ShellCheck, shfmt,
  yamllint, and Hadolint checks when those file types or workflows change.
- Use either `pre-commit` **or** `lefthook` per project, never both as active
  hook managers. Hooks complement, but do not replace, the final project gate.
- Use Renovate only for configuration validation, dependency discovery, or a
  user-approved update; do not apply dependency upgrades implicitly.
- Use OpenTelemetry SDK/Collector only with an explicit project config and
  reviewed destination. The server collector is not an automatic listener and
  must not open ports or export data by assumption.

#### Configured MCP servers

When the Codex client exposes them, use the applicable MCP directly:

| MCP | Mandatory use case |
| --- | --- |
| `serena` | symbol-aware project navigation, references, and safe semantic refactors |
| `codegraph` | relationship exploration in repositories with `.codegraph/` |
| `context7` | current official documentation for libraries, frameworks, or APIs whose behavior/version matters |
| `chrome-devtools` | browser runtime, console, network, layout, performance, and interaction verification |
| `github` | repository issues, PRs, Actions, and source context when the task includes GitHub; respect its read-only/lockdown setup |
| `openaiDeveloperDocs` | current official OpenAI product/API documentation |
| `sentry` | diagnosis of authorized application errors and regressions; do not expose secrets or unrelated user data |
| `open-design` and `miro` | design-system, visual-flow, or board work when the connected resource is in scope |
| `ovhcloud` and `ovhcloud-api` | authorized OVH infrastructure operations only; read first and require explicit scope for mutations |

MCP use must be evidence-producing: capture the relevant result in the
  reasoning or handoff and distinguish source facts from inference. If an MCP
  is unavailable in the current client, use the safest local fallback and say
  so. Never manufacture an MCP result.

### 5. Definition of done and quality gates

Every implementation handoff must include:

1. the selected profile and skills actually applied;
2. the preflight worktree baseline and confirmation that protected paths were
   not changed;
3. focused tests for the changed behavior, with RED/GREEN evidence when code
   behavior changed;
4. the project gate: `make check`, or
   `/home/debian/server/tools/ai-quality/bin/ai-check` when no project gate
   exists;
5. conditional browser, API, performance, dependency, CI, and security
   checks from the routing matrix;
6. a final `git status --short` and `git diff --name-only` comparison against
   the baseline;
7. the `CONTEXT BRIEF` and `REVIEW BRIEF`, including the actual `5.6 Luna`
   availability/execution status;
8. failures, baseline debt, skipped tools with reasons, residual risks, and
   the exact next action.

Do not disable a failing check, weaken a rule, or label a partial scan as a
“pass” to make the result green. If an existing baseline is not clean,
document it and add the narrowest new gate that prevents regression.

### 6. Response contract

Agent communication must be concise, direct, and outcome-first. Use the
user's language unless they ask otherwise. Progress updates should mention
only a material result, blocker, or decision; do not stream routine command
output.

The default final response is short enough to scan in a few seconds and uses
this order:

1. `Done:` one sentence stating what was actually completed;
2. `Checks:` only the relevant checks and their result;
3. `Git:` explicit `Commit: yes/no` and `Push: yes/no`. If pushed, include
   branch and commit; if not, say `Push: not performed` and the real reason;
4. `Next:` up to three concrete next-step options, with the recommended one
   first when there is a meaningful choice.

For a trivial task, compress this to one or two sentences. For an incomplete
task, replace `Done` with `Status` and state one blocker plus the required
user action. Never claim a commit, push, deployment, test, MCP call, or skill
use that did not actually happen. Do not paste raw logs, repeat the full
plan, list every inspected file, or add generic advice. Expand only when the
user asks for detail or a failure requires it.

When response text is available to the shell or CI, validate it with
`scripts/skillctl check-response < response-file>`; use `--trivial` only for
genuinely trivial work. The validator does not store or transmit response
content. When no response capture is available, apply the same checklist
manually before sending.

Prefer one canonical skill over copies in `.agents/skills`, `.claude/skills`,
and `.codex/skills`. Those directories are migration sources until their
project is explicitly switched to this catalog. Do not delete or replace them
as part of a skill import.

## Skill contract

Every canonical skill must:

- live below `skills/<namespace>/<skill-id>/`;
- contain a `SKILL.md` with frontmatter `name` and `description`;
- contain a `skill.yaml` with its canonical id and namespace;
- avoid secrets, credentials, cookies, private keys, and production dumps;
- state when it applies and what verification it requires;
- use repository-relative references or clearly mark external references;
- be small enough to load for one task.

The machine-readable index is `registry.yaml`. The server inventory and source
hashes are in `inventory/skills.tsv`. Run `scripts/validate-registry.sh` after
changing either one.

Use `scripts/skillctl list <profile>` to inspect a profile and
`scripts/skillctl resolve <skill-id>` to locate one canonical skill. These
commands are read-only. Use `scripts/skillctl audit <project-root>` before any
project migration to identify canonical matches and local drift.

## Safe migration

Import is additive. A skill moves through these states:

`discovered` → `reviewed` → `canonical` → `project-enabled` → `legacy-copy-removed`

Only the last state permits removing a project-local copy, and only in a
separate change after the project has passed its own checks. Conflicting files
keep explicit namespaces until a human chooses the winning version.

The `server` profile includes the `engineering` profile. Agents must select
the relevant engineering skills at preflight and apply every selected skill;
the profile is not a passive list of files. Loading remains task-scoped so
unrelated guidance does not dilute the active task's context.

## External catalogs

Vendor and platform catalogs remain dependencies, not copied source. They are
listed in `registry.yaml` and must not be silently edited or vendored into this
repository. Local project skills are the first candidates for canonicalization.
