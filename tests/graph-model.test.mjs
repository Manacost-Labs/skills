import assert from "node:assert/strict";
import test from "node:test";
import {
	indexGraph,
	searchNodes,
	visibleGraph,
} from "../ops/graph-portal/graph-model.mjs";

const nodes = Array.from({ length: 8 }, (_, i) => ({
	id: `n${i}`,
	label: `item${i}`,
	file: `src/${i}.js`,
	repo: "demo",
}));
const graph = {
	nodes,
	edges: [
		{ source: "n0", target: "n1" },
		{ source: "n1", target: "n2" },
	],
};

test("indexes true neighbors, keeps isolates, ignores dangling edges", () => {
	const index = indexGraph({
		...graph,
		edges: [...graph.edges, { source: "n0", target: "absent" }],
	});
	assert.deepEqual([...index.neighbors.get("n1")], ["n0", "n2"]);
	assert.equal(index.neighbors.get("n7").size, 0);
});
test("search covers the full index, including nodes outside the drawing cap", () => {
	const index = indexGraph(graph);
	assert.equal(searchNodes(index, "SRC/7")[0].id, "n7");
	assert.equal(searchNodes(index, "absent").length, 0);
});
test("bounded graph has no dangling links and always includes focused node", () => {
	const result = visibleGraph(indexGraph(graph), 3, "n7");
	assert.equal(result.nodes.length, 3);
	assert.ok(result.nodes.some((n) => n.id === "n7"));
	const ids = new Set(result.nodes.map((n) => n.id));
	assert.ok(result.edges.every((e) => ids.has(e.source) && ids.has(e.target)));
});
test("overview cap keeps every repository represented when capacity permits", () => {
	const diverse = {
		...graph,
		nodes: [
			...nodes,
			{ id: "rare", label: "rare", repo: "other", file: "rare.js" },
		],
	};
	const result = visibleGraph(indexGraph(diverse), 3);
	assert.ok(result.nodes.some((n) => n.repo === "other"));
});
