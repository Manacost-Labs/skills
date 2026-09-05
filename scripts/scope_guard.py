#!/usr/bin/env python3
"""Fail-closed Git worktree scope guard used by ``skillctl``.

The guard intentionally uses only Python's standard library and Git plumbing.
It records content hashes only for ordinary, non-opaque paths. Sensitive and
protected paths are represented solely by filesystem and index metadata, so
their contents are never opened by this program. ``--pre-edit`` detects an
unexpected change but cannot attribute its writer or prevent a check/edit
TOCTOU race; separate worktrees remain the safest parallel-work boundary.
It is an advisory coordination aid, not a hostile same-UID security boundary.
Ignored protected files below pruned generated/cache trees are intentionally
not discovered; those non-source trees are not authorized edit scope, and this
guard is not a universal filesystem sandbox.
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import json
import os
import posixpath
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

SCHEMA = 1
BUILTIN_PROTECTED = (
    ".env*",
    "**/.env*",
    "credentials*",
    "**/credentials*",
    "*.key",
    "**/*.key",
    "*.pem",
    "**/*.pem",
    "*.p12",
    "**/*.p12",
    "*.db",
    "**/*.db",
    "*.sqlite*",
    "**/*.sqlite*",
    "*dump*",
    "**/*dump*",
    "*private*key*",
    "**/*private*key*",
)
OPAQUE_PARTS = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".next",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "cache",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}


class GuardError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise GuardError(message)


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        fail(result.stderr.decode("utf-8", "replace").strip() or "git command failed")
    return result.stdout


def git_text(root: Path, *args: str) -> str:
    return git(root, *args).decode("utf-8", "surrogateescape").strip()


def absolute_git_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def repository(project: str) -> tuple[Path, Path, Path]:
    requested = Path(project).resolve()
    try:
        top = absolute_git_path(
            requested, git_text(requested, "rev-parse", "--show-toplevel")
        )
        git_dir = absolute_git_path(
            requested, git_text(requested, "rev-parse", "--git-dir")
        )
        common_dir = absolute_git_path(
            requested, git_text(requested, "rev-parse", "--git-common-dir")
        )
    except GuardError:
        raise
    if requested != top:
        fail("--project must be the Git worktree root")
    return top, git_dir, common_dir


def validate_relative(value: str, what: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or posixpath.isabs(value)
    ):
        fail(f"invalid {what}: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        fail(f"invalid {what}: {value!r}")
    bracket = False
    for char in value:
        if char == "[":
            if bracket:
                fail(f"invalid {what}: nested '['")
            bracket = True
        elif char == "]":
            if not bracket:
                fail(f"invalid {what}: unmatched ']'")
            bracket = False
    if bracket:
        fail(f"invalid {what}: unmatched '['")
    return value


def matches(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    return any(
        fnmatch.fnmatchcase(path, pattern)
        or (pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]))
        for pattern in patterns
    )


def protected(path: str, state: dict[str, Any]) -> bool:
    return matches(path, BUILTIN_PROTECTED) or matches(path, state["protect"])


def opaque(path: str) -> bool:
    return any(part in OPAQUE_PARTS for part in path.split("/"))


def status(root: Path) -> dict[str, list[str]]:
    """Return every changed path, including both sides of a rename/copy."""
    records = git(
        root, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    ).split(b"\0")
    result: dict[str, list[str]] = {}
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            fail("unrecognised git porcelain status")
        code = record[:2].decode("ascii", "strict")
        path = record[3:].decode("utf-8", "surrogateescape")
        paths = [path]
        if "R" in code or "C" in code:
            if index >= len(records) or not records[index]:
                fail("truncated rename status")
            paths.append(records[index].decode("utf-8", "surrogateescape"))
            index += 1
        for changed in paths:
            changed = validate_relative(changed, "Git path")
            result.setdefault(changed, []).append(code)
    return result


def index_identity(root: Path, path: str) -> list[str]:
    data = git(root, "ls-files", "--stage", "-z", "--", path)
    identities: list[str] = []
    for record in data.split(b"\0"):
        if not record:
            continue
        try:
            header, recorded_path = record.split(b"\t", 1)
        except ValueError:
            fail("unrecognised Git index record")
        if recorded_path.decode("utf-8", "surrogateescape") == path:
            identities.append(header.decode("ascii", "strict"))
    return sorted(identities)


def safe_path(root: Path, relative: str) -> Path:
    validate_relative(relative, "path")
    parts = relative.split("/")
    ancestor = root
    for part in parts[:-1]:
        ancestor /= part
        try:
            info = os.lstat(ancestor)
        except FileNotFoundError:
            break
        except OSError as error:
            fail(f"cannot inspect path ancestor {relative!r}: {error}")
        if stat.S_ISLNK(info.st_mode):
            fail(f"symlinked ancestor rejected: {relative}")
        if not stat.S_ISDIR(info.st_mode):
            fail(f"non-directory ancestor rejected: {relative}")
    # The final component is lstat'ed below, so it is never followed either.
    return root.joinpath(*parts)


def file_fingerprint(
    root: Path, path: str, metadata_only: bool = False
) -> dict[str, Any]:
    target = safe_path(root, path)
    result: dict[str, Any] = {"index": index_identity(root, path)}
    try:
        info = os.lstat(target)
    except FileNotFoundError:
        result["worktree"] = None
        return result
    worktree: dict[str, Any] = {
        "mode": stat.S_IMODE(info.st_mode),
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "ctime_ns": info.st_ctime_ns,
    }
    if stat.S_ISREG(info.st_mode):
        worktree["kind"] = "file"
        # Never open protected, cache, or vendored files.  Metadata is enough
        # to conservatively flag a change in those locations.
        if (
            not metadata_only
            and not matches(path, BUILTIN_PROTECTED)
            and not opaque(path)
        ):
            digest = hashlib.sha256()
            with target.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(block)
            worktree["sha256"] = digest.hexdigest()
    elif stat.S_ISLNK(info.st_mode):
        worktree["kind"] = "symlink"
    else:
        worktree["kind"] = "other"
    result["worktree"] = worktree
    return result


def snapshot(
    root: Path,
    only: set[str] | None = None,
    protect_patterns: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    current = status(root)
    paths = sorted(only if only is not None else current)
    return {
        "status": {path: current.get(path, []) for path in paths},
        "fingerprints": {
            path: file_fingerprint(
                root, path, metadata_only=matches(path, protect_patterns)
            )
            for path in paths
        },
    }


def tracked_and_untracked_names(root: Path) -> set[str]:
    names = {
        raw.decode("utf-8", "surrogateescape")
        for raw in git(root, "ls-files", "-z").split(b"\0")
        if raw
    }
    names.update(status(root))
    return {validate_relative(name, "Git path") for name in names}


def ignored(root: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    fail(result.stderr.decode("utf-8", "replace").strip() or "git ignore check failed")


def ignored_protected_paths(
    root: Path, protect_patterns: list[str] | tuple[str, ...]
) -> set[str]:
    """Discover ignored protected names without opening files or opaque trees."""
    patterns = BUILTIN_PROTECTED + tuple(protect_patterns)

    def on_error(error: OSError) -> None:
        fail(f"cannot scan protected path metadata: {error}")

    result: set[str] = set()
    for directory, directories, files in os.walk(
        root, topdown=True, followlinks=False, onerror=on_error
    ):
        directories[:] = [name for name in directories if name not in OPAQUE_PARTS]
        relative_directory = os.path.relpath(directory, root)
        prefix = "" if relative_directory == "." else relative_directory + "/"
        for name in [*directories, *files]:
            path = validate_relative(prefix + name, "filesystem path")
            if not opaque(path) and matches(path, patterns) and ignored(root, path):
                result.add(path)
    return result


def protected_ignored_snapshot(
    root: Path, protect_patterns: list[str] | tuple[str, ...]
) -> dict[str, dict[str, Any]]:
    return {
        path: file_fingerprint(root, path, metadata_only=True)
        for path in sorted(ignored_protected_paths(root, protect_patterns))
    }


def claim_dir(common_dir: Path) -> Path:
    return common_dir / "scope-guard-claims"


def claim_name(owner: str, scope: Path) -> str:
    return (
        hashlib.sha256((owner + "\0" + str(scope)).encode("utf-8")).hexdigest()
        + ".json"
    )


@contextlib.contextmanager
def claim_lock(common_dir: Path) -> Iterator[None]:
    directory = claim_dir(common_dir)
    directory.mkdir(mode=0o700, exist_ok=True)
    lock = directory / ".lock"
    descriptor: int | None = None
    for _ in range(100):
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, str(os.getpid()).encode("ascii"))
            break
        except FileExistsError:
            time.sleep(0.02)
    if descriptor is None:
        fail("scope claim lock is busy; retry rather than bypassing it")
    try:
        yield
    finally:
        os.close(descriptor)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as source:
            value = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read scope state: {error}")
    if not isinstance(value, dict):
        fail("scope state must be a JSON object")
    return value


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        fail("scope state already exists")
    try:
        os.write(descriptor, data)
    finally:
        os.close(descriptor)


def replace_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(descriptor, data)
        finally:
            os.close(descriptor)
        os.replace(temporary, path)
    except OSError as error:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        fail(f"cannot update scope state: {error}")


def static_disjoint(left: str, right: str) -> bool:
    """Return true only when segment literals prove two globs cannot meet."""
    left_parts, right_parts = left.split("/"), right.split("/")
    for a, b in zip(left_parts, right_parts):
        if any(char in a for char in "*?[") or any(char in b for char in "*?["):
            return False
        if a != b:
            return True
    if len(left_parts) == len(right_parts) and left != right:
        return True
    return False


def claims_overlap(new: dict[str, Any], existing: dict[str, Any]) -> bool:
    for candidate in new["candidates"]:
        if matches(candidate, existing["allow"]):
            return True
    for candidate in existing.get("candidates", []):
        if matches(candidate, new["allow"]):
            return True
    # No proof of glob disjointness is deliberately treated as a conflict.
    return any(
        not static_disjoint(a, b) for a in new["allow"] for b in existing["allow"]
    )


def validate_snapshot(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        fail(f"malformed {name} snapshot")
    statuses, fingerprints = value.get("status"), value.get("fingerprints")
    if not isinstance(statuses, dict) or not isinstance(fingerprints, dict):
        fail(f"malformed {name} snapshot maps")
    if set(statuses) != set(fingerprints):
        fail(f"mismatched {name} snapshot maps")
    for path, porcelain in statuses.items():
        if not isinstance(path, str):
            fail(f"malformed {name} snapshot path")
        validate_relative(path, f"{name} snapshot path")
        if not isinstance(porcelain, list) or not all(
            isinstance(code, str) for code in porcelain
        ):
            fail(f"malformed {name} status map")
        fingerprint = fingerprints[path]
        if not isinstance(fingerprint, dict) or not isinstance(
            fingerprint.get("index"), list
        ):
            fail(f"malformed {name} fingerprint map")
        if not all(isinstance(identity, str) for identity in fingerprint["index"]):
            fail(f"malformed {name} index fingerprint")
        if fingerprint.get("worktree") is not None and not isinstance(
            fingerprint.get("worktree"), dict
        ):
            fail(f"malformed {name} worktree fingerprint")


def validate_fingerprint_map(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        fail(f"malformed {name} fingerprint map")
    validate_snapshot(
        {"status": {path: [] for path in value}, "fingerprints": value}, name
    )


def validate_state(state: dict[str, Any]) -> None:
    required = {
        "schema",
        "root",
        "owner",
        "allow",
        "protect",
        "head",
        "git_dir",
        "common_dir",
        "baseline",
        "checkpoint",
        "protected_ignored",
    }
    if state.get("schema") != SCHEMA or not required.issubset(state):
        fail("malformed or unsupported scope state")
    if not isinstance(state["owner"], str) or not state["owner"]:
        fail("malformed scope owner")
    for key in ("root", "git_dir", "common_dir", "head"):
        if not isinstance(state[key], str) or not state[key]:
            fail(f"malformed scope {key}")
    for key in ("allow", "protect"):
        if not isinstance(state[key], list) or not all(
            isinstance(item, str) for item in state[key]
        ):
            fail(f"malformed scope {key}")
        for item in state[key]:
            validate_relative(item, f"{key} glob")
    if not state["allow"]:
        fail("scope allowlist is empty")
    validate_snapshot(state["baseline"], "baseline")
    validate_snapshot(state["checkpoint"], "checkpoint")
    validate_fingerprint_map(state["protected_ignored"], "protected ignored")


def immutable_digest(state: dict[str, Any]) -> str:
    immutable = {
        key: state[key]
        for key in (
            "schema",
            "root",
            "owner",
            "allow",
            "protect",
            "head",
            "git_dir",
            "common_dir",
            "baseline",
            "protected_ignored",
        )
    }
    encoded = json.dumps(
        immutable, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_environment(
    state: dict[str, Any], require_head: bool = True
) -> tuple[Path, Path, Path]:
    root = Path(state["root"])
    if not root.is_dir():
        fail("scope worktree no longer exists")
    actual_root, git_dir, common_dir = repository(str(root))
    if (
        str(actual_root) != state["root"]
        or str(git_dir) != state["git_dir"]
        or str(common_dir) != state["common_dir"]
    ):
        fail("worktree identity changed")
    if require_head and git_text(actual_root, "rev-parse", "HEAD") != state["head"]:
        fail("HEAD changed since scope initialization")
    return actual_root, git_dir, common_dir


def verify_claim(state: dict[str, Any], scope: Path, common_dir: Path) -> None:
    path = claim_dir(common_dir) / claim_name(state["owner"], scope)
    claim = read_json(path)
    expected = {
        "owner": state["owner"],
        "scope": str(scope),
        "root": state["root"],
        "git_dir": state["git_dir"],
        "binding": immutable_digest(state),
    }
    if any(claim.get(key) != value for key, value in expected.items()):
        fail("scope claim is missing or does not match this scope")


def guard(state: dict[str, Any], scope: Path, pre_edit: bool = False) -> None:
    validate_state(state)
    root, _, common_dir = verify_environment(state)
    verify_claim(state, scope, common_dir)
    current = status(root)
    baseline: dict[str, Any] = state["baseline"]["fingerprints"]
    if protected_ignored_snapshot(root, state["protect"]) != state["protected_ignored"]:
        fail("ignored protected path changed")

    # Baseline-dirty paths belong to a different session regardless of the
    # current porcelain code.  Exact fingerprint comparison catches edits that
    # remain in the same Git status bucket.
    for path, expected in baseline.items():
        validate_relative(path, "baseline path")
        if (
            file_fingerprint(root, path, metadata_only=protected(path, state))
            != expected
        ):
            fail(f"baseline dirty path changed: {path}")

    for path in current:
        if protected(path, state):
            if (
                path not in baseline
                or file_fingerprint(root, path, metadata_only=True) != baseline[path]
            ):
                fail(f"protected path changed: {path}")
        elif path not in baseline and not matches(path, state["allow"]):
            fail(f"changed path is outside this scope: {path}")

    if pre_edit:
        checkpoint = state["checkpoint"]
        for path, expected in checkpoint["fingerprints"].items():
            if (
                file_fingerprint(root, path, metadata_only=protected(path, state))
                != expected
            ):
                fail(f"path changed since checkpoint: {path}")
        for path in current:
            if matches(path, state["allow"]) and path not in checkpoint["fingerprints"]:
                fail(f"owned path appeared since checkpoint: {path}")


def command_init(args: argparse.Namespace) -> None:
    root, git_dir, common_dir = repository(args.project)
    allow = [validate_relative(pattern, "allow glob") for pattern in args.allow]
    protect = [validate_relative(pattern, "protect glob") for pattern in args.protect]
    if not allow:
        fail("at least one --allow glob is required")
    if (
        not isinstance(args.owner, str)
        or not args.owner
        or "/" in args.owner
        or "\0" in args.owner
    ):
        fail("invalid owner")
    scope = Path(args.scope).resolve()
    if scope.exists():
        fail("scope state already exists")
    if not scope.parent.is_dir():
        fail("scope state parent does not exist")
    candidates = sorted(
        path for path in tracked_and_untracked_names(root) if matches(path, allow)
    )
    state: dict[str, Any] = {
        "schema": SCHEMA,
        "root": str(root),
        "owner": args.owner,
        "allow": allow,
        "protect": protect,
        "head": git_text(root, "rev-parse", "HEAD"),
        "git_dir": str(git_dir),
        "common_dir": str(common_dir),
        "baseline": snapshot(root, protect_patterns=protect),
        "checkpoint": snapshot(root, set(candidates), protect),
        "protected_ignored": protected_ignored_snapshot(root, protect),
    }
    claim = {
        "owner": args.owner,
        "scope": str(scope),
        "root": str(root),
        "git_dir": str(git_dir),
        "allow": allow,
        "candidates": candidates,
        "binding": immutable_digest(state),
    }
    claim_path = claim_dir(common_dir) / claim_name(args.owner, scope)
    with claim_lock(common_dir):
        for path in claim_dir(common_dir).glob("*.json"):
            existing = read_json(path)
            if not all(
                isinstance(existing.get(key), value_type)
                for key, value_type in (
                    ("owner", str),
                    ("scope", str),
                    ("root", str),
                    ("git_dir", str),
                    ("allow", list),
                    ("candidates", list),
                )
            ) or not all(
                isinstance(item, str)
                for item in existing["allow"] + existing["candidates"]
            ):
                fail("malformed active scope claim")
            if existing.get("git_dir") == str(git_dir) and claims_overlap(
                claim, existing
            ):
                fail(
                    f"scope overlaps active claim {existing.get('owner', '<malformed>')!r}"
                )
        try:
            descriptor = os.open(
                claim_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            try:
                os.write(
                    descriptor,
                    (json.dumps(claim, sort_keys=True) + "\n").encode("utf-8"),
                )
            finally:
                os.close(descriptor)
        except FileExistsError:
            fail("an active claim already exists for this owner and scope")
        try:
            write_new_json(scope, state)
        except Exception:
            claim_path.unlink(missing_ok=True)
            raise


def command_guard(args: argparse.Namespace) -> None:
    scope = Path(args.scope).resolve()
    guard(read_json(scope), scope, args.pre_edit)


def command_checkpoint(args: argparse.Namespace) -> None:
    scope = Path(args.scope).resolve()
    state = read_json(scope)
    guard(state, scope)
    root, _, _ = verify_environment(state)
    owned = {
        path
        for path in tracked_and_untracked_names(root)
        if matches(path, state["allow"])
    }
    state["checkpoint"] = snapshot(root, owned, state["protect"])
    replace_json(scope, state)


def command_close(args: argparse.Namespace) -> None:
    scope = Path(args.scope).resolve()
    state = read_json(scope)
    validate_state(state)
    _, _, common_dir = verify_environment(state, require_head=False)
    path = claim_dir(common_dir) / claim_name(state["owner"], scope)
    with claim_lock(common_dir):
        claim = read_json(path)
        expected = {
            "owner": state["owner"],
            "scope": str(scope),
            "root": state["root"],
            "git_dir": state["git_dir"],
            "binding": immutable_digest(state),
        }
        if any(claim.get(key) != value for key, value in expected.items()):
            fail("refusing to remove a claim owned by another scope")
        path.unlink()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    init = commands.add_parser("scope-init")
    init.add_argument("scope")
    init.add_argument("--project", required=True)
    init.add_argument("--owner", required=True)
    init.add_argument("--allow", action="append", default=[])
    init.add_argument("--protect", action="append", default=[])
    init.set_defaults(handler=command_init)
    diff = commands.add_parser("guard-diff")
    diff.add_argument("scope")
    diff.add_argument(
        "--pre-edit",
        action="store_true",
        help="advisory checkpoint comparison; cannot attribute writers or prevent TOCTOU",
    )
    diff.set_defaults(handler=command_guard)
    checkpoint = commands.add_parser("scope-checkpoint")
    checkpoint.add_argument("scope")
    checkpoint.set_defaults(handler=command_checkpoint)
    close = commands.add_parser("scope-close")
    close.add_argument("scope")
    close.set_defaults(handler=command_close)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        args.handler(args)
        return 0
    except GuardError as error:
        print(f"scope-guard: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"scope-guard: failed closed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
