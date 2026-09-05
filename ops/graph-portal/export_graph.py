"""Project local AST graphs to a small, allowlisted public navigation schema."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath


def safe_file(value):
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or any(ord(c) < 32 for c in value):
        return False
    return not any(
        part.startswith((".env", "id_rsa", "service-account"))
        or part in {".npmrc", ".pypirc", "credentials.json"}
        or part.endswith((".key", ".pem", ".p12", ".pfx", ".kdbx"))
        for part in path.parts
    )


def project(raw, slug, label, group, commit):
    symbols, files, ids, file_ids = [], [], {}, {}
    for node in raw.get("nodes", []):
        file = node.get("source_file")
        if not safe_file(file) or str(node.get("id")) in ids:
            continue
        identifier = f"{slug}:s{len(symbols)}"
        ids[str(node["id"])] = identifier
        location = re.search(r"\d+", str(node.get("source_location", "")))
        symbol = {
            "id": identifier,
            "label": str(node.get("label", "?"))[:160],
            "file": file,
            "line": int(location[0]) if location else None,
            "kind": "class" if node.get("_callable_class") else "symbol",
            "repo": slug,
        }
        symbols.append(symbol)
        if file not in file_ids:
            file_id = f"{slug}:f{len(files)}"
            file_ids[file] = file_id
            files.append(
                {
                    "id": file_id,
                    "label": PurePosixPath(file).name,
                    "file": file,
                    "kind": "file",
                    "repo": slug,
                    "symbols": 0,
                }
            )
        files[int(file_ids[file].rsplit("f", 1)[1])]["symbols"] += 1

    by_id = {node["id"]: node for node in symbols}
    symbol_edges, file_edges = Counter(), Counter()
    for edge in raw.get("links", raw.get("edges", [])):
        source, target = (
            ids.get(str(edge.get("source"))),
            ids.get(str(edge.get("target"))),
        )
        if source is None or target is None or source == target:
            continue
        relation = edge.get("relation", "references")
        # Free-form extraction context is deliberately not part of the public schema.
        if relation not in {
            "calls",
            "references",
            "imports",
            "contains",
            "inherits",
            "implements",
        }:
            relation = "references"
        symbol_edges[(source, target, relation)] += 1
        a, b = file_ids[by_id[source]["file"]], file_ids[by_id[target]["file"]]
        if a != b:
            file_edges[(a, b)] += 1

    return {
        "schema": 1,
        "repo": slug,
        "label": label,
        "group": group,
        "commit": commit,
        "stats": {
            "files": len(files),
            "symbols": len(symbols),
            "links": sum(symbol_edges.values()),
            "excluded": len(raw.get("nodes", [])) - len(symbols),
        },
        "files": {
            "nodes": files,
            "edges": [
                {"source": a, "target": b, "weight": count}
                for (a, b), count in file_edges.items()
            ],
        },
        "symbols": {
            "nodes": symbols,
            "edges": [
                {"source": a, "target": b, "relation": relation, "weight": count}
                for (a, b, relation), count in symbol_edges.items()
            ],
        },
    }


def aggregate(parts):
    return {
        "schema": 1,
        "repo": "whole-server",
        "label": "Весь сервер",
        "repositories": [
            {key: part[key] for key in ("repo", "label", "group", "commit", "stats")}
            for part in parts
        ],
        "stats": {
            key: sum(p["stats"][key] for p in parts)
            for key in ("files", "symbols", "links", "excluded")
        },
        "files": {
            key: [item for p in parts for item in p["files"][key]]
            for key in ("nodes", "edges")
        },
    }


def validate_catalog(catalog, slugs):
    if set(catalog) != {"schema", "projects"} or catalog["schema"] != 1:
        raise ValueError("Invalid catalog schema")
    projects = catalog["projects"]
    if not isinstance(projects, list) or len(projects) != len(slugs):
        raise ValueError("Invalid catalog size")
    fields = {
        "slug",
        "label",
        "purpose",
        "aliases",
        "capabilities",
        "stack",
        "domains",
        "status",
        "entryPoints",
        "evidence",
    }
    seen = set()
    for item in projects:
        if not isinstance(item, dict) or set(item) != fields:
            raise ValueError("Unexpected public catalog fields")
        slug = item["slug"]
        if not isinstance(slug, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9-]{0,63}", slug
        ):
            raise ValueError("Invalid catalog slug")
        if slug in seen or slug not in slugs:
            raise ValueError("Catalog/manifest mismatch")
        seen.add(slug)
        if item["status"] not in {
            "primary",
            "experimental",
            "archive",
            "fork",
            "unverified",
        }:
            raise ValueError("Invalid project status")
        for field in fields - {"slug", "status"}:
            value = item[field]
            values = [value] if field in {"label", "purpose"} else value
            if not isinstance(values, list) or len(values) > 30:
                raise ValueError("Invalid catalog list")
            if any(
                not isinstance(v, str)
                or not v
                or len(v) > 500
                or any(ord(c) < 32 for c in v)
                for v in values
            ):
                raise ValueError("Invalid catalog text")
        if not item["evidence"]:
            raise ValueError("Catalog evidence required")
        if any(not safe_file(p) for p in item["entryPoints"] + item["evidence"]):
            raise ValueError("Unsafe catalog path")
        if any(
            not re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", d) for d in item["domains"]
        ):
            raise ValueError("Invalid catalog domain")


def validate_release(path):
    slugs = [
        line.split("\t")[0]
        for line in (path / "repositories.tsv").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not slugs or len(slugs) != len(set(slugs)) or "whole-server" in slugs:
        raise ValueError("Invalid repository manifest")
    expected = {
        "index.html",
        "app.js",
        "styles.css",
        "graph-model.mjs",
        "layout-worker.js",
        "repositories.tsv",
        "built-at.txt",
    } | {f"graphs/{slug}.json" for slug in [*slugs, "whole-server"]}
    # Preserve old immutable releases; new builders include the reviewed catalog.
    if (path / "projects.json").is_file():
        expected.add("projects.json")
        validate_catalog(json.loads((path / "projects.json").read_text()), slugs)
    actual = {str(file.relative_to(path)) for file in path.rglob("*") if file.is_file()}
    if actual != expected:
        raise ValueError("Unexpected or missing public assets")
    for slug in [*slugs, "whole-server"]:
        data = json.loads((path / "graphs" / f"{slug}.json").read_text())
        if data.get("schema") != 1 or data.get("repo") != slug:
            raise ValueError("Invalid graph identity")
        for level in ("files",) if slug == "whole-server" else ("files", "symbols"):
            graph = data[level]
            ids = {node["id"] for node in graph["nodes"]}
            if len(ids) != len(graph["nodes"]):
                raise ValueError("Duplicate node ids")
            for node in graph["nodes"]:
                if not safe_file(node["file"]) or node["repo"] not in slugs:
                    raise ValueError("Unsafe navigation metadata")
                if set(node) - {
                    "id",
                    "label",
                    "file",
                    "line",
                    "kind",
                    "repo",
                    "symbols",
                }:
                    raise ValueError("Unexpected public node fields")
            for edge in graph["edges"]:
                if edge["source"] not in ids or edge["target"] not in ids:
                    raise ValueError("Dangling graph edge")
                if set(edge) - {"source", "target", "relation", "weight"}:
                    raise ValueError("Unexpected public edge fields")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--validate-catalog", action="store_true")
    parser.add_argument("--catalog-manifest", type=Path)
    parser.add_argument("--repo", nargs=4, metavar=("SLUG", "LABEL", "GROUP", "COMMIT"))
    args = parser.parse_args()
    if args.validate_catalog or args.catalog_manifest:
        source = args.output if args.validate_catalog else args.inputs[0]
        catalog = json.loads(source.read_text())
        validate_catalog(catalog, [p["slug"] for p in catalog["projects"]])
        if args.catalog_manifest:
            slugs = [
                row.split("\t")[0]
                for row in args.catalog_manifest.read_text().splitlines()
                if row.strip() and not row.startswith("#")
            ]
            catalog["projects"] = [p for p in catalog["projects"] if p["slug"] in slugs]
            validate_catalog(catalog, slugs)
            if not args.validate_catalog:
                args.output.write_text(json.dumps(catalog, ensure_ascii=False) + "\n")
        return
    if args.validate:
        validate_release(args.output)
        print("Public navigation data validated")
        return
    if not args.inputs:
        parser.error("at least one graph input is required")
    data = [json.loads(path.read_text()) for path in args.inputs]
    result = project(data[0], *args.repo) if args.repo else aggregate(data)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    print(
        f"Public graph {result['repo']}: {result['stats']['files']} files, {result['stats']['symbols']} symbols"
    )


if __name__ == "__main__":
    main()
