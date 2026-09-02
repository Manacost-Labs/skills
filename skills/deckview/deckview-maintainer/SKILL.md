---
name: deckview-maintainer
description: Maintain, optimize, test, document, and release the Deckview Telegram bot and image renderer. Use for any Deckview code, rendering, settings, API, cache, deployment, or repository change; especially before declaring work complete or pushing to production.
---

# Deckview Maintainer

Keep the live bot stable while making small, measurable changes.

## Work safely

1. Read `AGENTS.md` and inspect the working tree before editing.
2. Treat `.env*`, databases, caches, generated images, user uploads, logs, backups, and virtual environments as runtime data. Never commit them.
3. Preserve unrelated edits and other worktrees. Do not reset or overwrite a dirty production tree.
4. Keep the repository root free of Python modules. Extend the matching package under `deckview/`, `image_creator/`, or `tools/`, while keeping Telegram transport, deck resolution, rendering, persistence, and web/API boundaries separate.
5. Add or update tests for every bug fix and behavior change.

## Verify every change

Run the narrowest relevant tests during implementation. Before handoff or push, run:

```bash
sudo -u ubuntu .venv/bin/python -m unittest discover -v
sudo -u ubuntu .venv/bin/python scripts/render_regression_decks.py \
  --output-dir artifacts/reno-regression
```

The Reno regression command must:

- decode and validate one 30-card singleton deck;
- decode and validate one 40-card singleton deck;
- render both decks without missing cards;
- print stage timings and output paths.

Open both generated images and visually check the grid, equal spacing, sideboards, class art, mana curve, and title. Show both images to the user when the interface supports local images.

Read [release-checks.md](references/release-checks.md) before a production deployment or Git push.

## Maintain reusable skills

When a Deckview workflow becomes recurring, fragile, or easy to forget, create or update a repository-local skill under `.agents/skills/`. Use the system `skill-creator` workflow, keep instructions concise, validate the skill, and commit it with the code it governs.

Do not create a skill for one-off facts or duplicate guidance already present here.

## Release

1. Inspect the complete staged diff.
2. Scan staged content for tokens, passwords, cookies, personal data, generated assets, and runtime state.
3. Record test and Reno-render results.
4. Use atomic commits with imperative messages.
5. Push only the intended branch and verify the remote commit.
