---
name: skill-eval-runner
description: Проверяет поведение SKILL.md через воспроизводимые тестовые сценарии и sandbox. Use when a skill needs regression coverage, dry-run validation, or CI-ready evidence beyond a manual chat run.
license: MIT
---

# Skill Eval Runner

`skill-eval-runner` is a local guide for using the upstream `ser` CLI to test
agent skills. The runner executes a skill in a fresh workspace and checks
observable results such as files, output, exit codes, JSON, duration, and token
usage.

## When to use

- a new or changed skill needs a repeatable regression test;
- a manual agent run looked correct but its file or command contract is not
  proven;
- a project needs dry-run or CI evidence for a skill;
- a skill should be checked in an isolated temporary or Docker sandbox.

## Safe workflow

1. Read the nearest project `AGENTS.md` and keep the test workspace narrow.
2. Start with the upstream runner's `dry-run` mode; it does not call an LLM or
   create files on behalf of an agent.
3. Define assertions for the actual contract: expected files, exit code,
   stderr, response markers, JSON shape, and resource limits where supported.
4. Use real model adapters only when the user has approved the provider and
   its costs; keep API keys in the environment and never place them in test
   fixtures or reports.
5. Review generated artifacts and run the project's quality gate after a
   skill change.

The upstream repository documents installation, test YAML, adapters, sandbox
options, and report formats in its README. Install the `ser` package separately
only when the project explicitly needs to execute these evaluations; this
catalog does not install global npm packages implicitly.

## Verification

- test discovery and YAML validation pass in `dry-run` mode;
- assertions cover both success and an expected failure path where practical;
- reports do not contain secrets, cookies, provider credentials, or private
  source data;
- the tested skill remains compatible with the project's own checks.

## Source

This wrapper is based on the upstream [skill-eval-runner](https://github.com/balyakin/skill-eval-runner) CLI README. It is intentionally a local guide because that repository provides a runner and fixtures, not an installable `SKILL.md` package.
