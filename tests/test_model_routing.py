"""Dispatch contracts; no model process or network is used."""

import copy
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
engineering = importlib.import_module("engineering")
routing = importlib.import_module("model_routing")


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.policy = routing.load_policy()
        self.models = engineering.resolve_models(engineering.load_policy())
        self.capabilities = {
            m: ["low", "medium", "high", "xhigh"] for m in self.models.values()
        }

    def plan(self, risk="MEDIUM", complexity="normal", **kwargs):
        return routing.build_plan(
            ROOT, risk, complexity, capabilities=self.capabilities, **kwargs
        )

    def test_five_routes_and_exact_roles(self):
        for risk, complexity, unknown, expected in (
            ("LOW", "trivial", False, [("worker", "medium")]),
            ("MEDIUM", "normal", False, [("worker", "medium")]),
            ("MEDIUM", "normal", True, [("scout", "low"), ("worker", "medium")]),
            ("MEDIUM", "complex", False, [("scout", "low"), ("worker", "medium")]),
            (
                "HIGH",
                "trivial",
                False,
                [("scout", "low"), ("lead", "high"), ("high_reviewer", "high")],
            ),
            (
                "CRITICAL",
                "normal",
                False,
                [("scout", "low"), ("lead", "high"), ("critical_reviewer", "xhigh")],
            ),
        ):
            with self.subTest(risk=risk, complexity=complexity, unknown=unknown):
                plan = self.plan(risk, complexity, unknown_context=unknown)
                self.assertEqual(
                    [(s["role"], s["reasoning_effort"]) for s in plan["stages"]],
                    expected,
                )
                self.assertEqual(plan["status"], "ready")
                for i, stage in enumerate(plan["stages"]):
                    self.assertEqual(stage["model"], self.models[stage["role"]])
                    self.assertEqual(stage["max_attempts"], 1)
                    self.assertEqual(
                        stage["depends_on"],
                        [] if not i else [plan["stages"][i - 1]["id"]],
                    )

    def test_architecture_is_separate_and_never_implements(self):
        plan = self.plan("CRITICAL", architecture=True)
        roles = [s["role"] for s in plan["stages"]]
        self.assertEqual(roles, ["scout", "architect", "lead", "critical_reviewer"])
        self.assertEqual(plan["stages"][1]["kind"], "planning")
        self.assertEqual(sum(s["kind"] == "review" for s in plan["stages"]), 1)
        low = self.plan("LOW", architecture=True)
        self.assertEqual(low["risk"], "HIGH")

    def test_missing_reviewer_or_reasoning_blocks_without_fallback(self):
        caps = copy.deepcopy(self.capabilities)
        del caps[self.models["critical_reviewer"]]
        plan = routing.build_plan(ROOT, "CRITICAL", "normal", capabilities=caps)
        self.assertEqual(plan["status"], "blocked")
        self.assertIn("critical_reviewer", plan["blocked_reasons"][0])
        self.assertEqual(plan["stages"][-1]["model"], self.models["critical_reviewer"])
        caps = copy.deepcopy(self.capabilities)
        caps[self.models["critical_reviewer"]] = ["high"]
        self.assertEqual(
            routing.build_plan(ROOT, "CRITICAL", "normal", capabilities=caps)["status"],
            "blocked",
        )
        self.assertEqual(
            routing.build_plan(ROOT, "HIGH", "normal")["status"], "needs_capabilities"
        )

    def test_escalation_requires_evidence_and_not_ci_alone(self):
        self.assertNotIn(
            "architect", [s["role"] for s in self.plan(ci_failed=True)["stages"]]
        )
        for condition in ("public_contract", "auth", "concurrency", "migration"):
            plan = self.plan(
                escalation=condition,
                evidence="Confirmed affected boundary from source inspection",
            )
            self.assertEqual(plan["risk"], "HIGH")
            self.assertNotIn("architect", [s["role"] for s in plan["stages"]])
        with self.assertRaises(ValueError):
            self.plan(escalation="unclear_root_cause", evidence="Still unclear")
        plan = self.plan(
            escalation="unclear_root_cause",
            prior_attempts=1,
            evidence="One focused reproduction failed to identify cause",
        )
        self.assertIn("architect", [s["role"] for s in plan["stages"]])
        with self.assertRaises(ValueError):
            self.plan(escalation="ci_failed", evidence="Build failed")

    def test_policy_rejects_dangerous_or_incomplete_mutations(self):
        routing.validate_policy(self.policy)
        mutations = [
            lambda p: p.update(version=2),
            lambda p: p["limits"].update(scout=2),
            lambda p: p["limits"].update(review_rounds=True),
            lambda p: p["stages"]["lead"].update(reasoning_effort="ultra"),
            lambda p: p["stages"]["worker"].update(reasoning_effort="max"),
            lambda p: p["stages"]["worker"].update(role="architect"),
            lambda p: p["stages"]["scout"].update(model="hardcoded-provider-id"),
            lambda p: p["routes"]["HIGH"].update(normal=["worker"]),
            lambda p: p["routes"]["MEDIUM"].pop("complex"),
            lambda p: p["escalation"].update(automatic=True),
            lambda p: p["escalation"].update(automatic=0),
            lambda p: p["handoff"].update(review_fresh_context=1),
        ]
        for mutate in mutations:
            invalid = copy.deepcopy(self.policy)
            mutate(invalid)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                routing.validate_policy(invalid)

    def test_duplicate_json_and_malformed_capabilities_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "caps.json"
            for data in (
                '{"models":{},"models":{}}',
                '{"models":[]}',
                '{"models":{"example":["unsupported"]}}',
            ):
                path.write_text(data)
                with self.assertRaises(ValueError):
                    routing.capabilities_from_file(path)
        with self.assertRaises(ValueError):
            self.plan(escalation="auth", evidence="x" * 4097)

    def test_all_routes_avoid_max_ultra_and_cap_expensive_stages(self):
        for risk in engineering.RISKS:
            for complexity in ("trivial", "normal", "complex"):
                for architecture in (False, True):
                    plan = self.plan(risk, complexity, architecture=architecture)
                    self.assertLessEqual(len(plan["stages"]), 4)
                    self.assertTrue(
                        all(
                            s["reasoning_effort"] not in ("max", "ultra")
                            for s in plan["stages"]
                        )
                    )

    def test_model_ids_follow_the_canonical_table_not_copied_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy = engineering.load_policy()
            table = root / policy["model_table"]
            table.parent.mkdir(parents=True)
            (root / "policies").mkdir()
            (root / "policies/engineering.json").write_text(json.dumps(policy))
            original = (ROOT / policy["model_table"]).read_text()
            replacement = "gpt-fixture-worker"
            table.write_text(original.replace(self.models["worker"], replacement))
            with patch.object(engineering, "ROOT", root):
                plan = self.plan("LOW")
                self.assertEqual(plan["stages"][0]["model"], replacement)
        for path in (
            "policies/model-routing.json",
            "scripts/model_routing.py",
            "scripts/dispatch_launcher.py",
            "scripts/manacost-dispatch",
        ):
            self.assertNotRegex((ROOT / path).read_text(), r"gpt-\d[\w.-]+")


if __name__ == "__main__":
    unittest.main()
