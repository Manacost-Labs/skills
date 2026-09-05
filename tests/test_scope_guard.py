"""Integration tests for the scope-guard command-line contract."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY = Path(__file__).resolve().parents[1]
GUARD = REPOSITORY / "scripts" / "scope_guard.py"


def load_scope_guard():
    specification = importlib.util.spec_from_file_location(
        "scope_guard_test_module", GUARD
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class ScopeGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "guard@example.test")
        self.git("config", "user.name", "Scope Guard")
        self.write("src/owned.txt", "original\n")
        self.write("src/other.txt", "original\n")
        self.write("tests/kept.txt", "original\n")
        self.write(".env", "TOKEN=original\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=self.repo, text=True, capture_output=True, check=True
        )

    def write(self, name: str, content: str) -> None:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def command(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(GUARD), *args], text=True, capture_output=True
        )
        if ok and result.returncode:
            self.fail(f"command failed: {result.stderr}")
        if not ok:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def initialize(
        self, name: str = "scope", *allow: str, protect: tuple[str, ...] = ()
    ) -> Path:
        scope = self.base / f"{name}.json"
        args = ["scope-init", str(scope), "--project", str(self.repo), "--owner", name]
        for pattern in allow:
            args.extend(("--allow", pattern))
        for pattern in protect:
            args.extend(("--protect", pattern))
        self.command(*args)
        return scope

    def guard(self, scope: Path, ok: bool = True, *extra: str) -> None:
        self.command("guard-diff", str(scope), *extra, ok=ok)

    def test_allowed_edit_passes_and_scope_close_releases_claim(self) -> None:
        scope = self.initialize("owner", "src/owned.txt")
        self.write("src/owned.txt", "changed\n")
        self.guard(scope)
        self.command("scope-close", str(scope))
        self.initialize("replacement", "src/owned.txt")

    def test_outside_protected_and_new_env_changes_fail(self) -> None:
        cases = (
            ("outside", "src/other.txt", "changed\n", ("src/owned.txt",), ()),
            (
                "protected",
                "src/owned.txt",
                "changed\n",
                ("src/**",),
                ("src/owned.txt",),
            ),
            ("env", ".env.local", "TOKEN=new\n", ("src/**",), ()),
        )
        for name, path, content, allow, protect in cases:
            with self.subTest(name=name):
                scope = self.initialize(name, *allow, protect=protect)
                self.write(path, content)
                self.guard(scope, ok=False)
                self.command("scope-close", str(scope))

    def test_baseline_dirty_paths_must_remain_byte_and_index_identical(self) -> None:
        self.write("src/owned.txt", "before scope\n")
        allowed = self.initialize("dirty-allowed", "src/owned.txt")
        self.guard(allowed)
        self.write("src/owned.txt", "different but still modified\n")
        self.guard(allowed, ok=False)
        self.command("scope-close", str(allowed))

        self.git("checkout", "--", "src/owned.txt")
        self.write("tests/kept.txt", "before scope\n")
        outside = self.initialize("dirty-outside", "src/owned.txt")
        self.write("src/owned.txt", "allowed work\n")
        self.guard(outside)

    def test_staged_unstaged_untracked_deleted_and_renamed_allowed_changes_pass(
        self,
    ) -> None:
        scope = self.initialize("states", "src/**", "new/**")
        self.write("src/owned.txt", "staged\n")
        self.git("add", "src/owned.txt")
        self.write("src/other.txt", "unstaged\n")
        self.write("new/untracked.txt", "new\n")
        (self.repo / "tests/kept.txt").unlink()
        self.git("mv", "src/other.txt", "src/renamed.txt")
        # The deletion is outside the allowlist, and must be rejected.
        self.guard(scope, ok=False)

        self.git("restore", "--staged", "tests/kept.txt")
        self.git("checkout", "--", "tests/kept.txt")
        self.guard(scope)

    def test_allowed_deletion_and_rename_need_both_rename_paths_allowed(self) -> None:
        scope = self.initialize("rename", "src/**")
        self.git("rm", "src/owned.txt")
        self.git("mv", "src/other.txt", "src/renamed.txt")
        self.guard(scope)

    def test_invalid_globs_existing_scope_and_wrong_head_fail_closed(self) -> None:
        bad = self.base / "bad.json"
        self.command(
            "scope-init",
            str(bad),
            "--project",
            str(self.repo),
            "--owner",
            "bad",
            "--allow",
            "../src/**",
            ok=False,
        )
        self.command(
            "scope-init",
            str(bad),
            "--project",
            str(self.repo),
            "--owner",
            "bad",
            "--allow",
            "[",
            ok=False,
        )
        scope = self.initialize("head", "src/**")
        self.write("src/owned.txt", "committed\n")
        self.git("add", "src/owned.txt")
        self.git("commit", "-qm", "other head")
        self.guard(scope, ok=False)
        self.command(
            "scope-init",
            str(scope),
            "--project",
            str(self.repo),
            "--owner",
            "again",
            "--allow",
            "src/**",
            ok=False,
        )

    def test_overlapping_claims_fail_and_disjoint_claims_pass(self) -> None:
        first = self.initialize("first", "src/**")
        self.command(
            "scope-init",
            str(self.base / "overlap.json"),
            "--project",
            str(self.repo),
            "--owner",
            "overlap",
            "--allow",
            "src/owned.txt",
            ok=False,
        )
        second = self.initialize("second", "tests/**")
        self.command("scope-close", str(second))
        self.command("scope-close", str(first))

    def test_checkpoint_pre_edit_is_advisory_and_malformed_scope_fails(self) -> None:
        scope = self.initialize("checkpoint", "src/**")
        self.guard(scope, True, "--pre-edit")
        self.write("src/other.txt", "clean file changed\n")
        self.guard(scope, False, "--pre-edit")
        self.write("src/owned.txt", "first\n")
        self.command("scope-checkpoint", str(scope))
        self.guard(scope, True, "--pre-edit")
        self.write("src/owned.txt", "second\n")
        self.guard(scope, False, "--pre-edit")
        self.guard(scope)
        self.command("scope-checkpoint", str(scope))
        self.write("src/new-owned.txt", "new after checkpoint\n")
        self.guard(scope, False, "--pre-edit")
        malformed = self.base / "malformed.json"
        malformed.write_text(json.dumps({"schema": 999}), encoding="utf-8")
        self.guard(malformed, ok=False)

    def test_malformed_baseline_checkpoint_and_empty_allow_fail_closed(self) -> None:
        scope = self.initialize("maps", "src/**")
        state = json.loads(scope.read_text(encoding="utf-8"))
        for name, mutate in (
            (
                "baseline",
                lambda item: item.__setitem__("baseline", {"fingerprints": []}),
            ),
            (
                "checkpoint",
                lambda item: item.__setitem__("checkpoint", {"fingerprints": []}),
            ),
            ("allow", lambda item: item.__setitem__("allow", [])),
        ):
            with self.subTest(name=name):
                candidate = self.base / f"{name}.json"
                malformed = dict(state)
                mutate(malformed)
                candidate.write_text(json.dumps(malformed), encoding="utf-8")
                result = self.command("guard-diff", str(candidate), ok=False)
                self.assertNotIn("Traceback", result.stderr)

    def test_ignored_protected_files_are_tracked_without_reading_contents(self) -> None:
        self.write(".gitignore", ".env*\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "ignore environment files")
        self.write(".env.before", "before\n")
        existing = self.initialize("ignored-existing", "src/**")
        self.guard(existing)
        self.write(".env.before", "after\n")
        self.guard(existing, ok=False)
        self.command("scope-close", str(existing))

        created = self.initialize("ignored-created", "src/**")
        self.write(".env.after", "created after init\n")
        self.guard(created, ok=False)

    def test_valid_schema_immutable_state_tampering_is_rejected(self) -> None:
        scope = self.initialize("tamper", "src/owned.txt")
        state = json.loads(scope.read_text(encoding="utf-8"))
        state["allow"] = ["**"]
        scope.write_text(json.dumps(state), encoding="utf-8")
        result = self.command("guard-diff", str(scope), ok=False)
        self.assertNotIn("Traceback", result.stderr)

    def test_symlinked_ancestor_rejects_before_opening_external_source_bytes(
        self,
    ) -> None:
        scope = self.initialize("symlink-parent", "src", "src/**")
        guard = load_scope_guard()
        external = self.base / "external"
        external.mkdir()
        (external / "owned.txt").write_text("outside bytes\n", encoding="utf-8")
        source = self.repo / "src"
        source.rename(self.base / "original-src")
        source.symlink_to(external, target_is_directory=True)
        opened: list[Path] = []
        original_open = Path.open

        def track_open(path: Path, *args, **kwargs):
            if path == source / "owned.txt":
                opened.append(path)
            return original_open(path, *args, **kwargs)

        state = json.loads(scope.read_text(encoding="utf-8"))
        with mock.patch.object(Path, "open", new=track_open):
            with self.assertRaises(guard.GuardError) as error:
                guard.guard(state, scope, pre_edit=True)
        self.assertIn("symlinked ancestor", str(error.exception))
        self.assertEqual(opened, [])


if __name__ == "__main__":
    unittest.main()
