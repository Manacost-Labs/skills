#!/usr/bin/env node
// Private read-only entrypoint. Never copied into the public release.
import { execFileSync } from "node:child_process";
import { readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
	buildContext,
	searchProjects,
	snapshotStatus,
} from "./graph-model.mjs";

const here = fileURLToPath(new URL(".", import.meta.url));
const readJson = (path, limit = 32 * 1024 * 1024) => {
	if (statSync(path).size > limit) throw new Error("Input too large");
	return JSON.parse(readFileSync(path, "utf8"));
};
const headOf = (root) => {
	try {
		return execFileSync("git", ["-C", root, "rev-parse", "--verify", "HEAD"], {
			encoding: "utf8",
			timeout: 3000,
			stdio: ["ignore", "pipe", "ignore"],
		}).trim();
	} catch {
		return undefined;
	}
};

function main() {
	const [command, query, ...rest] = process.argv.slice(2);
	if (!command || command === "--help") {
		process.stdout.write(
			"Usage: node navigate.mjs find-project|context QUERY [--repo SLUG] [--release DIR] [--max-bytes 8000]\nRead-only metadata retrieval; no source reads, network, indexing or HTTP listener.\n",
		);
		return;
	}
	if (
		!["find-project", "context"].includes(command) ||
		!query?.trim() ||
		query.length > 500
	)
		throw new Error("Invalid command/query");
	const options = {};
	for (let i = 0; i < rest.length; i += 2) {
		if (
			!["--repo", "--release", "--max-bytes"].includes(rest[i]) ||
			!rest[i + 1] ||
			options[rest[i]]
		)
			throw new Error("Invalid options");
		options[rest[i]] = rest[i + 1];
	}
	const catalog = readJson(resolve(here, "projects.json"), 65536).projects;
	const roots = new Map(
		readFileSync(resolve(here, "repositories.tsv"), "utf8")
			.split("\n")
			.filter((line) => line.trim() && !line.startsWith("#"))
			.map((line) => {
				const [slug, , root] = line.split("\t");
				return [slug, root];
			}),
	);
	const found = searchProjects(catalog, query);
	if (command === "find-project") {
		process.stdout.write(
			`${JSON.stringify({
				ambiguous: found[0]?.ambiguous || false,
				projects: found.map(({ project, reasons }) => ({
					slug: project.slug,
					label: project.label,
					purpose: project.purpose,
					root: roots.get(project.slug),
					reasons,
					entryPoints: project.entryPoints,
				})),
			})}\n`,
		);
		return;
	}
	const slug =
		options["--repo"] || (!found[0]?.ambiguous && found[0]?.project.slug);
	const project = catalog.find((item) => item.slug === slug);
	if (!project || !roots.has(slug))
		throw new Error(
			"Choose a repository with find-project, then pass --repo SLUG",
		);
	const release = resolve(
		options["--release"] || "/var/www/graph.kolodahearthstone.com/current",
	);
	const data = readJson(resolve(release, "graphs", `${slug}.json`));
	if (
		data.schema !== 1 ||
		data.repo !== slug ||
		!Array.isArray(data.files?.nodes) ||
		!Array.isArray(data.files?.edges)
	)
		throw new Error("Invalid graph");
	const head = headOf(roots.get(slug));
	const output = buildContext(data, project, query, {
		maxBytes:
			options["--max-bytes"] === undefined
				? 8000
				: Number(options["--max-bytes"]),
		head,
	});
	// No newline: the requested byte ceiling includes the complete stdout response.
	process.stdout.write(output);
	if (snapshotStatus(data.commit, head).state === "stale")
		process.stderr.write(
			"Index is stale; verify selected paths against current source.\n",
		);
}

try {
	main();
} catch {
	process.stderr.write(
		"Navigation failed: check command, query, repository, release and limits. Use --help.\n",
	);
	process.exitCode = 1;
}
