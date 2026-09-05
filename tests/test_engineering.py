"""Executable contracts for task routing and risk-based verification."""

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class EngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "engineering", ROOT / "scripts/engineering.py"
        )
        cls.e = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.e)
        cls.policy = cls.e.load_policy()

    def test_policy_and_roles(self):
        self.e.validate_policy(self.policy)
        models = self.e.resolve_models(self.policy)
        # Golden acceptance values are test expectations, not a runtime model catalog.
        self.assertEqual(models["lead"], "gpt-5.6-sol")
        self.assertEqual(models["worker"], "gpt-5.6-terra")
        self.assertEqual(models["scout"], "gpt-5.6-luna")
        self.assertEqual(models["architect"], "gpt-6-astra")
        self.assertNotEqual(models["lead"], models["worker"])
        self.assertEqual(models["lead"], models["high_reviewer"])
        self.assertEqual(models["architect"], models["critical_reviewer"])
        for role in self.policy["roles"].values():
            self.assertIn(role["tier"], ("judgment", "routine", "bulk"))
        bad = copy.deepcopy(self.policy)
        bad["roles"]["lead"]["tier"] = "unknown"
        with self.assertRaises(ValueError):
            self.e.validate_policy(bad)

    def test_risk_cannot_be_lowered_by_hint(self):
        self.assertEqual(self.e.classify(["docs/usage.md"], "typo", "LOW"), "LOW")
        self.assertEqual(self.e.classify(["src/business.py"], "", "LOW"), "MEDIUM")
        for path in (
            "src/auth/login.ts",
            "migrations/003.sql",
            "AGENTS.md",
            ".github/workflows/ci.yml",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.e.classify([path], "", "LOW"), "HIGH")
        self.assertEqual(
            self.e.classify(
                ["src/payments/charge.go"], "production irreversible", "LOW"
            ),
            "CRITICAL",
        )
        self.assertEqual(self.e.classify([], "", "auto"), "MEDIUM")

    def test_policy_rejects_removed_required_safeguards(self):
        for level in ("HIGH", "CRITICAL"):
            for mutation in (
                {"checks": ["security"]},
                {"reviewer": None},
                {"review_required": "true"},
                {"full_gate": 1},
            ):
                bad = copy.deepcopy(self.policy)
                bad["risk"][level].update(mutation)
                with (
                    self.subTest(level=level, mutation=mutation),
                    self.assertRaises(ValueError),
                ):
                    self.e.validate_policy(bad)
        bad = copy.deepcopy(self.policy)
        bad["complexity"]["trivial"]["scout"] = True
        with self.assertRaises(ValueError):
            self.e.validate_policy(bad)

    def test_duplicate_profile_keys_are_rejected(self):
        self.e.validate_profile("profile: fixture\nactivation: on-demand\navailable:\n")
        with self.assertRaises(ValueError):
            self.e.validate_profile(
                "activation: on-demand\navailable:\nactivation: available-on-demand\n"
            )

    def test_global_architecture_review_is_distinct_from_correctness_review(self):
        result = self.e.route(ROOT, "", "trivial", "LOW", ["AGENTS.md"], "server", [])
        self.assertEqual(result["risk"], "HIGH")
        self.assertTrue(result["architecture_review_required"])
        self.assertIsNotNone(result["scout"])
        self.assertNotEqual(result["reviewer"], result["architecture_reviewer"])

    def test_skill_budget_and_explicit_selection(self):
        for complexity, limit in (("trivial", 1), ("normal", 3), ("complex", 5)):
            route = self.e.route(
                ROOT,
                "fix test API architecture CI graph",
                complexity,
                "auto",
                [],
                "server",
                [],
            )
            self.assertLessEqual(len(route["skills"]), limit)
            self.assertEqual(route["scout"] is not None, complexity != "trivial")
        with self.assertRaises(ValueError):
            self.e.route(ROOT, "", "normal", "auto", [], "server", ["unknown/skill"])
        selected = "engineering/diagnosing-bugs"
        result = self.e.route(
            ROOT, "", "trivial", "LOW", ["docs/a.md"], "server", [selected]
        )
        self.assertEqual(result["skills"][0]["id"], selected)

    def test_router_does_not_match_keywords_inside_other_words(self):
        result = self.e.route(
            ROOT,
            "precision about capital letters",
            "normal",
            "LOW",
            ["docs/text.md"],
            "server",
            [],
        )
        self.assertEqual(result["skills"], [])

    def test_profiles_are_catalogs_and_precedence_matches(self):
        for path in (ROOT / "profiles").glob("*.yaml"):
            content = path.read_text()
            self.assertIn("activation: on-demand", content)
            self.assertNotIn("\nload:", content)
        agents = (ROOT / "AGENTS.md").read_text()
        positions = [
            agents.index(f"{i}. {label}")
            for i, label in enumerate(self.policy["authority"], 1)
        ]
        self.assertEqual(positions, sorted(positions))

    def test_brief_rejects_missing_unknown_and_oversized_fields(self):
        brief = {name: [] for name in self.policy["brief"]["list_fields"]}
        brief["goal"] = "Fix one scoped regression"
        self.e.validate_brief(brief, self.policy)
        for invalid in (
            {},
            {**brief, "extra": True},
            {**brief, "goal": "word " * 601},
            {**brief, "recommended_skills": ["x"] * 5},
        ):
            with self.assertRaises(ValueError):
                self.e.validate_brief(invalid, self.policy)

    def test_verify_selects_risk_and_reports_skipped_checks(self):
        config = {
            "version": 1,
            "checks": [
                {
                    "id": "focused",
                    "argv": ["true"],
                    "min_risk": "LOW",
                    "covers": ["focused"],
                },
                {
                    "id": "full",
                    "argv": ["true"],
                    "min_risk": "HIGH",
                    "covers": ["lint", "types", "unit", "integration", "security"],
                },
            ],
        }
        low = self.e.verification_plan(config, "LOW", [])
        self.assertEqual([x["id"] for x in low["run"]], ["focused"])
        self.assertEqual(low["skip"][0]["id"], "full")
        self.assertEqual(len(self.e.verification_plan(config, "HIGH", [])["run"]), 2)
        incomplete = copy.deepcopy(config)
        incomplete["checks"][1]["covers"].remove("security")
        with self.assertRaisesRegex(ValueError, "security"):
            self.e.verification_plan(incomplete, "HIGH", [])
        for bad in (
            {"version": 1, "checks": []},
            {"checks": [{"id": "x", "argv": "echo unsafe"}]},
        ):
            with self.assertRaises(ValueError):
                self.e.verification_plan(bad, "LOW", [])

    def test_missing_tool_and_failed_check_are_not_success(self):
        for argv in (
            ["manacost-tool-that-does-not-exist"],
            [sys.executable, "-c", "raise SystemExit(7)"],
        ):
            with tempfile.TemporaryDirectory() as directory:
                report = self.e.run_checks(
                    Path(directory), {"run": [{"id": "test", "argv": argv}], "skip": []}
                )
                self.assertFalse(report["ok"])

    def test_stack_detection_and_nonmatching_check_fails_required_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "go.mod").touch()
            self.assertEqual(self.e.detect_stacks(project), ["go"])
            config = {
                "version": 1,
                "checks": [
                    {
                        "id": "node",
                        "argv": ["true"],
                        "covers": ["focused"],
                        "stacks": ["node"],
                    }
                ],
            }
            with self.assertRaises(ValueError):
                self.e.verification_plan(config, "LOW", [], ["go"])

    def test_zero_sha_scans_initial_committed_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)

            def git(*args):
                return subprocess.run(
                    ["git", *args], cwd=project, check=True, capture_output=True
                )

            git("init", "-q")
            git("config", "user.email", "test@example.invalid")
            git("config", "user.name", "Test")
            (project / "first.md").write_text("initial")
            git("add", "first.md")
            git("commit", "-qm", "initial")
            self.assertEqual(self.e.changed_paths(project, "0" * 40), ["first.md"])
            self.assertEqual(self.e.changed_paths(project), [])

    def test_whitespace_gate_checks_committed_and_index_changes(self):
        config = json.loads((ROOT / ".ai/verify.json").read_text())
        argv = next(c["argv"] for c in config["checks"] if c["id"] == "whitespace")
        argv = [str(ROOT / a) if (ROOT / a).is_file() else a for a in argv]
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=project)

            git("init", "-q")
            git("config", "user.email", "test@example.invalid")
            git("config", "user.name", "Test")
            path = project / "sample.md"
            path.write_text("clean\n")
            git("add", ".")
            git("commit", "-qm", "initial")
            env = {
                **os.environ,
                "VERIFY_BASE": git("rev-parse", "HEAD").decode().strip(),
            }

            def check():
                return subprocess.run(
                    argv, cwd=project, env=env, capture_output=True
                ).returncode

            self.assertEqual(check(), 0)
            path.write_text("bad \n")
            git("add", ".")
            git("commit", "-qm", "committed whitespace")
            self.assertNotEqual(check(), 0, "CI must inspect the committed diff")
            env["VERIFY_BASE"] = "0" * 40
            self.assertNotEqual(
                check(), 0, "new-branch base must inspect the initial tree"
            )
            path.write_text("clean\n")
            git("add", ".")
            git("commit", "-qm", "clean again")
            env["VERIFY_BASE"] = "HEAD"
            self.assertEqual(check(), 0)
            path.write_text("bad \n")
            git("add", ".")
            path.write_text("clean\n")
            self.assertNotEqual(
                check(), 0, "clean worktree must not hide staged whitespace"
            )
            git("add", ".")
            self.assertEqual(check(), 0)

    def test_ci_calls_same_entrypoint(self):
        workflow = (ROOT / ".github/workflows/verify.yml").read_text()
        self.assertIn("run: make verify", workflow)
        self.assertNotIn("make test", workflow)
        self.assertIn("verify:", (ROOT / "Makefile").read_text())

    def test_operational_policy_uses_roles_not_scattered_identifiers(self):
        for name in (
            "AGENTS.md",
            "policies/engineering.json",
            "scripts/skillctl",
            "skills/core/dev-team/SKILL.md",
            "skills/engineering/addy/using-agent-skills/SKILL.md",
        ):
            with self.subTest(path=name):
                self.assertNotRegex((ROOT / name).read_text(), r"\bgpt-\d[\w.-]+")


if __name__ == "__main__":
    unittest.main()
