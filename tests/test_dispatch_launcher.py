"""Launcher runner is a test double in every test; real Codex is forbidden."""

import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
launcher = importlib.import_module("dispatch_launcher")
engineering = importlib.import_module("engineering")
routing = importlib.import_module("model_routing")


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.state = self.directory / "attempts.json"
        models = engineering.resolve_models(engineering.load_policy())
        self.caps = {m: ["low", "medium", "high", "xhigh"] for m in models.values()}
        self.project = self.directory / "project"
        self.project.mkdir()
        self.plan = routing.build_plan(
            self.project, "LOW", "trivial", capabilities=self.caps
        )
        self.brief = {k: [] for k in engineering.load_policy()["brief"]["list_fields"]}
        self.brief["goal"] = "A focused bounded change"
        self.snapshot = "source-revision-one"
        patcher = patch.object(
            launcher, "snapshot", side_effect=lambda _: self.snapshot
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def fake(self, outcome="completed", code=0):
        def run(argv, **kwargs):
            kwargs["stdout"].write(
                json.dumps({"outcome": outcome, "brief": self.brief}).encode()
            )
            return type("Result", (), {"returncode": code})()

        return Mock(side_effect=run)

    def call(self, **kwargs):
        return launcher.launch(
            self.plan, "Fix scoped text", state_path=self.state, **kwargs
        )

    def test_default_dry_run_never_starts_or_writes(self):
        runner = Mock(side_effect=AssertionError("must not execute"))
        report = self.call(runner=runner)
        self.assertEqual(report["status"], "dry_run")
        self.assertFalse(self.state.exists())
        runner.assert_not_called()

    def test_argv_preserves_untrusted_task_as_one_argument(self):
        task = '--config unsafe=true; $(touch /tmp/should-not-exist) `id` "x"\nnext'
        argv = launcher.codex_argv(self.plan["stages"][0], task)
        self.assertEqual(argv[:3], ["codex", "exec", "-m"])
        self.assertEqual(argv[-2], "--")
        self.assertEqual(argv[-1], task)
        self.assertIn('model_reasoning_effort="medium"', argv)
        self.assertIn("features.multi_agent=false", argv)
        self.assertIn("read-only", argv)

    def test_execute_requires_stage_and_verified_capabilities(self):
        with self.assertRaises(ValueError):
            self.call(execute=True)
        plan = routing.build_plan(self.project, "HIGH", "normal")
        runner = Mock()
        result = launcher.launch(
            plan,
            "task",
            execute=True,
            stage_id="scout",
            state_path=self.state,
            runner=runner,
        )
        self.assertEqual(result["status"], "blocked")
        runner.assert_not_called()

    def test_attempt_is_reserved_before_process_and_never_retried(self):
        runner = self.fake()
        report = self.call(execute=True, stage_id="worker", runner=runner)
        self.assertEqual(report["status"], "awaiting_acceptance")
        self.assertEqual(
            json.loads(self.state.read_text())["stages"]["worker"]["attempts"], 1
        )
        result = self.call(execute=True, stage_id="worker", runner=runner)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o600)

    def test_review_failure_blocks_without_fallback(self):
        self.plan = routing.build_plan(
            self.project, "HIGH", "normal", capabilities=self.caps
        )
        runner = self.fake()
        for stage in ("scout", "lead"):
            self.call(execute=True, stage_id=stage, runner=runner)
            self.assertEqual(self.call(accept_stage=stage)["status"], "accepted")
        failed = Mock(side_effect=FileNotFoundError("no executable"))
        result = self.call(execute=True, stage_id="high_reviewer", runner=failed)
        self.assertEqual(result["status"], "blocked")
        self.call(execute=True, stage_id="high_reviewer", runner=failed)
        self.assertEqual(failed.call_count, 1)

    def test_dependencies_need_explicit_acceptance_and_fresh_source(self):
        self.plan = routing.build_plan(
            self.project, "HIGH", "normal", capabilities=self.caps
        )
        runner = self.fake()
        self.assertEqual(
            self.call(execute=True, stage_id="lead", runner=runner)["status"], "blocked"
        )
        self.call(execute=True, stage_id="scout", runner=runner)
        self.assertEqual(
            self.call(execute=True, stage_id="lead", runner=runner)["status"], "blocked"
        )
        self.snapshot = "changed-source"
        self.assertEqual(self.call(accept_stage="scout")["status"], "blocked")
        self.assertEqual(runner.call_count, 1)

    def test_failed_or_unstructured_output_is_not_pass(self):
        for outcome, code in (("changes_required", 0), ("completed", 2)):
            self.state = self.directory / f"{outcome}-{code}.json"
            self.assertEqual(
                self.call(
                    execute=True, stage_id="worker", runner=self.fake(outcome, code)
                )["status"],
                "blocked",
            )
            self.assertEqual(self.call(accept_stage="worker")["status"], "blocked")

    def test_duplicate_response_fields_are_not_accepted(self):
        def duplicate_outcome(argv, **kwargs):
            kwargs["stdout"].write(
                (
                    '{"outcome":"changes_required","outcome":"completed","brief":'
                    + json.dumps(self.brief)
                    + "}"
                ).encode()
            )
            return type("Result", (), {"returncode": 0})()

        result = self.call(execute=True, stage_id="worker", runner=duplicate_outcome)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.call(accept_stage="worker")["status"], "blocked")

    def test_task_change_symlink_and_malformed_state_are_rejected(self):
        self.call(execute=True, stage_id="worker", runner=self.fake())
        with self.assertRaises(ValueError):
            launcher.launch(
                self.plan,
                "different task",
                execute=True,
                stage_id="worker",
                state_path=self.state,
                runner=self.fake(),
            )
        target = self.directory / "target.json"
        target.write_text("untouched")
        link = self.directory / "link.json"
        link.symlink_to(target)
        with self.assertRaises((ValueError, OSError)):
            launcher.launch(
                self.plan,
                "task",
                execute=True,
                stage_id="worker",
                state_path=link,
                runner=self.fake(),
            )
        self.assertEqual(target.read_text(), "untouched")

    def test_durable_reservation_and_lock_prevent_recursive_launch(self):
        def runner(argv, **kwargs):
            saved = json.loads(self.state.read_text())
            self.assertEqual(saved["stages"]["worker"]["status"], "running")
            with self.assertRaisesRegex(ValueError, "another stage"):
                self.call(execute=True, stage_id="worker", runner=Mock())
            return self.fake()(argv, **kwargs)

        self.assertEqual(
            self.call(execute=True, stage_id="worker", runner=runner)["status"],
            "awaiting_acceptance",
        )

    def test_review_is_fresh_readonly_even_with_write_permission(self):
        plan = routing.build_plan(
            self.project, "HIGH", "normal", capabilities=self.caps
        )
        self.assertIn(
            "workspace-write", launcher.codex_argv(plan["stages"][1], "task", True)
        )
        self.assertIn(
            "read-only", launcher.codex_argv(plan["stages"][-1], "task", True)
        )
        self.assertNotIn(
            "resume", launcher.codex_argv(plan["stages"][-1], "task", True)
        )

    def test_oversized_invalid_output_and_timeout_consume_attempt(self):
        for label in ("large", "invalid", "timeout"):
            self.state = self.directory / f"{label}.json"

            def runner(argv, **kwargs):
                if label == "timeout":
                    raise subprocess.TimeoutExpired(argv, 1)
                kwargs["stdout"].write(b"x" * (20000 if label == "large" else 1))
                return type("Result", (), {"returncode": 0})()

            self.assertEqual(
                self.call(execute=True, stage_id="worker", runner=runner)["status"],
                "blocked",
            )
            self.assertEqual(
                self.call(execute=True, stage_id="worker", runner=Mock())["status"],
                "blocked",
            )

    def test_untrusted_state_and_project_local_ledger_rejected(self):
        self.state.write_text('{"schema":1,"binding":"forged","stages":{}}')
        self.state.chmod(0o600)
        with self.assertRaises(ValueError):
            self.call(execute=True, stage_id="worker", runner=self.fake())
        with self.assertRaises(ValueError):
            launcher.launch(
                self.plan,
                "task",
                execute=True,
                stage_id="worker",
                state_path=self.project / "state.json",
                runner=self.fake(),
            )
        self.project.chmod(0o700)
        outside = self.directory / "elsewhere"
        outside.mkdir(mode=0o700)
        with self.assertRaises(ValueError):
            launcher.check_state_path(outside / "../project/ledger.json", self.project)

    def test_shell_entrypoint_dry_run_and_execute_use_fake_only(self):
        # The PATH sentinel makes accidental real Codex impossible, even if the
        # launcher regresses and starts a process in dry-run mode.
        bin_dir = self.directory / "bin"
        bin_dir.mkdir()
        sentinel = self.directory / "fake-called"
        fake = bin_dir / "codex"
        response = json.dumps({"outcome": "completed", "brief": self.brief})
        fake.write_text(
            f"#!{sys.executable}\nfrom pathlib import Path\nPath({str(sentinel)!r}).touch()\nprint({response!r})\n"
        )
        fake.chmod(0o755)
        env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}

        def git(*args):
            subprocess.run(
                ["git", *args], cwd=self.project, check=True, capture_output=True
            )

        git("init", "-q")
        git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            "fixture",
        )
        caps = self.directory / "capabilities.json"
        caps.write_text(json.dumps({"models": self.caps}))
        task_file = self.directory / "task.txt"
        task_file.write_text("literal --config x; $(not-a-command) `also-literal`")
        command = [
            str(ROOT / "scripts/manacost-dispatch"),
            str(self.project),
            "--task-file",
            str(task_file),
            "--capabilities",
            str(caps),
            "--state",
            str(self.state),
            "--stage",
            "worker",
        ]
        dry = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertEqual(json.loads(dry.stdout)["status"], "dry_run")
        self.assertFalse(sentinel.exists())
        self.assertFalse(self.state.exists())
        result = subprocess.run(
            [*command, "--execute"], env=env, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "awaiting_acceptance")
        self.assertTrue(sentinel.exists())
        again = subprocess.run(
            [*command, "--execute"], env=env, capture_output=True, text=True
        )
        self.assertEqual(again.returncode, 2)

    def test_dry_run_existing_state_is_read_only_and_handoff_is_bounded(self):
        self.call(execute=True, stage_id="worker", runner=self.fake())
        original = self.state.read_bytes()
        self.call(stage_id="worker", runner=Mock())
        self.assertEqual(original, self.state.read_bytes())
        with self.assertRaises(ValueError):
            launcher.prompt_for(self.plan["stages"][0], "x" * 16384, self.brief)


