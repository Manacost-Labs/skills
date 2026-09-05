#!/usr/bin/env python3
"""Small, dependency-free policy router and shared local/CI check runner."""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RISKS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def load_policy():
    return json.loads((ROOT / "policies/engineering.json").read_text())


def inventory():
    with (ROOT / "inventory/skills.tsv").open() as stream:
        return {
            row["id"]: row["canonical_path"]
            for row in csv.DictReader(stream, delimiter="\t")
        }


def resolve_models(policy):
    # Deliberately parse only the existing table's restricted OpenAI inline lists,
    # not arbitrary YAML. Reject unsupported syntax instead of guessing its meaning.
    table_path = (ROOT / policy["model_table"]).resolve()
    if not table_path.is_relative_to(ROOT):
        raise ValueError("model table must stay inside the canonical catalog")
    table = table_path.read_text()
    block = re.search(r"^  openai:\n(.*?)(?=^  \w|\Z)", table, re.MULTILINE | re.DOTALL)
    if not block:
        raise ValueError("OpenAI model table missing")
    tiers = {}
    for tier in ("judgment", "routine", "bulk"):
        match = re.search(
            rf"^    {tier}: \[([a-z0-9., -]+)\]\s*(?:#.*)?$", block[1], re.MULTILINE
        )
        if not match:
            raise ValueError(f"invalid model tier: {tier}")
        tiers[tier] = [name.strip() for name in match[1].split(",")]
        if any(not re.fullmatch(r"gpt-[a-z0-9.-]+", name) for name in tiers[tier]):
            raise ValueError("invalid provider identifier")
    try:
        return {
            name: tiers[role["tier"]][role["index"]]
            for name, role in policy["roles"].items()
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("unresolvable model role") from exc


def validate_policy(policy):
    if policy.get("version") != 1 or set(policy.get("risk", {})) != set(RISKS):
        raise ValueError("invalid policy version or risk levels")
    if policy.get("authority") != [
        "system / platform",
        "developer / security",
        "explicit user instructions",
        "project-specific AGENTS.md",
        "server/global AGENTS.md",
        "selected profile",
        "applicable SKILL.md",
    ]:
        raise ValueError("invalid authority order")
    for role in policy["roles"].values():
        if (
            role.get("tier") not in ("judgment", "routine", "bulk")
            or type(role.get("index")) is not int
            or role["index"] < 0
        ):
            raise ValueError("invalid model role")
    required_roles = {
        "lead",
        "scout",
        "worker",
        "architect",
        "medium_reviewer",
        "high_reviewer",
        "critical_reviewer",
    }
    if set(policy["roles"]) != required_roles:
        raise ValueError("missing or unknown orchestration roles")
    models = resolve_models(policy)
    if (
        policy["architecture_review"]["role"] != "architect"
        or not policy["architecture_review"]["paths"]
    ):
        raise ValueError(
            "global architecture assessment must resolve the architect role"
        )
    if (
        policy["roles"]["high_reviewer"] != policy["roles"]["lead"]
        or policy["roles"]["critical_reviewer"] != policy["roles"]["architect"]
    ):
        raise ValueError("mandatory review role mismatch")
    if models["worker"] == models["lead"] or models["scout"] == models["architect"]:
        raise ValueError("bounded roles must remain distinct")
    floors = {
        "LOW": {"focused"},
        "MEDIUM": {"focused", "lint", "types", "unit"},
        "HIGH": {"focused", "lint", "types", "unit", "integration", "security"},
        "CRITICAL": {
            "focused",
            "lint",
            "types",
            "unit",
            "integration",
            "security",
            "rollback",
        },
    }
    for level, rules in policy["risk"].items():
        if not rules.get("checks") or rules["reviewer"] not in (None, *models):
            raise ValueError(f"invalid requirements for {level}")
        if not isinstance(rules["checks"], list) or not floors[level].issubset(
            rules["checks"]
        ):
            raise ValueError("required verification categories missing")
        if any(
            type(rules.get(key)) is not bool for key in ("full_gate", "review_required")
        ):
            raise ValueError("risk switches must be booleans")
        expected_reviewer = {
            "LOW": None,
            "MEDIUM": "medium_reviewer",
            "HIGH": "high_reviewer",
            "CRITICAL": "critical_reviewer",
        }[level]
        if rules["reviewer"] != expected_reviewer:
            raise ValueError("risk reviewer does not match its role")
        high = level in ("HIGH", "CRITICAL")
        if rules["full_gate"] != high or rules["review_required"] != high:
            raise ValueError("invalid risk gate policy")
    for name, ceiling in (("trivial", 1), ("normal", 3), ("complex", 5)):
        budget = policy["complexity"][name]
        if type(budget["skill_limit"]) is not int or budget["skill_limit"] != ceiling:
            raise ValueError("invalid skill budget")
        if type(budget["scout"]) is not bool or budget["scout"] != (name != "trivial"):
            raise ValueError("invalid scout complexity policy")
        if type(budget["workers"]) is not int or not 0 <= budget["workers"] <= (
            2 if name == "complex" else 0
        ):
            raise ValueError("invalid bounded-worker budget")
    known = inventory()
    for rule in policy["routes"]:
        re.compile(rule["match"])
        if rule["skill"] not in known:
            raise ValueError(f"unknown routed skill: {rule['skill']}")
    if policy["agents"]["leaf_may_spawn"]:
        raise ValueError("recursive worker gates are forbidden")
    for path in (ROOT / "profiles").glob("*.yaml"):
        contents = path.read_text()
        validate_profile(contents)
        if not profile_skills(path.stem).issubset(known):
            raise ValueError(f"profile references unknown skills: {path.name}")


def needs_architect(paths, task=""):
    policy = load_policy()
    return any(
        re.search(pattern, path)
        for path in paths
        for pattern in policy["architecture_review"]["paths"]
    ) or bool(
        re.search(policy["architecture_review"]["task_match"], task, re.IGNORECASE)
    )


def classify(paths, task="", hint="auto"):
    policy = load_policy()
    if hint not in (*RISKS, "auto"):
        raise ValueError("invalid risk")
    # Unknown source is MEDIUM; filenames alone cannot prove behavioral safety.
    level = (
        "LOW"
        if paths and all(re.search(r"\.(md|txt|css)$", p) for p in paths)
        else "MEDIUM"
    )
    for candidate in ("HIGH", "CRITICAL"):
        patterns = policy["risk_patterns"][candidate]
        if any(
            re.search(pattern, p, re.IGNORECASE) for p in paths for pattern in patterns
        ) or re.search(policy["risk_keywords"][candidate], task, re.IGNORECASE):
            level = candidate
    return max(
        (
            level,
            "HIGH" if needs_architect(paths, task) else "LOW",
            hint if hint != "auto" else level,
        ),
        key=RISKS.index,
    )


def validate_profile(contents):
    keys = re.findall(r"^([a-z_]+):", contents, re.MULTILINE)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate profile key")
    if (
        re.findall(r"^activation: (.+)$", contents, re.MULTILINE) != ["on-demand"]
        or "load" in keys
        or "available" not in keys
    ):
        raise ValueError("profile must declare one on-demand catalog")


def profile_skills(profile, seen=None):
    if not re.fullmatch(r"[a-z0-9-]+", profile):
        raise ValueError("invalid profile")
    seen = set() if seen is None else seen
    if profile in seen:
        raise ValueError("cyclic profile inclusion")
    path = ROOT / "profiles" / f"{profile}.yaml"
    if not path.is_file():
        raise ValueError("unknown profile")
    seen = seen | {profile}
    result, section = set(), ""
    contents = path.read_text()
    validate_profile(contents)
    for line in contents.splitlines():
        if line and not line.startswith(" "):
            section = line.rstrip(":")
        elif line.startswith("  - "):
            value = line[4:]
            if section == "available":
                result.add(value)
            elif section == "include":
                result.update(profile_skills(value, seen))
    return result


def route(project, task, complexity, risk_hint, paths, profile, explicit):
    policy, known = load_policy(), inventory()
    budget = policy["complexity"][complexity]
    allowed = profile_skills(profile)
    chosen = list(dict.fromkeys(explicit))
    if any(skill not in known for skill in chosen):
        raise ValueError("unknown explicitly requested skill")
    if len(chosen) > budget["skill_limit"]:
        raise ValueError(
            "explicit skill selection exceeds budget; split phases or document an exception"
        )
    for rule in policy["routes"]:
        if len(chosen) >= budget["skill_limit"]:
            break
        if (
            rule["skill"] in allowed
            and rule["skill"] not in chosen
            and re.search(rule["match"], task, re.IGNORECASE)
        ):
            chosen.append(rule["skill"])
    risk = classify(paths, task, risk_hint)
    rules, models = policy["risk"][risk], resolve_models(policy)
    return {
        "project": str(project.resolve()),
        "profile": profile,
        "complexity": complexity,
        "risk": risk,
        "lead": models["lead"],
        "scout": models["scout"]
        if budget["scout"] or risk in ("HIGH", "CRITICAL")
        else None,
        "optional_workers_max": budget["workers"],
        "reviewer": models.get(rules["reviewer"]),
        "review_required": rules["review_required"],
        "architecture_reviewer": models["architect"]
        if needs_architect(paths, task)
        else None,
        "architecture_review_required": needs_architect(paths, task),
        "verification": rules["checks"],
        "skills": [
            {
                "id": skill,
                "path": str(ROOT / known[skill]),
                "reason": "explicit" if skill in explicit else "task match",
            }
            for skill in chosen
        ],
    }


def validate_brief(brief, policy):
    fields = policy["brief"]["list_fields"]
    if not isinstance(brief, dict) or set(brief) != {"goal", *fields}:
        raise ValueError("brief requires exactly goal and declared list fields")
    if not isinstance(brief["goal"], str) or not brief["goal"].strip():
        raise ValueError("brief goal is empty")
    words = len(brief["goal"].split())
    for field in fields:
        value = brief[field]
        limit = 4 if field == "recommended_skills" else policy["brief"]["max_items"]
        if (
            not isinstance(value, list)
            or len(value) > limit
            or any(not isinstance(item, str) for item in value)
        ):
            raise ValueError(f"invalid brief field: {field}")
        words += sum(len(item.split()) for item in value)
    if words > policy["brief"]["max_words"]:
        raise ValueError("brief exceeds word budget")


def resolve_base(project, base):
    # GitHub's before SHA is zero for a new branch. Scan the complete tree,
    # never silently turn this into HEAD..HEAD and miss the initial change.
    if re.fullmatch(r"0{40}|0{64}", base):
        return (
            subprocess.check_output(
                ["git", "hash-object", "-w", "-t", "tree", "--stdin"],
                cwd=project,
                input=b"",
            )
            .decode()
            .strip()
        )
    return subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", base + "^{commit}"],
        cwd=project,
        text=True,
    ).strip()


