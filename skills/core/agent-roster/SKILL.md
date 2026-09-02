---
name: agent-roster
description: Show and invoke Codex Dev Team subagents, including static specialist roles, live run agents, historical agents, and backslash shortcuts like \product-designer, \team, or \last product-designer. Use when the user asks to see old subagents, current working agents, or call a specific specialist such as Product Designer.
---

# Codex Dev Team Agent Roster

Use this skill when the user wants to see or call a specific Codex Dev Team specialist.

## Default Flow

1. Call `dev_team_agent_roster` with the absolute repository path.
2. If the user names a specialist, pass their wording as `query`.
3. Show Live agents first, then Available agents, then Historical agents.
4. If the user asks to call a specialist, start a one-agent run:

```json
{
  "repo_path": "/absolute/path/to/repo",
  "task": "The user's requested work",
  "max_agents": 1,
  "planning_mode": "simple",
  "preferred_agent_ids": ["product-designer"],
  "auto_review": true,
  "auto_integrate": false,
  "wait_for_completion": false
}
```

Use the matching `preferred_agent_ids` value from `dev_team_agent_roster.callable_agents[].id`.

## Dashboard Agent Picker

When the dashboard shows Agent Picker, treat it as a picker for Dev Team workflow shortcuts, not as a replacement for native Codex agent triggering. The sections are:

- **Live agents**: running or recently active workers from current runs, with follow-up shortcuts when available.
- **Available agents**: callable specialist roles, with shortcuts like `\product-designer`.
- **Historical agents**: agents from previous runs, with shortcuts like `\last product-designer`.

`@` remains the native Codex trigger for installed custom subagents. Agent Picker helps the user choose the backslash shortcut that should be routed through `dev_team_route`.

When widget tool calls are available, the dashboard picker can call `dev_team_route` directly:

- **Plan**: route the selected shortcut with `mode: "plan_only"`.
- **Run**: route the selected shortcut with `mode: "start"`.
- **Copy**: copy or show the composed backslash command for chat fallback.

## Chat Shortcut Handling

Treat backslash commands as Codex Dev Team plugin shortcuts:

- `\product-designer <task>`: call `dev_team_route` with `mode: "start"` to start a one-agent run with the matching id.
- `\team <task>`: call `dev_team_route` with `mode: "start"` to use the normal team workflow with resolver-selected roles.
- `\last product-designer <task>`: call `dev_team_route` with `mode: "start"` so it can attach the latest matching live or historical context when available.

Do not treat `@product-designer` as a Codex Dev Team shortcut. `@` belongs to the native Codex custom-agent trigger after TOML installation; the plugin shortcut namespace is `\`.

## Important Behavior

Bundled specialist roles are generated as native Codex custom-agent TOML files under `codex-agents/`. They become visible to Codex as custom subagents after running `npm run install:codex-agents --prefix plugins/codex-dev-team` and starting a new thread.

Live agents are local `codex exec` worker processes. Calling a live agent from chat starts a follow-up run with the same role and run context; it does not attach an interactive message to the already-running process.

## Native Sidebar Lifecycle

When the user asks to show agents in the right sidebar, use native host subagent tools if available. Keep the sidebar as an active team, not as the whole catalog:

- Open specialists that match the current task or an explicit user request.
- Keep at most 6 open sidebar agents unless the host reports a different limit.
- Close completed agents after they provide a handoff and their result is summarized or integrated.
- Do not close running agents, agents with unreviewed patches/findings, or agents the user is actively addressing.
- If the host returns a thread limit error, close completed low-relevance agents first, then retry the needed specialist.
- Use `dev_team_agent_roster.native_sidebar_lifecycle` as the policy source when presenting or automating open/close choices.

If `preferred_agent_ids` does not resolve, report the error and ask the user to choose an id from `dev_team_agent_roster`; do not let the workflow silently choose another role.

For Product Designer, prefer `preferred_agent_ids: ["product-designer"]`.