class LauncherIntegrationTests(unittest.TestCase):
    """Exercise real local Git/process behavior, but never a Codex executable."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.repo = self.directory / "repo"
        self.project = self.repo / "subproject"
        self.project.mkdir(parents=True)
        self.source = self.project / "module.py"
        self.source.write_text("value = 1\n")
        self.git("init", "-q")
        self.git("add", "subproject/module.py")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        )
        models = engineering.resolve_models(engineering.load_policy())
        self.capabilities = {
            model: ["low", "medium", "high", "xhigh"] for model in models.values()
        }
        self.brief = {
            key: [] for key in engineering.load_policy()["brief"]["list_fields"]
        }
        self.brief["goal"] = "Fixture handoff"
        self.state = self.directory / "attempts.json"

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def complete(self, argv, **kwargs):
        kwargs["stdout"].write(
            json.dumps({"outcome": "completed", "brief": self.brief}).encode()
        )
        return type("Result", (), {"returncode": 0})()

    def launch(self, plan, **kwargs):
        return launcher.launch(
            plan,
            "Review a fixture",
            state_path=self.state,
            **kwargs,
        )

    def test_review_acceptance_detects_change_from_git_subdirectory(self):
        plan = routing.build_plan(
            self.project, "HIGH", "normal", capabilities=self.capabilities
        )
        for stage in ("scout", "lead", "high_reviewer"):
            result = self.launch(
                plan, execute=True, stage_id=stage, runner=self.complete
            )
            self.assertEqual(result["status"], "awaiting_acceptance")
            if stage != "high_reviewer":
                self.assertEqual(
                    self.launch(plan, accept_stage=stage)["status"], "accepted"
                )
        self.source.write_text("value = 2\n")
        accepted = self.launch(plan, accept_stage="high_reviewer")
        self.assertEqual(accepted["status"], "blocked")

    def test_timeout_terminates_the_started_process_group(self):
        child_pid = self.directory / "child.pid"
        spawner = self.directory / "spawner.py"
        spawner.write_text(
            "import subprocess, sys, time\n"
            "child = subprocess.Popen([sys.executable, '-c', "
            "'import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'])\n"
            "open(sys.argv[1], 'w').write(str(child.pid))\n"
            "time.sleep(60)\n"
        )
        with tempfile.TemporaryFile() as output:
            with self.assertRaises(subprocess.TimeoutExpired):
                launcher.run_stage_process(
                    [sys.executable, str(spawner), str(child_pid)],
                    cwd=self.project,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.DEVNULL,
                    timeout=0.5,
                    check=False,
                )
        self.assertTrue(child_pid.is_file())
        pid = int(child_pid.read_text())
        deadline = time.monotonic() + 1
        while Path(f"/proc/{pid}").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertFalse(Path(f"/proc/{pid}").exists())


if __name__ == "__main__":
    unittest.main()
