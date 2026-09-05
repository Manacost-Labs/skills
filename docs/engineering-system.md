# AI engineering system

## Architecture and authority

The canonical chain is system/platform → developer/security → explicit user →
project AGENTS → global AGENTS → selected profile → selected skills. The global
policy is a stable short prefix, not a CLI manual. Project rules may narrow
its defaults; no skill can authorize unrelated work or override explicit intent.

`policies/engineering.json` defines role selectors, skill budgets, brief fields,
risk floors, required verification categories and protected-path guidance.
The existing `tiers.yaml` is the only runtime provider-ID table. `skillctl models`
resolves roles; it does not call an API or change the current conversation's model.

| Role | Responsibility |
| --- | --- |
| Sol | Everyday lead, contracts, implementation and final integration |
| Luna | Compact Context Scout; optional bounded advisory review |
| Terra | Clearly specified, disjoint implementation or tests |
| Astra | Global architecture, difficult escalation, critical independent review |

OpenAI identifiers were checked on 2026-09-04 against the official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages, and
against this client's advertised native model overrides. Account/client access
is separate evidence. A successful scout proves execution for that run only;
a timeout does not prove that the model is missing. Do not use a human display
label as an override unless that exact alias is advertised by the client.

## A bounded task

From the catalog root:

```bash
scripts/skillctl plan /path/to/project
scripts/skillctl route /path/to/project --profile server \
  --complexity normal --task 'Fix API pagination regression'
scripts/skillctl risk /path/to/project --risk HIGH
scripts/skillctl resolve engineering/diagnosing-bugs
```

`route` emits paths, not file bodies. Profiles use `activation: on-demand` and
`available:` instead of `load:`. `list` still prints the entire requested
catalog for inventory work; it is not required preflight. External consumers
parsing `load:` must migrate to `available:`. Explicit `--skill` selections
come first and must resolve; split phases when explicit requests exceed the
budget. Pattern matches are suggestions: the lead confirms task applicability.
`--path` adds planned paths; it cannot hide actual Git changes during verification.

Complexity selects a skill/context budget (1/3/5) and optional workers. Risk
selects the quality floor independently. Unknown source is MEDIUM. Global
policy, auth, migrations, infrastructure and CI are HIGH; production,
irreversible operations and sensitive paths are CRITICAL. Semantic hazards
without recognizable filenames require a raised `--risk`; classifiers are
not a security oracle. A risk hint can raise, never lower the detected floor.

Trivial work is lead-only. Nontrivial work normally gets a Luna scout. HIGH
requires fresh-context Sol review, CRITICAL Astra; MEDIUM review is optional.
Workers are leaves and cannot bootstrap another set of gates. Runtime model
selection remains the client's responsibility, not a shell-side impersonation.
Global policy and skill-orchestration architecture separately require bounded
Astra assessment; Sol's correctness review has a disjoint purpose. Exact
selectors are not automatic tier fallback permission. Review evidence must
match the relevant revision/diff and have required findings resolved before
integration, live policy activation or release. Incomplete/stale reviews are
unsatisfied gates; safe candidate preparation can continue.

## Graph and brief discipline

Use existing Graphify maps for narrow architecture/blast-radius questions,
then CodeGraph/Serena for indexed symbols, then source/tests at those locations.
Check the map's revision. Never paste a whole graph or repository tree.
Absent/stale indexes allow targeted source fallback; building or publishing a
map is not implicit permission. Approved refresh uses the graph skill's
code-only wrapper with `--update` and reviewed ignore files.

Scout JSON contains exactly `goal` (string) and these string arrays:
`scope`, `relevant_files`, `symbols`, `dependencies`, `tests`, `constraints`,
`protected_paths`, `risks`, `recommended_skills`, `unknowns`.
At most 12 entries per array, at most 4 skills, at most 600 words total.
Validate with `skillctl validate-brief brief.json`. No raw logs or secrets.
The reviewer receives that brief, acceptance criteria, diff and relevant tests;
it returns severity, evidence, required fixes, test gaps and residual risks.
The lead confirms findings. Test execution does not attest independent review.

Keep stable policy first and dynamic request/brief/diff afterward. Cache reuse
depends on the actual provider/client, so no automatic billing savings are
claimed. On compaction save: root/HEAD, policy revision, owned/protected paths,
accepted decisions, verified test commands/results, remaining risks and exact
next action. Invalidate a brief when its code, task, ownership or policy changes.

## One executable quality entrypoint

```bash
make verify
scripts/skillctl verify . --dry-run
VERIFY_RISK=HIGH VERIFY_BASE=<base-commit> make verify
make entrypoints
```

`.ai/verify.json` is reviewed project configuration, not arbitrary task text.
Checks are argv arrays, a minimum risk, bounded timeout, `covers` categories,
and optional `stacks` selectors. Stack detection recognizes catalog, Node,
TypeScript, Go, Python and OpenAPI marker files. There is no automatic package
installation, API testing against live systems, or shell expansion of requests.
Missing coverage fails before execution. `not_applicable` requires an explicit
reason; it is not a substitute for a failing or unavailable applicable tool.

LOW runs focused/whitespace/changed-secret checks here. MEDIUM adds catalogue,
unit and temporary-Git integration tests, Ruff and ShellCheck; HIGH adds Actionlint.
This repository has no typed application, production migration or runtime API;
application typechecking/recovery tools are not claimed. Required missing tools,
nonzero exit and timeout fail. Each selected check runs once and produces a
compact status/duration report. Fixes invalidate the affected prior result.

