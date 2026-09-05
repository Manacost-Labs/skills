"""Real Git/Gitleaks regressions with synthetic, noncredential fixtures."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_changed_secrets.py"


class SecretCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        (self.root / "example.py").write_text("answer = 42\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=True
        )

    def scan(self, base="HEAD"):
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=self.root,
            env={**os.environ, "VERIFY_BASE": base},
            capture_output=True,
            check=False,
        )

    def test_sensitive_symlink_is_rejected_without_following_it(self):
        (self.root / "credentials.txt").symlink_to("/nonexistent-sensitive-file")
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"sensitive path", result.stderr)

    def test_tracked_binary_and_oversized_postimages_fail_closed(self):
        for content in (b"opaque\0data", b"x" * 2_000_001):
            with self.subTest(size=len(content)):
                (self.root / "example.py").write_bytes(content)
                self.assertNotEqual(self.scan().returncode, 0)

    @unittest.skipUnless(shutil.which("gitleaks"), "Gitleaks unavailable")
    def test_unchanged_key_is_kept_as_secret_detection_context(self):
        label = b"sec" + b"ret =\n"
        value = b'"p8eP6x2qJ3vH9sK4mN7bR5tY1uW0zA6c"\n'
        target = self.root / "settings.txt"
        target.write_bytes(label)
        self.git("add", "settings.txt")
        self.git("commit", "-qm", "context label")
        target.write_bytes(label + value)
        self.assertNotEqual(self.scan().returncode, 0)

    def test_symlinked_ancestor_is_rejected_without_following_it(self):
        with tempfile.TemporaryDirectory() as external:
            (Path(external) / "example.py").write_text(
                "sensitive fixture outside scope"
            )
            directory = self.root / "src"
            directory.mkdir()
            target = directory / "example.py"
            target.write_text("original")
            self.git("add", "src/example.py")
            self.git("commit", "-qm", "source")
            target.unlink()
            directory.rmdir()
            directory.symlink_to(external, target_is_directory=True)
            result = self.scan()
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(b"sensitive fixture", result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("gitleaks"), "Gitleaks unavailable")
    def test_staged_secret_is_not_hidden_by_a_clean_worktree(self):
        fake = "gh" + "p_" + "aB9Cd3Ef7Gh2Jk6Lm4Np8Qr5St1Uv0Wx9Yz2"
        target = self.root / "example.py"
        target.write_text(f'token = "{fake}"\n')
        self.git("add", "example.py")
        target.write_text("answer = 42\n")
        self.assertNotEqual(self.scan().returncode, 0)

    @unittest.skipUnless(
        shutil.which("gitleaks"),
        "Gitleaks unavailable: gate separately fails if required tool missing",
    )
    def test_clean_change_and_synthetic_added_token(self):
        (self.root / "example.py").write_text("answer = 43\n")
        self.assertEqual(self.scan().returncode, 0)
        fake = "gh" + "p_" + "aB9Cd3Ef7Gh2Jk6Lm4Np8Qr5St1Uv0Wx9Yz2"
        (self.root / "new.py").write_text(f'token = "{fake}"\n')
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(fake.encode(), result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
