# Bounded runtime model dispatch (v1)

Opt-in source tooling, not a daemon or an automatic model switch in existing
clients. `skillctl route` retains its original JSON contract and on-demand
skill selection. `skillctl dispatch` adds the executable stage plan; it does
not load skills, contact providers, prove account access or run a model.

`policies/model-routing.json` contains versioned routes, reasoning levels,
limits and escalation conditions. It refers to roles in
`policies/engineering.json`; provider identifiers resolve exclusively through
the canonical `skills/engineering/synthesis/synthesis-model-tiers/tiers.yaml`.
No second model catalog or ordered fallback list is introduced.

## Routes and budgets

| Risk/context | Ordered stages |
| --- | --- |
| LOW, clear | worker / Medium |
| MEDIUM, known context, trivial or normal | worker / Medium |
| MEDIUM, complex or explicitly unknown context | scout / Low → worker / Medium |
| HIGH, any complexity | scout / Low → lead / High → high_reviewer / High |
| CRITICAL, any complexity | scout / Low → lead / High → critical_reviewer / Extra High |
| Global policy/skills architecture, or evidenced unclear root cause | Insert architect / Extra High planning after scout; keep independent correctness review |

The table currently resolves worker to Terra, scout to Luna, lead/high reviewer
to Sol, architect/critical reviewer to Astra. These labels are explanatory;
the executable reads exact selectors, never labels or a tier fallback.
Extra High is the Codex effort `xhigh`. Automatic `max` and `ultra` are rejected.
Architecture raises the risk to at least HIGH and is never an implementation
assignment. A HIGH architecture task has both architect planning and Sol review;
a CRITICAL architecture task retains separate Astra planning and critical review.

Limits per task ledger: one scout, one implementation attempt before escalation,
one review round, one architecture stage, at most four launcher-started model
processes. All selected stages have `max_attempts: 1` and explicit dependencies.
The launcher serializes one task; independent tasks can use independent ledgers
and isolated worktrees. It never creates agents or parallel workers on its own.

## Preview and availability

```bash
scripts/skillctl validate-routing-policy
scripts/skillctl dispatch /path/to/project --task 'Check an auth boundary' \
  --risk HIGH --complexity normal
scripts/manacost-dispatch /path/to/project --task-file /private/task.txt \
  --risk HIGH --complexity normal
```

Both commands are read-only by default. A plan contains risk, complexity,
reasons, ordered stages, resolved model, effort, requiredness, dependencies,
limits, escalation policy and status. Git changed/untracked/staged paths plus
`--path` contribute to the existing risk classifier; `--risk LOW` cannot hide
auth, public-contract or policy changes. Unrecognized source is MEDIUM, so use
actual scoped paths, not a low-risk hint to force a cheaper model. A declared
unknown context raises LOW to MEDIUM and adds one scout. `--architecture` can
raise the planning requirement, never disable a detected architecture gate.

Without capabilities, status is `needs_capabilities`, NOT ready. The caller
must supply a bounded UTF-8 JSON file via `--capabilities` with this shape:

```json
{"models":{"MODEL_ID_REPORTED_BY_CLIENT":["low","medium","high","xhigh"]}}
```

The placeholder is not an executable ID. Obtain exact identifiers AND supported
efforts from the intended client's advertised capabilities. `skillctl models`
only resolves policy: it is not an account/capability probe. Extra advertised
efforts may include max/ultra, but the router never selects them. If any required
model/effort is absent, status is `blocked` and no stage can run; no model/effort
fallback is performed. The declared capabilities are caller evidence, not an
authentication check or proof of availability at launch time.

## Explicit, one-stage execution

Future operator usage (not executed during implementation):

```bash
# Existing owner-only directory outside every model-writable root, mode0700.
# Reuse exactly this state path for the same task; keep it after failures.
scripts/manacost-dispatch /path/to/project --task-file /private/task.txt \
  --risk HIGH --capabilities /private/caps.json \
  --state /private/task-42/attempts.json --stage scout

# Add --execute to start ONLY the selected stage, once.
scripts/manacost-dispatch /path/to/project --task-file /private/task.txt \
  --risk HIGH --capabilities /private/caps.json \
  --state /private/task-42/attempts.json --stage scout --execute

# Inspect the returned brief/evidence before recording explicit acceptance.
scripts/manacost-dispatch /path/to/project --task-file /private/task.txt \
  --risk HIGH --capabilities /private/caps.json \
  --state /private/task-42/attempts.json --accept-stage scout
```

Continue with the next stage ID in the plan using the same task, initial brief,
flags and ledger. An ordinary HIGH plan uses scout, lead, high_reviewer; a
policy task inserts architect before lead. Acceptance and execution are separate
actions: an exit code of zero is not a review pass. A model must return only
`{"outcome":"completed|blocked|changes_required","brief":{...}}`; the brief
must satisfy `skillctl validate-brief`. Only completed, validated output enters
`awaiting_acceptance`. Required findings, missing executable, authentication/
provider failure, unsupported arguments, timeout, oversized or invalid output
consume the attempt and stop with `blocked`, without trying another model.
No logs or unvalidated model output are replayed into the next prompt.

