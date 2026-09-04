export function indexGraph(graph) {
	const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
	const neighbors = new Map(graph.nodes.map((node) => [node.id, new Set()]));
	const edges = graph.edges.filter(
		(edge) => nodes.has(edge.source) && nodes.has(edge.target),
	);
	for (const edge of edges) {
		neighbors.get(edge.source).add(edge.target);
		neighbors.get(edge.target).add(edge.source);
	}
	const ranked = [...nodes.values()].sort(
		(a, b) => neighbors.get(b.id).size - neighbors.get(a.id).size,
	);
	return { nodes, neighbors, edges, ranked };
}

export function searchNodes(index, query, limit = 40) {
	const term = query.trim().toLocaleLowerCase();
	return index.ranked
		.filter(
			(node) =>
				!term ||
				`${node.label} ${node.file} ${node.repo}`
					.toLocaleLowerCase()
					.includes(term),
		)
		.slice(0, limit);
}

export function visibleGraph(index, limit = 1800, focus = null) {
	const ids = new Set();
	if (index.nodes.has(focus)) {
		ids.add(focus);
		for (const id of index.neighbors.get(focus)) {
			if (ids.size >= limit) break;
			ids.add(id);
		}
	}
	const repos = new Set([...ids].map((id) => index.nodes.get(id).repo));
	for (const node of index.ranked) {
		if (ids.size >= limit) break;
		if (!repos.has(node.repo)) {
			ids.add(node.id);
			repos.add(node.repo);
		}
	}
	for (const node of index.ranked) {
		if (ids.size >= limit) break;
		ids.add(node.id);
	}
	return {
		nodes: [...ids].map((id) => index.nodes.get(id)),
		edges: index.edges.filter(
			(edge) => ids.has(edge.source) && ids.has(edge.target),
		),
	};
}
