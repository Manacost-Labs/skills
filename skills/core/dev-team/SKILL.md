---
name: dev-team
description: Coordinate a local team of Codex agents for planning, parallel implementation, read-only review, and controlled patch integration. Use when the user asks for a team of agents, parallel developers, multi-agent implementation, review agents, or Codex Dev Team.
---

# Codex Dev Team

Use this skill when the user wants multiple Codex agents to work like a small development team.

## Operating Model

Codex Dev Team is intentionally process-heavy:

- Planning and exploration should be broad and mostly read-only.
- Use `dev_team_plan_only` before implementation when parallel safety, risk, or task boundaries are unclear.
- Use `dev_team_audit` for read-only architecture/security/performance/test/dependency review without patches.
- Runs should begin with a repository discovery/profile brief so planning and worker briefings share the same initial repository facts.
- Do not create blind generic workers when specialist profiles exist. Use `dev_team_agent_catalog` or `dev_team_resolve_agents` to inspect local Codex skills, local `.codex/agents`, `.agents`, and `.claude/agents` profiles, then rely on the bundled fallback catalog only when local profiles are missing or weaker.
- Treat `max_agents` as a run cost/noise budget ceiling, not a target. Prefer fewer, better-owned shards when extra agents would add coordination noise.
- Use `context_budget` to control how much run context workers read before editing. `standard` is the default; use `lean` for small tasks and `deep` for high-ambiguity work that needs full briefings up front.
- Use `quality_profile` to control code quality gates. `standard` is the default; use `strict` when the user explicitly prioritizes code quality over speed.
- Implementation should be narrow and isolated in Git worktrees.
- Reviewers must not fix code; they only return findings.
- Integration should prefer a temporary integration worktree dry-run before any selected patch reaches the user's main checkout.
- Lifecycle recovery is durable: stalled, failed, or interrupted workers should leave reports, logs, and any best-effort partial patch artifacts inspectable in the run directory.
- The main thread should stay focused on requirements, decisions, status, and final results.
- Team Memory is local to a run under `.codex-team/runs/<run_id>/memory/`; do not introduce external services or persistent global state for it.
- Dashboard and graph data should be derived from durable run artifacts, not from volatile in-process state alone.
- When the Codex host supports MCP Apps widgets, prefer surfacing the bundled inline dashboard widget over asking the user to call or remember a status command.
- Native sidebar subagents are host-managed custom-agent threads, not MCP workers. Use host native subagent tools when the user explicitly wants agents visible in the right sidebar; use Dev Team MCP workers for durable worktree-based runs.

## Team Memory

Runs may expose simple Markdown or JSON artifacts under:

```text
.codex-team/runs/<run_id>/memory/
  facts/
  decisions/
  claims/
  interfaces/
  contracts/
  risks/
  questions/
  agent-notes/
  briefing/
  graph/ (optional)
```

Claims are generated from normalized plan tasks before workers start. Treat each task id, title, allowed path list, and suggested test list as the worker's ownership source of truth.

Claims may also include `execution_policy`, `allowed_paths`, `forbidden_paths`, patch size/file limits, package/network/migration flags, `context_budget`, compact briefing paths, `quality_gates`, and `contract_paths`. Treat these as safety boundaries. If a patch exceeds policy or fails a quality gate, call out the exception and prefer `dev_team_patch_score`, `dev_team_verify`, or a retry/rebase before integration.

Claims may include `agent_profile`. Treat it as role guidance for the worker. Local profiles come from discovered Codex skills or Claude-style agent Markdown files; bundled fallback profiles are Codex-adapted from VoltAgent's MIT-licensed Claude Code subagent categories.

Before planning, runs should create repository discovery/profile briefs, normally at `.codex-team/runs/<run_id>/memory/facts/repository-discovery.md` and `.codex-team/runs/<run_id>/memory/facts/repository-discovery.compact.md`. Worker prompts should include generated primary, compact, and full briefing paths. The worker is expected to read the primary briefing before editing and use it for assigned task details, allowed paths, the repository discovery brief, sibling claims, shared context, claims, risks, questions, relevant findings, and suggested tests.