def staged_paths(project):
    data = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--no-renames", "-z", "--"],
        cwd=project,
    )
    return {os.fsdecode(path) for path in data.split(b"\0") if path}


def changed_paths(project, base="HEAD"):
    revision = resolve_base(project, base)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", revision, "--"],
        cwd=project,
    )
    new = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=project
    )
    return sorted(
        {
            path.decode("utf-8", "surrogateescape")
            for path in (changed + new).split(b"\0")
            if path
        }
        | staged_paths(project)
    )


def check_whitespace(project, base):
    revision = resolve_base(project, base)
    # CI is clean: compare against its event base as well as the local index.
    # Keep source contents out of the report, even on an invalid diff.
    codes = [
        subprocess.run(
            ["git", "diff", "--check", *args, "--"],
            cwd=project,
            capture_output=True,
        ).returncode
        for args in ([revision], ["--cached"])
    ]
    return {
        "ok": not any(codes),
        "base_diff_exit": codes[0],
        "index_diff_exit": codes[1],
    }


def detect_stacks(project):
    markers = {
        "catalog": "registry.yaml",
        "typescript": "tsconfig.json",
        "node": "package.json",
        "go": "go.mod",
        "python": "pyproject.toml",
        "api": "openapi.yaml",
    }
    stacks = [name for name, marker in markers.items() if (project / marker).is_file()]
    if "python" not in stacks and (
        any(project.glob("*.py")) or any((project / "scripts").glob("*.py"))
    ):
        stacks.append("python")
    return stacks


