#!/usr/bin/env python3
"""Pure, versioned model plans. Never probes or executes a model."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import engineering as engineering

ROOT = Path(__file__).resolve().parents[1]
COMPLEXITIES = ("trivial", "normal", "complex")
ROLES = ("scout", "worker", "lead", "high_reviewer", "critical_reviewer", "architect")
CONDITIONS = (
    "high_risk",
    "critical_risk",
    "public_contract",
    "auth",
    "concurrency",
    "migration",
    "unclear_root_cause",
    "architecture_review",
)


def load_policy():
    return read_json_file(ROOT / "policies/model-routing.json")


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON field")
        value[key] = item
    return value


def exact_keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f"invalid {label} fields")


def validate_policy(policy):
    exact_keys(
        policy,
        (
            "version",
            "reasoning_levels",
            "forbidden_automatic_reasoning",
            "limits",
            "stages",
            "routes",
            "unknown_context",
            "escalation",
            "handoff",
            "unavailable_required_stage",
        ),
        "routing policy",
    )
    if type(policy["version"]) is not int or policy["version"] != 1:
        raise ValueError("unsupported routing policy version")
    if policy["reasoning_levels"] != ["low", "medium", "high", "xhigh"] or policy[
        "forbidden_automatic_reasoning"
    ] != ["max", "ultra"]:
        raise ValueError("invalid automatic reasoning levels")
    limits = policy["limits"]
    exact_keys(
        limits,
        (
            "scout",
            "implementation_attempts",
            "review_rounds",
            "architecture_stages",
            "model_launches",
            "brief_bytes",
            "timeout_seconds",
        ),
        "limits",
    )
    for key, ceiling in (
        ("scout", 1),
        ("implementation_attempts", 1),
        ("review_rounds", 1),
        ("architecture_stages", 1),
        ("model_launches", 4),
    ):
        if type(limits[key]) is not int or limits[key] != ceiling:
            raise ValueError(f"unsafe {key} limit")
    for key, ceiling in (("brief_bytes", 16384), ("timeout_seconds", 1800)):
        if type(limits[key]) is not int or not 1 <= limits[key] <= ceiling:
            raise ValueError(f"unsafe {key} limit")
    exact_keys(policy["stages"], ROLES, "stages")
    expected = {
        "scout": ("low", "context"),
        "worker": ("medium", "implementation"),
        "lead": ("high", "implementation"),
        "high_reviewer": ("high", "review"),
        "critical_reviewer": ("xhigh", "review"),
        "architect": ("xhigh", "planning"),
    }
    for role, stage in policy["stages"].items():
        exact_keys(
            stage,
            ("role", "reasoning_effort", "kind", "required", "max_attempts"),
            "stage",
        )
        if (
            stage["role"] != role
            or (stage["reasoning_effort"], stage["kind"]) != expected[role]
            or stage["required"] is not True
            or type(stage["max_attempts"]) is not int
            or stage["max_attempts"] != 1
        ):
            raise ValueError("unsafe stage or reasoning selection")
    exact_keys(policy["routes"], engineering.RISKS, "risk routes")
    for risk, choices in policy["routes"].items():
        exact_keys(choices, COMPLEXITIES, "complexity routes")
        for complexity, stages in choices.items():
            if risk in ("HIGH", "CRITICAL"):
                expected_stages = [
                    "scout",
                    "lead",
                    "high_reviewer" if risk == "HIGH" else "critical_reviewer",
                ]
            else:
                expected_stages = (
                    ["scout", "worker"]
                    if risk == "MEDIUM" and complexity == "complex"
                    else ["worker"]
                )
            if stages != expected_stages:
                raise ValueError("missing review or invalid bounded route")
    if policy["unknown_context"] != {"risk_floor": "MEDIUM", "prepend": "scout"}:
        raise ValueError("invalid unknown-context rule")
    escalation = policy["escalation"]
    if (
        not isinstance(escalation, dict)
        or escalation.get("automatic") is not False
        or escalation.get("requires_evidence") is not True
        or type(escalation.get("unclear_root_cause_after_attempts")) is not int
    ):
        raise ValueError("escalation switches/counts require exact JSON types")
    if escalation != {
        "automatic": False,
        "conditions": list(CONDITIONS),
        "requires_evidence": True,
        "unclear_root_cause_after_attempts": 1,
        "on_ci_failure_alone": "no_model_upgrade",
        "on_exhaustion": "blocked_manual_rescope",
    }:
        raise ValueError("unsafe escalation rules")
    if (
        not isinstance(policy["handoff"], dict)
        or policy["handoff"].get("whole_repository") is not False
        or policy["handoff"].get("review_fresh_context") is not True
    ):
        raise ValueError("handoff switches require booleans")
    if (
        policy["handoff"]
        != {
            "format": "engineering-brief",
            "whole_repository": False,
            "parallel": "independent_tasks_only",
            "review_fresh_context": True,
        }
        or policy["unavailable_required_stage"] != "blocked_no_fallback"
    ):
        raise ValueError("unsafe handoff or fallback rule")


def capabilities_from_file(path):
    if path is None:
        return None
    value = read_json_file(path)
    exact_keys(value, ("models",), "capabilities")
    models = value["models"]
    if not isinstance(models, dict) or len(models) > 100:
        raise ValueError("invalid client model capabilities")
    for model, efforts in models.items():
        if (
            not isinstance(model, str)
            or not re.fullmatch(r"[a-zA-Z0-9._/-]{1,160}", model)
            or not isinstance(efforts, list)
            or not efforts
            or any(
                e
                not in (
                    "none",
                    "minimal",
                    "low",
                    "medium",
                    "high",
                    "xhigh",
                    "max",
                    "ultra",
                )
                for e in efforts
            )
        ):
            raise ValueError("invalid client reasoning capabilities")
    return models


def read_json_file(path, limit=16384):
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("input exceeds byte budget")
    return json.loads(data, object_pairs_hook=unique_object)


def policy_digest():
    digest = hashlib.sha256()
    for path in (
        "policies/model-routing.json",
        "policies/engineering.json",
        "skills/engineering/synthesis/synthesis-model-tiers/tiers.yaml",
    ):
        digest.update((ROOT / path).read_bytes())
    return digest.hexdigest()


def build_plan(
    project,
    risk,
    complexity,
    *,
    unknown_context=False,
    architecture=False,
    capabilities=None,
    escalation=None,
    evidence="",
    prior_attempts=0,
    ci_failed=False,
):
    policy = load_policy()
    validate_policy(policy)
    if risk not in engineering.RISKS or complexity not in COMPLEXITIES:
        raise ValueError("invalid risk or complexity")
    if type(prior_attempts) is not int or prior_attempts not in (0, 1):
        raise ValueError("at most one prior meaningful attempt")
    if (
        not isinstance(evidence, str)
        or len(evidence.encode()) > 4096
        or "\0" in evidence
    ):
        raise ValueError("escalation evidence must be bounded text")
    if escalation is None and (evidence or prior_attempts):
        raise ValueError(
            "evidence/prior attempts require an explicit escalation condition"
        )
    if escalation is not None and (
        escalation not in CONDITIONS or not evidence.strip()
    ):
        raise ValueError(
            "escalation requires an allowed condition and confirmed evidence"
        )
    if escalation == "unclear_root_cause" and prior_attempts != 1:
        raise ValueError("unclear root cause requires one evidenced meaningful attempt")
    reasons = [f"{risk}/{complexity}: bounded role route"]
    floor = "MEDIUM" if unknown_context else "LOW"
    if architecture or escalation:
        floor = "CRITICAL" if escalation == "critical_risk" else "HIGH"
        reasons.append("mandatory architecture or explicitly evidenced escalation")
    risk = max(risk, floor, key=engineering.RISKS.index)
    architecture = architecture or escalation in (
        "unclear_root_cause",
        "architecture_review",
    )
    selected = list(policy["routes"][risk][complexity])
    if unknown_context and "scout" not in selected:
        selected.insert(0, policy["unknown_context"]["prepend"])
        reasons.append("unknown context: one bounded scout")
    if architecture:
        selected.insert(1, "architect")
        reasons.append("architect is separate planning, never implementation")
    if ci_failed:
        reasons.append("CI failure alone does not upgrade models")
    models = engineering.resolve_models(engineering.load_policy())
    stages, blocked = [], []
    for index, name in enumerate(selected):
        stage = {
            "id": name,
            **policy["stages"][name],
            "model": models[name],
            "depends_on": selected[index - 1 : index],
            "fresh_context": True,
        }
        if capabilities is not None and stage[
            "reasoning_effort"
        ] not in capabilities.get(stage["model"], []):
            blocked.append(f"{name}: required model/effort unavailable; no fallback")
        stages.append(stage)
    return {
        "schema_version": 1,
        "policy_version": policy["version"],
        "policy_digest": policy_digest(),
        "project": str(Path(project).resolve()),
        "risk": risk,
        "complexity": complexity,
        "reasons": reasons,
        "stages": stages,
        "limits": policy["limits"],
        "escalation": {
            **policy["escalation"],
            "confirmed_condition": escalation,
            "evidence": evidence,
            "prior_attempts": prior_attempts,
        },
        "handoff": policy["handoff"],
        "status": "blocked"
        if blocked
        else "needs_capabilities"
        if capabilities is None
        else "ready",
        "blocked_reasons": blocked,
        "availability": "caller_supplied_not_probed"
        if capabilities is not None
        else "not_probed",
    }


def add_arguments(parser):
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--task", default="")
    parser.add_argument("--task-file", type=Path)
    parser.add_argument("--brief-file", type=Path)
    parser.add_argument("--risk", choices=["auto", *engineering.RISKS], default="auto")
    parser.add_argument("--complexity", choices=COMPLEXITIES, default="normal")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--unknown-context", action="store_true")
    parser.add_argument("--architecture", action="store_true")
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--escalation", choices=CONDITIONS)
    parser.add_argument("--evidence", default="")
    parser.add_argument("--prior-attempts", type=int, choices=(0, 1), default=0)
    parser.add_argument("--ci-failed", action="store_true")


def request_from_args(args):
    if args.task and args.task_file:
        raise ValueError("choose --task or --task-file")
    task = args.task
    if args.task_file:
        with args.task_file.open("rb") as stream:
            data = stream.read(16385)
        if len(data) > 16384:
            raise ValueError("task file exceeds byte budget")
        task = data.decode("utf-8")
    if not task.strip() or len(task.encode()) > 16384 or "\0" in task:
        raise ValueError("a nonempty bounded task is required")
    brief = read_json_file(args.brief_file) if args.brief_file else None
    if brief is not None:
        engineering.validate_brief(brief, engineering.load_policy())
    project = Path(args.project).resolve(strict=True)
    paths = sorted(set(args.path + engineering.changed_paths(project, args.base)))
    # A caller can raise the risk floor, never hide Git paths or semantic hazards.
    risk = engineering.classify(paths, task, args.risk)
    plan = build_plan(
        project,
        risk,
        args.complexity,
        unknown_context=args.unknown_context,
        architecture=args.architecture or engineering.needs_architect(paths, task),
        capabilities=capabilities_from_file(args.capabilities),
        escalation=args.escalation,
        evidence=args.evidence,
        prior_attempts=args.prior_attempts,
        ci_failed=args.ci_failed,
    )
    return plan, task, brief


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-policy", action="store_true")
    add_arguments(parser)
    args = parser.parse_args(argv)
    try:
        if args.validate_policy:
            validate_policy(load_policy())
            result = {"ok": True}
        else:
            result, _, _ = request_from_args(args)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2 if result.get("status") == "blocked" else 0
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