`memory/graph/` may contain optional durable knowledge graph artifacts compiled from plan claims, agent reports, reviews, patches, risks, and questions. Missing graph sources should produce warnings or empty graph sections, not fail the run.

`dev_team_status` may include memory health, claims summary, discovery, and graph data when those files exist. `dev_team_dashboard` should expose a compact dashboard view with run `status`, per-agent `currentActivity` and `recentActions`, run-level coordination state, and a knowledge graph. In widget-capable Codex hosts, dashboard-capable tool results include `openai/outputTemplate` and `_meta.widgetData` so the app can render the bundled dashboard card directly. These fields are additive; absence of memory, graph, or dashboard-only fields on older runs is not itself a failure.

## Native Sidebar Agent Lifecycle

When the user wants agents to appear in the Codex sidebar, manage native custom subagents through host tools rather than `dev_team_start`.

- Open only specialists that materially advance the current task, plus explicit user requests.
- Prefer a compact active team of 3-6 sidebar agents; do not open the whole role catalog unless the user explicitly accepts the host thread limit tradeoff.
- Before opening a new sidebar agent at the limit, close completed agents that have already returned a handoff.
- Do not close agents that are still running, own an unreviewed patch/finding, or are in an active user conversation.
- Ask each native sidebar agent to finish with a compact handoff: outcome, touched or inspected files, residual risks, and recommended next specialist.
- Treat `dev_team_agent_roster.native_sidebar_lifecycle` as the machine-readable policy for host-side open/close decisions.
- MCP live agents remain background `codex exec` workers; calling them starts a follow-up run with context, not an interactive message to the already-running process.

## Tool Sequence

1. Call `dev_team_preflight` with the absolute current repository path.
2. If team composition is important, call `dev_team_agent_roster`, `dev_team_agent_catalog`, or `dev_team_resolve_agents` and summarize which live agents, historical agents, local skills/subagents, or fallback roles will be used.
3. If the task is broad, risky, or the user asks for a plan first, call `dev_team_plan_only` and summarize `recommended_agents`, `noise_budget`, `context_budget_report`, `token_ledger_report`, `quality_gates`, `parallel_safety_score`, `risk_level`, `tasks`, selected `agent_resolution`, and `blocked_reason`.
4. If the user asks for review without changes, call `dev_team_audit` instead of starting implementation agents.
5. If preflight is healthy and implementation is desired, call `dev_team_start`.
   - Default to `wait_for_completion: false` so the tool returns a `run_id` quickly.
   - Use `max_agents: 2` unless the user explicitly asks for more.
   - Use `auto_review: true` for implementation tasks.
   - Leave `auto_integrate: false` unless the user explicitly asked to apply changes automatically.
   - Surface the returned dashboard widget/card when the host renders one.
6. Poll `dev_team_status` with the `run_id` until the run status is `completed`, `failed`, `partial`, `reviewed`, `integrated`, or `aborted`.
7. Call `dev_team_dashboard` immediately after start and during polling when a visible progress surface is useful. Prefer showing the widget/card over asking the user to type a command; summarize agent status, agent roles, `currentActivity`, `recentActions`, coordination state, `agent_quality_report`, and graph/discovery warnings when present.
8. If the app or MCP server restarted, call `dev_team_list_runs` when the `run_id` is unknown, then call `dev_team_resume` for the selected run before deciding what to do next.
9. If status or resume reports stalled, interrupted, failed, or stale workers, inspect preserved patches and use `dev_team_retry_agent` or `dev_team_rebase_agent` for one claimed shard.
10. If reviews were not run, call `dev_team_review`; use `dev_team_patch_score` and `dev_team_verify` when risk or verification evidence is needed.
11. Before integration, call `dev_team_integrate_dry_run` for selected patches. Use `dev_team_conflicts` when partial, retried, old, or likely-overlapping patches need an extra conflict check.
12. Present the dry-run, patch score, review, conflict, and verification summary to the user.
13. Call `dev_team_integrate_apply` only when the user requested integration or already authorized the dry-run result. Use direct `dev_team_integrate` only for compatibility or explicit user preference.