def verification_plan(config, risk, paths, stacks=None):
    if (
        config.get("version") != 1
        or not isinstance(config.get("checks"), list)
        or not config["checks"]
    ):
        raise ValueError("verification needs version 1 and nonempty checks")
    plan, ids = {"risk": risk, "stacks": stacks or [], "run": [], "skip": []}, set()
    waived = config.get("not_applicable", {})
    if not isinstance(waived, dict) or any(
        not isinstance(reason, str) or not reason.strip() for reason in waived.values()
    ):
        raise ValueError("not_applicable requires explicit reasons")
    covered = set(waived)
    for check in config["checks"]:
        name, argv = check.get("id"), check.get("argv")
        minimum = check.get("min_risk", "LOW")
        if (
            not isinstance(name, str)
            or name in ids
            or not isinstance(argv, list)
            or not argv
            or any(not isinstance(a, str) or not a for a in argv)
            or minimum not in RISKS
        ):
            raise ValueError("invalid/duplicate verification check")
        if not 1 <= check.get("timeout", 300) <= 3600:
            raise ValueError("invalid check timeout")
        categories = check.get("covers")
        if (
            not isinstance(categories, list)
            or not categories
            or any(not isinstance(c, str) for c in categories)
        ):
            raise ValueError(
                "check must declare the verification requirements it covers"
            )
        required_stacks = check.get("stacks", [])
        if not isinstance(required_stacks, list) or any(
            not isinstance(s, str) for s in required_stacks
        ):
            raise ValueError("invalid stack selector")
        ids.add(name)
        if required_stacks and not set(required_stacks).intersection(stacks or []):
            plan["skip"].append({"id": name, "reason": "project stack does not match"})
        elif RISKS.index(risk) < RISKS.index(minimum):
            plan["skip"].append(
                {"id": name, "reason": f"requires {minimum}; change is {risk}"}
            )
        else:
            plan["run"].append(check)
            covered.update(categories)
    if not plan["run"]:
        raise ValueError("no applicable focused verification configured")
    missing = set(load_policy()["risk"][risk]["checks"]) - covered
    if missing:
        raise ValueError("unconfigured required checks: " + ", ".join(sorted(missing)))
    plan["not_applicable"] = waived
    return plan


