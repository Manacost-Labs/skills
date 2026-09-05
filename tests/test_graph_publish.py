"""Publication failure regressions; every privileged operation is sandboxed."""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "ops/graph-portal"


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="graph-publish-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.release = self.root / "release"
        (self.release / "graphs").mkdir(parents=True)
        for asset in (
            "index.html",
            "app.js",
            "styles.css",
            "graph-model.mjs",
            "layout-worker.js",
        ):
            shutil.copyfile(PORTAL / asset, self.release / asset)
        (self.release / "built-at.txt").write_text("2026-09-04T00:00:00Z")
        (self.release / "repositories.tsv").write_text("demo\tDemo\tTest\n")
        spec = importlib.util.spec_from_file_location(
            "exporter", PORTAL / "export_graph.py"
        )
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        raw = {
            "nodes": [{"id": "a", "label": "run", "source_file": "main.py"}],
            "links": [],
        }
        data = exporter.project(raw, "demo", "Demo", "Test", "abc")
        (self.release / "graphs/demo.json").write_text(json.dumps(data))
        (self.release / "graphs/whole-server.json").write_text(
            json.dumps(exporter.aggregate([data]))
        )
        previous = self.root / "web/releases/previous"
        previous.mkdir(parents=True)
        (self.root / "web/current").symlink_to("releases/previous")
        binary = self.root / "bin"
        binary.mkdir()
        shutil.copyfile(ROOT / "tests/fixtures/graph-publish-sudo.py", binary / "sudo")
        (binary / "sudo").chmod(0o755)
        # Only relocate the hard-coded deployment root; execute the real script.
        self.publisher = binary / "publish-graph-portal.sh"
        source = (PORTAL / "publish-graph-portal.sh").read_text()
        self.assertEqual(
            source.count("web_root=/var/www/graph.kolodahearthstone.com"), 1
        )
        self.publisher.write_text(
            source.replace(
                "web_root=/var/www/graph.kolodahearthstone.com",
                f"web_root={self.root}/web",
            )
        )
        self.publisher.chmod(0o755)
        shutil.copyfile(PORTAL / "export_graph.py", binary / "export_graph.py")
        self.env = {
            **os.environ,
            "PATH": f"{binary}:{os.environ['PATH']}",
            "GRAPH_PUBLISH_TEST_ROOT": str(self.root),
        }

    def publish(self, **flags):
        return subprocess.run(
            [str(self.publisher), str(self.release)],
            env={**self.env, **flags},
            capture_output=True,
            text=True,
            check=False,
        )

    def test_reload_failure_restores_previous_link_and_attempts_recovery(self):
        result = self.publish(GRAPH_PUBLISH_FAIL_RELOAD="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.readlink(self.root / "web/current"), "releases/previous")
        self.assertEqual((self.root / "reload-count").read_text(), "2")
        self.assertIn("recovery reload verified", result.stderr)

    def test_validation_failure_does_not_change_active_release(self):
        result = self.publish(GRAPH_PUBLISH_FAIL_VALIDATE="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.readlink(self.root / "web/current"), "releases/previous")

    def test_changed_copy_is_rejected_before_activation(self):
        result = self.publish(GRAPH_PUBLISH_TAMPER="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.readlink(self.root / "web/current"), "releases/previous")
        self.assertIn("changed during publication", result.stderr)

    def test_success_and_immutable_destination(self):
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.readlink(self.root / "web/current"), "releases/release")
        self.assertNotEqual(self.publish().returncode, 0)

    def test_catalog_is_allowed_but_private_cli_is_rejected(self):
        catalog = json.loads((PORTAL / "projects.json").read_text())
        sample = dict(catalog["projects"][0], slug="demo")
        (self.release / "projects.json").write_text(
            json.dumps({"schema": 1, "projects": [sample]})
        )
        shutil.copyfile(PORTAL / "navigate.mjs", self.release / "navigate.mjs")
        self.assertNotEqual(self.publish().returncode, 0)
        (self.release / "navigate.mjs").unlink()
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