## Required Inputs

Always pass an absolute `repo_path`. If the current thread is already in a repository, use that workspace root.

When starting a run, pass:

```json
{
  "repo_path": "/absolute/path/to/repo",
  "task": "The user's requested engineering task",
  "max_agents": 2,
  "agent_budget_mode": "auto",
  "context_budget": "standard",
  "quality_profile": "standard",
  "preferred_agent_ids": [],
  "auto_review": true,
  "auto_integrate": false,
  "wait_for_completion": false
}
```

## Lifecycle Recovery Tools

Use these tools when durable run state matters:

- `dev_team_list_runs`: read recent runs for a repository, including effective lifecycle state and retry/review/integration hints.
- `dev_team_resume`: reconstruct status from `.codex-team/runs/<run_id>/` after a restart or lost in-process state.
- `dev_team_retry_agent`: rerun one failed, stalled, or interrupted implementation shard in a fresh worktree while keeping the previous attempt inspectable.
- `dev_team_rebase_agent`: rebase one saved patch onto fresh `HEAD` in a temporary worktree.
- `dev_team_conflicts`: dry-run selected complete or partial patches against the main checkout before integration.
- `dev_team_integrate_dry_run`: stage selected patches in a temporary integration worktree and produce a final patch.
- `dev_team_integrate_apply`: apply an approved dry-run final patch into the main checkout.
- `dev_team_verify`: run verification commands in agent, integration, or main checkouts.
- `dev_team_patch_score`: score patches for risk before integration.
- `dev_team_contracts`: read or update run-local shared API, DB, UI, auth, and env contracts.
- `dev_team_agent_catalog`: list local specialist profiles from Codex skills and Claude-style agent files plus bundled fallback roles.
- `dev_team_agent_roster`: list callable specialists, live agents from the current run, and historical agents from previous runs with ready-to-use chat prompts.
- `dev_team_resolve_agents`: select task-specific agent profiles before a run.
- `dev_team_dashboard`: show a dashboard-ready widget/status view with per-agent current activity, recent actions, run coordination state, and a knowledge graph derived from `memory/graph/`.

Treat `stalled` and `interrupted` as recovery states. They may appear as an `effective_status` or nested recovery field while the original top-level `status` remains backward-compatible. Do not clean up worktrees or delete run directories until the user has decided whether to review, retry, integrate, or discard preserved partial patches.

## When To Avoid Parallel Implementation

Prefer one implementer when:

- the task is small;
- the repository has no committed `HEAD`;
- the requested change touches one tight file cluster;
- preflight reports a dirty working tree and the user did not explicitly allow it;
- the plan cannot produce disjoint ownership paths.

Use parallel agents freely for:

- codebase exploration;
- test gap analysis;
- PR review by concern;
- independent feature slices with clear file ownership.

## User Updates

Keep updates short and practical:

- Tell the user the `run_id`.
- Say whether implementation is still running, completed, partial, failed, stalled, interrupted, reviewed, integrated, or aborted.
- Use `dev_team_dashboard` details when dashboard-style progress is requested: current agent activity, recent actions, coordination state, and graph warnings.
- Highlight patch paths, partial patch paths, retry actions, conflict checks, review verdicts, and verification results.
- Highlight plan-only risk, run cost/noise budget, context budget savings, token ledger estimates, quality gates, patch scores, integration dry-run status, rebase status, and contract changes when those tools are used.
- Mention memory health, claim, discovery, or graph warnings when `dev_team_status` or `dev_team_dashboard` reports them.

Do not paste raw JSONL logs unless the user asks. Summarize them.