GitHub Actions calls the same `make verify`, with a conservative HIGH floor and
the event base revision. An all-zero new-branch base scans the complete tree.
Local `VERIFY_BASE=<same-base> VERIFY_RISK=HIGH make verify` reproduces that
selection. The whitespace gate also compares against that base and separately
checks the staged index; a clean CI checkout or clean working file cannot hide
committed/staged whitespace errors. Reports omit source contents.
Host symlink installation checks are deliberately separate from
portable catalog validation: a CI checkout must not point server links at itself.
The existing `make test` also checks the deployed server-map environment:
it requires actual `/srv/projects` repositories and Graphify. It is preserved
as a host integration command; `make test-portable` supplies the catalog
contracts to `make verify` on every machine. Do not call the portable suite
proof of a deployed graph or browser. Graph deployment tasks additionally
require the host tests and their own browser verification.

The Gitleaks check scans complete changed-file postimages, including
nonignored untracked files and separately staged index blobs, so unchanged
contextual keys are preserved and a clean working tree cannot hide an indexed
secret. Staged paths also participate in risk discovery. The scanner
redacts output and rejects sensitive names without opening them. Symlink,
binary and oversized postimages require explicit review, not a silent skip.
The limits are 2 MB per file and 20 MB per task scan. It is not a
historical full scan, vulnerability audit or proof of absence of secrets. The
existing historical scanner has documented baseline findings; do not suppress
them or describe the scoped scan as full coverage. Add OSV/Trivy/Semgrep/CodeQL
only for actual dependency/build/language targets; CodeQL needs a real database.

## Project opt-in without replacing existing gates

Keep an existing stronger canonical command. No application repository was
automatically migrated. For a project without one, review a local
`.ai/verify.json`, then add this target and invoke it unchanged from CI:

```makefile
.PHONY: verify
verify:
	/path/to/skills/scripts/skillctl verify .
```

Each project's commands must match its scripts, test isolation and lockfile.
For example, a reviewed TypeScript check can be:

```json
{"id":"types","argv":["pnpm","exec","tsc","--noEmit"],"min_risk":"MEDIUM","covers":["types"],"stacks":["typescript"]}
```

Add focused/unit/lint checks and HIGH safe integration/security checks so all
required categories are covered. Use the project's ESLint or Biome, scoped
unused-code checks and Playwright for changed browser behavior. Go projects
configure formatting check, vet/staticcheck/lint, unit and justified race tests.
API projects add their contract/integration checks; use Spectral/Buf/sqlc only
with matching contracts. `verify --dry-run` fails on gaps before running commands.
Do not point an argv back at this same runner recursively.

## Scope Guard and parallel sessions

Create the scope outside the repository or in ignored `.ai/*.scope.json`:

```bash
scripts/skillctl scope-init /tmp/example.scope.json --project /path/to/project \
  --owner task-unique-id --allow 'src/example/**' --allow 'tests/example/**' \
  --protect 'migrations/**'
scripts/skillctl guard-diff /tmp/example.scope.json --pre-edit
# apply one owned atomic slice
scripts/skillctl guard-diff /tmp/example.scope.json
scripts/skillctl scope-checkpoint /tmp/example.scope.json
# before an explicitly authorized commit: guard-diff again
scripts/skillctl scope-close /tmp/example.scope.json
```

The state records HEAD/worktree identity, baseline dirt and fingerprints;
claims live in the common Git directory and are created exclusively. Overlap
in one worktree fails conservatively. Baseline dirt remains protected even if
an allow pattern matches. The guard checks both sides of renames, staged,
deleted and untracked paths. Sensitive/opaque paths use metadata, not contents.
Ignored protected files are monitored by metadata outside explicitly pruned
generated/cache/vendor trees. Contents within those pruned trees are not
covered or authorized for editing by this guard.
Close removes only the matching claim, not source files or the audit state.

Use unique owners and scope files. There is no automatic stale-claim stealing;
coordinate before releasing another session's claim. A pre-edit checkpoint
detects intervening changes, including same-status edits, but cannot identify
an arbitrary writer or atomically lock a later write. Separate worktrees remain
the strongest isolation. A session actively changing disjoint baseline dirt
may require a fresh coordinated scope, not a destructive reset or blind rebase.
This tool protects cooperating sessions, not hostile code running as the same
Unix account; the JSON state is not an authenticated security boundary.

## Tool versions and caches: audit decision

No mise installation or global runtime-manager replacement was warranted for
this dependency-free Python/Bash catalog. Existing Node/Go/pnpm/uv installations
and application lockfiles are preserved. CI pins its external Go-installed
checker versions and Ruff in an isolated virtual environment; no framework
was added just for catalog validation.
For a future mixed-runtime project, adopt one reviewed local mise configuration
only after checking existing `.tool-versions`/runtime files; mise's
[configuration rules](https://mise.jdx.dev/configuration.html) distinguish
explicit config from optional idiomatic version files.

Existing server caches were found: pnpm store v11, Go build/module caches and
uv cache. They were not cleared or moved. uv supports concurrent cache use and
[documents its locking](https://docs.astral.sh/uv/concepts/cache/). Reuse installed
Playwright browser binaries and keyed package/build caches per project/version;
never put credentials, production fixtures or secrets in cached artifacts.
Do not share writable Next build outputs between concurrently running worktrees.

There is no Node/Next monorepo workload in this catalog, so Turborepo was not
added: there is no measured build DAG to accelerate. For an application pilot,
measure cold/warm build and test durations, then evaluate input/output keys and
the [official cache documentation](https://turborepo.com/docs/crafting-your-repository/caching).
Remote caches require a reviewed destination and authorization, not an implicit
network export. Prompt-size reduction is measured separately from actual token
cost/latency; neither caching nor model savings is claimed without telemetry.
