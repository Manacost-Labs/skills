---
name: wrangler
description: Use Cloudflare Wrangler to develop, validate, deploy, observe, and roll back Workers and their KV, R2, D1, Vectorize, Hyperdrive, AI, Queue, Workflow, Pipeline, Container, Pages, and Secrets Store bindings. Use before writing or running Wrangler commands, changing wrangler.jsonc, managing environments or secrets, or troubleshooting a Worker deployment.
---

# Wrangler CLI

Treat Wrangler flags, resource limits, configuration fields and platform availability as version-sensitive. Check the installed version and current official Cloudflare documentation before writing commands.

## Workflow

1. Read the repository rules and determine whether the task is read-only, staging or production. Do not infer deployment permission from a request to inspect or configure.
2. Run `npx wrangler --version` from the owning Worker repository. Prefer the project-pinned Wrangler version; do not install or upgrade it silently.
3. Read only the relevant guide:
   - configuration, environments, bindings, types and local development: [references/configuration.md](references/configuration.md);
   - KV, R2, D1 and other managed resources: [references/resources.md](references/resources.md);
   - validation, deployment, logs, versions and rollback: [references/deploy-and-debug.md](references/deploy-and-debug.md).
4. Retrieve current syntax from [official Wrangler documentation](https://developers.cloudflare.com/workers/wrangler/) or the installed `node_modules/wrangler/config-schema.json`. Do not rely on remembered flags.
5. Inspect the existing `wrangler.jsonc`, package scripts, lockfile and deployment workflow before proposing a command. Reuse the repository's environment names and conventions.
6. Keep secrets out of command arguments, source, shell history and logs. Use interactive secret input or an approved CI secret provider.
7. Validate locally and with `wrangler deploy --dry-run`; regenerate binding types after configuration changes.
8. Deploy only the exact reviewed commit to the authorized environment. Record the version and verify the actual route, logs and dependent resources.
9. Roll back through Wrangler versions or the project deployment workflow. Cache purge, secret deletion and resource deletion are not rollback plans.

## Safe defaults

- Prefer `wrangler.jsonc` and a pinned Wrangler dependency in the owning repository.
- Require an explicit `compatibility_date` supported by the project; do not advance it incidentally.
- Use separate staging and production environments with explicit non-secret bindings.
- Treat `--remote`, resource create/delete, D1 migrations, secret mutation and deploy as external state changes.
- Run destructive resource commands only after resolving an exact name/ID and confirming recovery options.
- Use `wrangler types` after binding changes and keep generated types synchronized with configuration.
- Use `wrangler tail` with bounded filters and duration; never expose request bodies, authorization headers or personal data.

## Evidence

Report the installed Wrangler version, changed configuration, dry-run result, target environment, deployed version/commit, route checks and rollback version. Separate commands that were executed from commands shown only as recommendations.

## Hard stops

- Do not run `wrangler deploy`, `delete`, remote D1 mutation, resource deletion or secret mutation without task authorization.
- Do not install `wrangler@latest` into an existing project without dependency-review approval and a lockfile diff.
- Do not place token or secret values in command-line arguments, Git, issues, logs or generated configuration.
- Do not invent binding IDs, account IDs, routes, environment names or compatibility flags.
- Do not use Wrangler or Cloudflare controls to bypass access control, WAF, Turnstile or rate limits.
