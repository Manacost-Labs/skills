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

## Operating contract

At the beginning of work:

1. identify the project and read its nearest `AGENTS.md`;
2. select one profile from `profiles/`;
3. load only the listed skills needed for the task;
4. check the project worktree before changing files;
5. run the project quality gate before handing work back.

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
commands are read-only.

## Safe migration

Import is additive. A skill moves through these states:

`discovered` → `reviewed` → `canonical` → `project-enabled` → `legacy-copy-removed`

Only the last state permits removing a project-local copy, and only in a
separate change after the project has passed its own checks. Conflicting files
keep explicit namespaces until a human chooses the winning version.

## External catalogs

Vendor and platform catalogs remain dependencies, not copied source. They are
listed in `registry.yaml` and must not be silently edited or vendored into this
repository. Local project skills are the first candidates for canonicalization.
