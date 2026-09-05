"""Behavior/security contract for the public graph projection."""

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "ops/graph-portal/export_graph.py"


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("graph_export", MODULE)
        cls.exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.exporter)

    def node(self, identifier, file, label="run"):
        return {
            "id": identifier,
            "label": label,
            "source_file": file,
            "source_location": "L12",
            "context": "do not publish",
        }

    def test_real_edges_collapse_by_file_without_self_edges(self):
        raw = {
            "nodes": [
                self.node("a", "src/a.py"),
                self.node("b", "src/a.py"),
                self.node("c", "src/b.py"),
            ],
            "links": [
                {"source": "a", "target": "b", "relation": "calls"},
                {"source": "a", "target": "c", "relation": "calls"},
                {"source": "b", "target": "c", "relation": "references"},
            ],
        }
        result = self.exporter.project(raw, "demo", "Demo", "Test", "abc")
        self.assertEqual(len(result["symbols"]["nodes"]), 3)
        self.assertEqual(len(result["files"]["nodes"]), 2)
        self.assertEqual(len(result["files"]["edges"]), 1)
        self.assertEqual(result["files"]["edges"][0]["weight"], 2)
        self.assertNotIn("context", str(result))
        self.assertEqual(result["symbols"]["nodes"][0]["line"], 12)

    def test_rejects_sensitive_absolute_traversal_and_dangling_links(self):
        paths = [
            "/srv/projects/private.py",
            "../escape.py",
            "src/../../x.py",
            ".env",
            "src/.env.production",
            "keys/private.key",
            "id_rsa",
            "credentials.json",
            "src\\windows.py",
            "src/ok.py",
        ]
        raw = {
            "nodes": [self.node(str(i), file) for i, file in enumerate(paths)],
            "links": [
                {"source": "0", "target": "9"},
                {"source": "9", "target": "missing"},
            ],
        }
        result = self.exporter.project(raw, "demo", "Demo", "Test", "abc")
        self.assertEqual([n["file"] for n in result["symbols"]["nodes"]], ["src/ok.py"])
        self.assertEqual(result["symbols"]["edges"], [])

    def test_aggregate_namespaces_nodes_without_fabricating_links(self):
        raw = {"nodes": [self.node("same", "index.js")], "links": []}
        parts = [
            self.exporter.project(raw, slug, slug, "Test", "abc")
            for slug in ["one", "two"]
        ]
        result = self.exporter.aggregate(parts)
        self.assertEqual(len({n["id"] for n in result["files"]["nodes"]}), 2)
        self.assertEqual(result["files"]["edges"], [])
        self.assertEqual(result["stats"]["symbols"], 2)

    def test_catalog_allowlist_and_manifest_identity(self):
        import json

        catalog = json.loads((MODULE.parent / "projects.json").read_text())
        slugs = [p["slug"] for p in catalog["projects"]]
        self.exporter.validate_catalog(catalog, slugs)
        self.assertEqual(len(slugs), 11)
        with self.assertRaises(ValueError):
            self.exporter.validate_catalog(catalog, slugs[:-1])
        for field, value in (
            ("source_text", "not public"),
            ("entryPoints", ["../escape"]),
            ("entryPoints", [".env"]),
            ("status", "probably primary"),
            ("domains", ["https://user:pass@example.com"]),
        ):
            bad = json.loads(json.dumps(catalog))
            bad["projects"][0][field] = value
            with self.assertRaises(ValueError, msg=field):
                self.exporter.validate_catalog(bad, slugs)


if __name__ == "__main__":
    unittest.main()
