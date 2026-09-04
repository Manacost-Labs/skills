// Finite, deterministic layout, off the UI thread. No idle simulation.
self.onmessage = ({ data }) => {
	const { nodes, edges, aggregate } = data;
	const key = (node) =>
		aggregate
			? node.repo
			: node.file.split("/").slice(0, -1).slice(0, 2).join("/") || "root";
	const buckets = new Map();
	for (const node of nodes) {
		const group = key(node);
		if (!buckets.has(group)) buckets.set(group, []);
		buckets.get(group).push(node);
	}
	const groups = [...buckets].sort((a, b) => b[1].length - a[1].length);
	const positions = new Map(),
		clusters = [];
	groups.forEach(([name, members], i) => {
		const radius = Math.max(36, Math.sqrt(members.length) * 11);
		let x = 0,
			y = 0;
		if (i) {
			for (let step = 0; step < 20000; step++) {
				const angle = step * 0.11,
					distance = 9 * Math.sqrt(step);
				x = Math.cos(angle) * distance;
				y = Math.sin(angle) * distance;
				if (
					clusters.every(
						(c) => Math.hypot(c.x - x, c.y - y) > c.radius + radius + 35,
					)
				)
					break;
			}
		}
		clusters.push({ name, x, y, radius, repo: members[0].repo });
		members.forEach((node, j) => {
			const distance = Math.sqrt((j + 0.5) / members.length) * radius * 0.84;
			const angle = j * 2.3999632297;
			positions.set(node.id, {
				id: node.id,
				x: x + Math.cos(angle) * distance,
				y: y + Math.sin(angle) * distance,
				cx: x,
				cy: y,
				vx: 0,
				vy: 0,
				group: name,
			});
		});
	});
	const points = [...positions.values()];
	const links = edges
		.map((e) => [positions.get(e.source), positions.get(e.target)])
		.filter(([a, b]) => a && b);
	for (let tick = 0; tick < 100; tick++) {
		const alpha = 0.45 * (1 - tick / 105),
			cells = new Map();
		for (const p of points) {
			const cell = `${Math.floor(p.x / 24)},${Math.floor(p.y / 24)}`;
			if (!cells.has(cell)) cells.set(cell, []);
			cells.get(cell).push(p);
			p.vx += (p.cx - p.x) * 0.002 * alpha;
			p.vy += (p.cy - p.y) * 0.002 * alpha;
		}
		for (const [a, b] of links) {
			if (a.group !== b.group) continue;
			const dx = b.x - a.x,
				dy = b.y - a.y,
				length = Math.hypot(dx, dy) || 1;
			const force = ((length - 24) / length) * 0.017 * alpha;
			a.vx += dx * force;
			a.vy += dy * force;
			b.vx -= dx * force;
			b.vy -= dy * force;
		}
		for (const a of points) {
			const cx = Math.floor(a.x / 24),
				cy = Math.floor(a.y / 24);
			for (let x = cx - 1; x <= cx + 1; x++)
				for (let y = cy - 1; y <= cy + 1; y++) {
					for (const b of cells.get(`${x},${y}`) || []) {
						if (a === b) continue;
						const dx = a.x - b.x,
							dy = a.y - b.y,
							d2 = Math.max(1, dx * dx + dy * dy);
						if (d2 > 576) continue;
						a.vx += (dx / d2) * 7 * alpha;
						a.vy += (dy / d2) * 7 * alpha;
					}
				}
			a.x += a.vx = Math.max(-8, Math.min(8, a.vx * 0.6));
			a.y += a.vy = Math.max(-8, Math.min(8, a.vy * 0.6));
		}
	}
	self.postMessage({
		nodes: points.map(({ id, x, y, group }) => ({ id, x, y, group })),
		clusters,
	});
};
