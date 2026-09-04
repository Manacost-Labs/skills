# Upstream skills roadmap

This catalog uses additive, reviewed imports. A source is not copied merely
because it appears in a link list: the skill must have a clear server or
project use, a compatible license, a pinned revision, and a verification path.

## Adopted in this slice

| Source | Decision | Why |
| --- | --- | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | Adapted three workflows | Adds design-before-edit, executable plans, and focused review without installing a second global policy. |
| [mattpocock/skills/grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) | Adapted one workflow | Useful for domain clarification; the upstream stub names a vendor skill that is not present here, so the local version is self-contained. |
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Added opt-in server-map workflow | Provides visual HTML/JSON/report outputs while keeping code-only extraction, source scope, and generated output explicit. |

## Deferred by scope or overlap

| Source | Decision | Next condition |
| --- | --- | --- |
| [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill) | Do not load into the server profile | Review as a frontend-only skill after selecting a project and its design system; it is a large marketing/UI rule set. |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Do not import globally | Add only for an approved Obsidian vault; Graphify's `--obsidian` output is not a reason to alter all server agents. |
| [crewAIInc/skills](https://github.com/crewAIInc/skills) | Project-scoped only | Enable when a CrewAI repository is identified and its installed version is verified. |
| [anthropics/skills/webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Deferred | Existing QA/browser skills cover much of the server profile; add a Playwright-specific variant when a project needs its helper scripts. |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | Deferred | Install the CLI only for a browser-automation project; its current skill is a versioned discovery stub. |
| `skills.sh` TypeScript/Tailwind/shadcn/find-skills links | Not imported from the links alone | Resolve the canonical GitHub repository, revision, license, and overlap first; do not run `npx skills add` implicitly. |
| Anthropic Claude Code Agent Development | Deferred | Review the current directory contents and license, then select only practices not already covered by this policy. |

The imported material is adapted, not a second policy source. Local
`AGENTS.md`, project rules, security boundaries, and quality gates remain
authoritative.
