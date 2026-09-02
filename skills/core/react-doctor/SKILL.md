---
name: react-doctor
description: Use after editing React code, before shipping frontend changes, or when asked to diagnose React performance, correctness, lint, accessibility, dead code, or architecture issues.
---

# React Doctor

React Doctor is installed globally:

```bash
/usr/bin/react-doctor --help
```

Source repo:

`/opt/ai-agent-resources/repos/react-doctor`

Canonical upstream skill:

`/opt/ai-agent-resources/repos/react-doctor/skills/react-doctor/SKILL.md`

After React changes, prefer:

```bash
/usr/bin/react-doctor --no-telemetry --scope changed --verbose
```

For a full project scan:

```bash
/usr/bin/react-doctor --no-telemetry --verbose
```

If this wrapper and the upstream skill differ, read the upstream skill and follow the newer project-specific guidance.