Each accepted dependency hands off only its validated short brief (at most
600 words, 12 strings/list, four recommended skills). Initial `--brief-file`
uses the same schema. Input JSON/task files and the combined prompt are capped
at 16KiB; escalation evidence at 4KiB. Dry-run emits exact argv arrays for the
current input. Future handoffs cannot be predicted: `handoff_pending: true`
marks that dependency, and previewing again with the ledger after acceptance
shows the concrete argv containing the new brief. The entire repository,
conversation transcript and automatic file bodies are never embedded.

The private local JSON ledger (0600, max128KiB) is locked during a stage. An
attempt is fsynced BEFORE process creation; an interrupted `running` record is
not resumable. Task, policy, roles, limits and initial brief are bound to the
ledger. Source freshness uses HEAD, index identities and lstat metadata for Git
changes without reading source/secrets. Changed source invalidates outstanding
acceptance/review evidence. Deleting, copying or modifying a ledger is not an
authorized retry protocol; failed work requires explicit human rescoping.

## Codex invocation, not global configuration

The launcher constructs a Python argv list starting with `codex exec -m` and
the resolved model. Reasoning is a per-invocation `-c` TOML value for
`model_reasoning_effort`, not an edit to client configuration. The built-in
OpenAI provider is explicitly selected. There is no eval, shell interpolation,
`shell=True`, session resume or automatic reviewer substitution. User text is
one prompt argument after `--`; inherited stdin is disabled.

Each stage is a fresh ephemeral invocation. The native multi-agent feature is
disabled per invocation. All stages default to an explicit read-only sandbox.
`--allow-write` permits workspace-write ONLY for implementation; include this
same flag throughout that task so the ledger binding remains stable. Read-only
scout/planning/review stays read-only. Extra workspace writable roots are
cleared and implicit /tmp/TMPDIR write access excluded per invocation.
Execution requires a POSIX host: the launcher starts each stage in its own
process group and, on timeout or interruption, terminates that group before
returning. A non-POSIX host blocks before starting a stage rather than risking
an orphaned child process.
No permission bypass option is provided. Existing client, administrator and
project policy still applies, and unsupported flags fail closed.

This does **not** impose a host-wide spending quota, cap the model's internal
turns/tokens/HTTP retries, attest which model a remote provider actually used,
or prevent a same-user process from tampering with local files. It cannot
police other launchers, arbitrary model-invoked shell commands or inherited
MCP/plugin side effects. Use a client with appropriate permissions, keep the
ledger outside all writable scopes, and review brief/changes before acceptance.
The native multi-agent disable flag is defense in depth, not a security boundary.
No automatic billing savings or full runtime isolation is claimed.

Current official references (consulted without running the Codex binary):
[one-off configuration overrides](https://developers.openai.com/codex/config-advanced),
[reasoning and multi-agent configuration](https://developers.openai.com/codex/config-reference),
[non-interactive execution](https://developers.openai.com/codex/noninteractive).
Actual account access, installed CLI flag support and reasoning compatibility
remain client-specific. Global `config.toml`, authentication, symlink entrypoints,
production, DNS and existing sessions are untouched.

## Escalation and review boundary

`--ci-failed` adds information, never selects Astra by itself. Existing HIGH or
CRITICAL risk already chooses the stronger route. Additional confirmed
conditions require `--escalation CONDITION --evidence TEXT`: high_risk,
critical_risk, public_contract, auth, concurrency, migration, architecture_review,
or unclear_root_cause. Only architecture_review and unclear_root_cause add an
architect planning stage; unclear_root_cause also requires `--prior-attempts 1`.
Evidence and the one meaningful attempt are operator attestations, not inferred
from an exit code. They are included in the stage prompt as bounded context.

There is no automatic escalation launch or in-ledger retry/reset. After a
failed stage the launcher returns the allowed escalation conditions for a human
to validate and explicitly rescope. A fresh task is a new budget, not a hidden
fallback. Do not reuse an approval against a different plan/revision.

## Verification and adoption

`VERIFY_RISK=HIGH make verify` includes policy, route, ledger/argv regressions
and lint. Tests use injected runners or a PATH-pinned fake executable; they
never run real Codex or remote models. Existing `route` is unchanged.
No daemon, database, queue, network service, monitor or automatic client
registration is installed. The new command only runs when a caller opts in.

Implementation was explicitly constrained to no real model calls. Therefore
Sol correctness and Astra architecture reviews of this new routing layer are
**not performed**, not simulated by tests; adoption/integration gates remain
pending those authorized independent reviews. No commit/push is part of this
implementation. Real execution, session-model switching and client capability
claims require separately authorized validation.