def run_checks(project, plan):
    report = {
        "ok": True,
        "risk": plan.get("risk"),
        "checks": [],
        "skipped": plan["skip"],
        "not_applicable": plan.get("not_applicable", {}),
    }
    for check in plan["run"]:
        start = time.monotonic()
        try:
            # Commands are reviewed project argv arrays, never shell-expanded task text.
            result = subprocess.run(
                check["argv"],
                cwd=project,
                timeout=check.get("timeout", 300),
                check=False,
            )
            status = "passed" if result.returncode == 0 else "failed"
        except FileNotFoundError:
            status = "unavailable"
        except subprocess.TimeoutExpired:
            status = "timed_out"
        report["checks"].append(
            {
                "id": check["id"],
                "status": status,
                "seconds": round(time.monotonic() - start, 2),
            }
        )
        report["ok"] = report["ok"] and status == "passed"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "route",
            "risk",
            "models",
            "validate-policy",
            "validate-brief",
            "check-whitespace",
            "verify",
        ],
    )
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--task", default="")
    parser.add_argument(
        "--complexity", choices=["trivial", "normal", "complex"], default="normal"
    )
    parser.add_argument(
        "--risk",
        choices=["auto", *RISKS],
        default=os.environ.get("VERIFY_RISK", "auto"),
    )
    parser.add_argument("--profile", default="server")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--base", default=os.environ.get("VERIFY_BASE", "HEAD"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        policy = load_policy()
        validate_policy(policy)
        project = Path(args.project).resolve()
        if args.command == "models":
            result = {
                "roles": resolve_models(policy),
                "availability": "not-probed; client must advertise and execute the identifier",
            }
        elif args.command == "validate-policy":
            result = {"ok": True}
        elif args.command == "validate-brief":
            validate_brief(json.loads(project.read_text()), policy)
            result = {"ok": True}
        elif args.command == "check-whitespace":
            result = check_whitespace(project, args.base)
        else:
            paths = sorted(set(args.path + changed_paths(project, args.base)))
            risk = classify(paths, args.task, args.risk)
            if args.command == "risk":
                result = {"risk": risk, "paths": paths, **policy["risk"][risk]}
            elif args.command == "route":
                result = route(
                    project,
                    args.task,
                    args.complexity,
                    args.risk,
                    paths,
                    args.profile,
                    args.skill,
                )
            else:
                config_path = project / ".ai/verify.json"
                if not config_path.is_file():
                    raise ValueError(
                        "no .ai/verify.json; use the project's existing canonical gate or opt in explicitly (docs/engineering-system.md)"
                    )
                plan = verification_plan(
                    json.loads(config_path.read_text()),
                    risk,
                    paths,
                    detect_stacks(project),
                )
                os.environ["VERIFY_BASE"] = args.base
                result = plan if args.dry_run else run_checks(project, plan)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0 if result.get("ok", True) else 1
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"skillctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
