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

const stopWords = new Set(
	"где у нас как найти проект для мне нужно нужен сделать исправить добавить изменить наш наша на в и с по из the a an where find project for to".split(
		" ",
	),
);

function terms(value) {
	return [
		...new Set(
			String(value)
				.normalize("NFKC")
				.toLowerCase()
				.replaceAll("ё", "е")
				.match(/[\p{L}\p{N}]+/gu) || [],
		),
	].filter((word) => !stopWords.has(word));
}

export function searchProjects(projects, query, limit = 5) {
	const words = terms(query.slice(0, 500));
	if (!words.length) return [];
	const fields = projects.map((project) =>
		[
			{
				weight: 5,
				values: [
					project.slug,
					project.label,
					...(project.aliases || []),
					...(project.domains || []),
				],
			},
			{ weight: 3, values: project.capabilities || [] },
			{ weight: 1, values: project.stack || [] },
		].map((field) => ({
			...field,
			tokens: new Set(field.values.flatMap(terms)),
		})),
	);
	const frequency = new Map(
		words.map((word) => [
			word,
			fields.filter((parts) => parts.some((field) => field.tokens.has(word)))
				.length,
		]),
	);
	const results = projects
		.map((project, i) => {
			let score = 0;
			const reasons = [];
			for (const word of words) {
				const field = fields[i].find((part) => part.tokens.has(word));
				if (!field) continue;
				score +=
					field.weight *
					(1 + Math.log(1 + projects.length / frequency.get(word)));
				reasons.push(word);
			}
			return { project, score, reasons };
		})
		.filter((result) => result.score > 0)
		.sort(
			(a, b) =>
				b.score - a.score || a.project.slug.localeCompare(b.project.slug),
		);
	const sameCoverage =
		results.length > 1 &&
		results[0].reasons.join() === results[1].reasons.join();
	const ambiguous =
		results.length > 1 &&
		(results[1].score >= results[0].score * 0.8 ||
			(sameCoverage && results[1].score >= results[0].score * 0.5));
	return results.slice(0, limit).map((result) => ({ ...result, ambiguous }));
}

export function snapshotStatus(commit, head) {
	if (!commit || !head) return { state: "unknown", label: "HEAD не проверен" };
	return commit === head
		? { state: "current", label: "Совпадает с HEAD на момент проверки" }
		: { state: "stale", label: "Индекс отстаёт от HEAD" };
}

function safeContextPath(value) {
	return (
		typeof value === "string" &&
		value.length > 0 &&
		value.length <= 500 &&
		!value.startsWith("/") &&
		!value.includes("\\") &&
		![...value].some((char) => char.charCodeAt(0) < 32) &&
		!value
			.split("/")
			.some(
				(part) =>
					part === ".." ||
					part.startsWith(".") ||
					/credentials|secret|id_rsa|service-account/i.test(part) ||
					/\.(key|pem|p12|pfx|db|sqlite|dump)$/i.test(part),
			)
	);
}

// Metadata only: never copy free-form extraction context or source text.
// The serialized UTF-8 byte cap is exact, not an approximate tokenizer count.
export function buildContext(
	data,
	project,
	query,
	{ maxBytes = 8000, maxFiles = 8, head } = {},
) {
	if (
		!Number.isInteger(maxBytes) ||
		maxBytes < 512 ||
		maxBytes > 32000 ||
		!Number.isInteger(maxFiles) ||
		maxFiles < 1 ||
		maxFiles > 8
	)
		throw new RangeError("Context limits: 512–32000 bytes, 1–8 files");
	if (
		!/^[a-z0-9][a-z0-9-]{0,63}$/.test(project.slug) ||
		data.repo !== project.slug
	)
		throw new Error("Graph/project mismatch");
	const words = terms(query.slice(0, 500));
	const nodes = data.files.nodes.filter(
		(node) => node.repo === project.slug && safeContextPath(node.file),
	);
	const byId = new Map(nodes.map((node) => [node.id, node]));
	const symbolsByFile = new Map();
	for (const symbol of data.symbols?.nodes || []) {
		if (symbol.repo !== project.slug || !safeContextPath(symbol.file)) continue;
		if (!symbolsByFile.has(symbol.file)) symbolsByFile.set(symbol.file, []);
		symbolsByFile.get(symbol.file).push(symbol);
	}
	const ranked = nodes
		.map((node) => {
			const tokens = terms(
				node.file +
					" " +
					(node.label || "") +
					" " +
					(symbolsByFile.get(node.file) || [])
						.map((symbol) => symbol.label)
						.join(" "),
			);
			const matches = words.filter((word) =>
				tokens.some((token) => token.includes(word)),
			).length;
			const entry = (project.entryPoints || []).some(
				(path) => node.file === path || node.file.startsWith(`${path}/`),
			);
			return { node, score: matches * 10 + (entry ? 1 : 0) };
		})
		.filter((item) => item.score > 0)
		.sort(
			(a, b) => b.score - a.score || a.node.file.localeCompare(b.node.file),
		);
	const chosen = new Map();
	for (const { node } of ranked.slice(0, Math.min(3, maxFiles)))
		chosen.set(node.id, node);
	const seeds = new Set(chosen.keys());
	const relevant = new Set(ranked.map(({ node }) => node.id));
	// Only one-hop, real edges; no inferred cross-project relationships.
	for (const edge of data.files.edges) {
		let neighbor;
		if (seeds.has(edge.source) && byId.has(edge.target)) neighbor = edge.target;
		else if (seeds.has(edge.target) && byId.has(edge.source))
			neighbor = edge.source;
		if (neighbor !== undefined) {
			relevant.add(neighbor);
			if (chosen.size < maxFiles) chosen.set(neighbor, byId.get(neighbor));
		}
	}
	for (const { node } of ranked) {
		if (chosen.size >= maxFiles) break;
		chosen.set(node.id, node);
	}
	const result = {
		schema: 1,
		repo: project.slug,
		commit: String(data.commit || "").slice(0, 64),
		freshness: snapshotStatus(data.commit, head).state,
		scope: "navigation-metadata; verify in source",
		files: [],
		edges: [],
		truncated: false,
	};
	const encode = () => JSON.stringify(result);
	const fits = () => new TextEncoder().encode(encode()).length <= maxBytes;
	// Reserve the longer false literal while packing, so final status always fits.
	for (const node of chosen.values()) {
		result.files.push({ file: node.file });
		if (!fits()) {
			result.files.pop();
			result.truncated = true;
		}
	}
	const included = new Set(result.files.map((node) => node.file));
	for (const edge of data.files.edges) {
		const a = byId.get(edge.source)?.file,
			b = byId.get(edge.target)?.file;
		if (!included.has(a) || !included.has(b)) continue;
		result.edges.push({ source: a, target: b, relation: "file-dependency" });
		if (!fits()) {
			result.edges.pop();
			result.truncated = true;
			break;
		}
	}
	// Relationships take priority over optional symbol names within the budget.
	for (const file of result.files) {
		const candidates = (symbolsByFile.get(file.file) || [])
			.filter((symbol) => Number.isInteger(symbol.line) && symbol.line > 0)
			.slice(0, 3);
		if (!candidates.length) continue;
		file.symbols = candidates.map((symbol) => ({
			label: String(symbol.label).slice(0, 120),
			line: symbol.line,
		}));
		if (!fits()) {
			delete file.symbols;
			result.truncated = true;
		}
	}
	result.truncated ||= relevant.size > result.files.length;
	if (!fits()) throw new RangeError("Context metadata exceeds byte budget");
	return encode();
}
