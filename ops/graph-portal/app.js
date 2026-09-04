import { indexGraph, searchNodes, visibleGraph } from "./graph-model.mjs";

const $ = (selector) => document.querySelector(selector);
const canvas = $("#graph-canvas"),
	ctx = canvas.getContext("2d"),
	stage = $("#stage");
const palette = [
	"#79b8ff",
	"#a995ed",
	"#57c7ad",
	"#efad6c",
	"#eb8caa",
	"#80c2dd",
	"#c5bc7c",
	"#d28ce0",
	"#70c696",
	"#df9580",
	"#92a9ff",
];
const whole = { slug: "whole-server", label: "Весь сервер", group: "Обзор" };
const number = (value) => new Intl.NumberFormat("ru").format(value);
let repositories = [],
	activeRepo = whole,
	dataset,
	index,
	graph,
	positions = new Map(),
	clusters = [];
let selected = null,
	hovered = null,
	level = "files",
	neighborhood = false,
	labels = false;
let transform = { x: 0, y: 0, k: 1 },
	width = 0,
	height = 0,
	worker,
	abort,
	generation = 0,
	frame = 0;
let initialRequest = true;
let layoutVersion = 0;
const cache = new Map(),
	groupColors = new Map();
const color = (node) =>
	activeRepo.slug === "whole-server"
		? repositories.find((r) => r.slug === node.repo)?.color || palette[0]
		: groupColors.get(node.group) || palette[0];

function element(tag, text, className) {
	const el = document.createElement(tag);
	if (text != null) el.textContent = text;
	if (className) el.className = className;
	return el;
}
function dot(value) {
	const el = element("span", null, "repo-dot");
	el.style.setProperty("--cluster", value);
	return el;
}
function status(message, error = false) {
	$("#status").hidden = !message;
	$("#status-text").textContent = message || "";
	$("#retry").hidden = !error;
}
async function json(url, signal) {
	const response = await fetch(url, { signal, cache: "no-cache" });
	if (!response.ok) throw new Error("Graph request failed");
	const value = await response.json();
	if (
		value.schema !== 1 ||
		!Array.isArray(value.files?.nodes) ||
		!Array.isArray(value.files?.edges)
	)
		throw new Error("Invalid graph");
	return value;
}
function closeSearch() {
	$("#search-results").hidden = true;
	$("#search").setAttribute("aria-expanded", "false");
}
function closeDetail() {
	selected = null;
	$("#focus-node").textContent = "Показать окружение";
	$("#detail").hidden = true;
	$("#overview").hidden = false;
	$("#inspector").classList.remove("is-open");
	if (neighborhood) {
		neighborhood = false;
		layout();
	} else drawSoon();
}
async function activate(slug, push = true) {
	activeRepo = [whole, ...repositories].find((r) => r.slug === slug) || whole;
	abort?.abort();
	worker?.terminate();
	const ticket = ++generation;
	abort = new AbortController();
	selected = null;
	hovered = null;
	neighborhood = false;
	index = null;
	dataset = null;
	positions.clear();
	clusters = [];
	graph = null;
	canvas.dataset.ready = "false";
	$("#detail").hidden = true;
	$("#overview").hidden = false;
	$("#inspector").classList.remove("is-open");
	$("#search").value = "";
	closeSearch();
	$("#tooltip").hidden = true;
	if (activeRepo.slug === "whole-server") level = "files";
	$("#symbols-view").disabled = activeRepo.slug === "whole-server";
	$("#symbols-view").title =
		activeRepo.slug === "whole-server"
			? "Выберите репозиторий для просмотра символов"
			: "Функции, классы и другие символы";
	$("#repository-select").value = activeRepo.slug;
	for (const button of document.querySelectorAll("#repository-list button")) {
		const active = button.dataset.repo === activeRepo.slug;
		button.classList.toggle("active", active);
		button.setAttribute("aria-current", active ? "page" : "false");
	}
	$("#current-title").textContent = activeRepo.label;
	$("#current-group").textContent = activeRepo.group;
	$("#graph-summary").textContent = "Загрузка индекса…";
	$("#entry-nodes").replaceChildren();
	$("#legend").replaceChildren();
	$("#stat-files").textContent = "—";
	$("#stat-links").textContent = "—";
	$("#stat-symbols").textContent = "—";
	if (push) {
		const url = new URL(location.href);
		url.search =
			activeRepo.slug === "whole-server"
				? ""
				: `?repo=${encodeURIComponent(activeRepo.slug)}`;
		history.pushState(null, "", url);
	}
	status("Загружаю граф…");
	drawSoon();
	try {
		const slug = activeRepo.slug;
		const received =
			cache.get(slug) ||
			(await json(`/graphs/${encodeURIComponent(slug)}.json`, abort.signal));
		if (ticket !== generation) return;
		dataset = received;
		// Bound retained datasets as well as drawing size.
		if (!cache.has(slug) && cache.size >= 3)
			cache.delete(cache.keys().next().value);
		cache.set(slug, dataset);
		for (const part of dataset.repositories || []) {
			const count = document.querySelector(`[data-repo="${part.repo}"] small`);
			if (count) count.textContent = number(part.stats.files);
		}
		layout();
	} catch (error) {
		if (error.name !== "AbortError" && ticket === generation)
			status("Не удалось загрузить граф. Попробуйте ещё раз.", true);
	}
}
function listNode(node) {
	const button = element("button");
	button.title = node.file;
	button.append(
		dot(repositories.find((r) => r.slug === node.repo)?.color || palette[0]),
		element("span", node.label),
		element("small", number(index.neighbors.get(node.id).size)),
	);
	button.addEventListener("click", () => inspect(node.id, true));
	return button;
}
function layout(focus = null) {
	if (!dataset) return;
	worker?.terminate();
	positions.clear();
	clusters = [];
	hovered = null;
	$("#tooltip").hidden = true;
	const version = ++layoutVersion;
	$("#focus-node").textContent = neighborhood
		? "Вернуть всю карту"
		: "Показать окружение";
	canvas.dataset.ready = "false";
	index = indexGraph(dataset[level] || dataset.files);
	graph = visibleGraph(index, 1800, focus || selected);
	if (neighborhood && selected) {
		const ids = new Set([selected, ...index.neighbors.get(selected)]);
		graph.nodes = graph.nodes.filter((n) => ids.has(n.id));
		const present = new Set(graph.nodes.map((n) => n.id));
		graph.edges = graph.edges.filter(
			(e) => present.has(e.source) && present.has(e.target),
		);
	}
	$("#files-view").setAttribute("aria-pressed", String(level === "files"));
	$("#symbols-view").setAttribute("aria-pressed", String(level === "symbols"));
	$("#map-title").textContent =
		activeRepo.slug === "whole-server"
			? "Связи, которые\nсобирают проекты."
			: activeRepo.label;
	$("#map-description").textContent =
		level === "files"
			? "Каждая точка — файл. Каждая линия — связь в коде."
			: "Функции, классы и их связи. Нажмите на узел, чтобы узнать больше.";
	$("#cluster-help").textContent =
		activeRepo.slug === "whole-server" ? "Один репозиторий" : "Одна папка";
	$("#stat-files").textContent = number(dataset.stats.files);
	$("#stat-symbols").textContent = number(dataset.stats.symbols);
	$("#stat-links").textContent = number(index.edges.length);
	$("#entry-nodes").replaceChildren(...index.ranked.slice(0, 5).map(listNode));
	$("#graph-summary").textContent =
		number(graph.nodes.length) +
		" / " +
		number(index.nodes.size) +
		" узлов · " +
		number(graph.edges.length) +
		" связей" +
		(graph.nodes.length < index.nodes.size ? " · поиск по всему индексу" : "");
	if (!graph.nodes.length) {
		positions.clear();
		clusters = [];
		status("В этом снимке нет доступных узлов.");
		drawSoon();
		return;
	}
	status("Располагаю узлы и связи…");
	const layoutWorker = new Worker("/layout-worker.js");
	worker = layoutWorker;
	const ticket = generation;
	layoutWorker.onmessage = ({ data }) => {
		if (ticket !== generation || version !== layoutVersion) return;
		positions = new Map(
			data.nodes.map((p) => [p.id, { ...index.nodes.get(p.id), ...p }]),
		);
		clusters = data.clusters;
		groupColors.clear();
		clusters.forEach((c, i) => {
			groupColors.set(c.name, palette[i % palette.length]);
		});
		renderLegend();
		fit();
		status(null);
		canvas.dataset.ready = "true";
		layoutWorker.terminate();
		worker = null;
		if (focus) centerNode(focus);
	};
	layoutWorker.onerror = () => {
		if (ticket !== generation || version !== layoutVersion) return;
		status("Не удалось расположить граф. Попробуйте ещё раз.", true);
		layoutWorker.terminate();
	};
	layoutWorker.postMessage({
		...graph,
		aggregate: activeRepo.slug === "whole-server",
	});
}
function renderLegend() {
	$("#legend").replaceChildren();
	for (const cluster of clusters.slice(0, 11)) {
		const label =
			activeRepo.slug === "whole-server"
				? repositories.find((r) => r.slug === cluster.name)?.label ||
					cluster.name
				: cluster.name;
		const button = element("button");
		button.title = label;
		button.append(
			dot(color({ ...cluster, group: cluster.name })),
			element("span", label.length > 25 ? `…${label.slice(-24)}` : label),
		);
		button.addEventListener("click", () => {
			if (activeRepo.slug === "whole-server") activate(cluster.name);
			else {
				transform.k = Math.min(
					2,
					Math.min(width, height) / (cluster.radius * 2.7),
				);
				transform.x = width / 2 - cluster.x * transform.k;
				transform.y = height / 2 - cluster.y * transform.k;
				drawSoon();
			}
		});
		$("#legend").append(button);
	}
}
function inspect(id, center = false) {
	const node = index?.nodes.get(id);
	if (!node) return;
	selected = id;
	closeSearch();
	$("#detail").hidden = false;
	$("#overview").hidden = true;
	$("#inspector").classList.add("is-open");
	$("#detail-kind").textContent =
		node.kind === "file" ? "ФАЙЛ" : node.kind === "class" ? "КЛАСС" : "СИМВОЛ";
	$("#detail-title").textContent = node.label;
	$("#detail-path").textContent =
		node.file + (node.line ? `:${node.line}` : "");
	$("#detail-repo").textContent =
		repositories.find((r) => r.slug === node.repo)?.label || node.repo;
	$("#detail-degree").textContent = number(index.neighbors.get(id).size);
	const adjacent = [...index.neighbors.get(id)].map((key) =>
		index.nodes.get(key),
	);
	$("#neighbors").replaceChildren(...adjacent.slice(0, 80).map(listNode));
	$("#detail-note").textContent =
		adjacent.length > 80
			? "Первые 80 из " +
				number(adjacent.length) +
				" соседей. Все связи выбранного узла подсвечены на карте в пределах отображаемого набора."
			: adjacent.length
				? "На карте выделены доступные соседи. Направление связи показано стрелкой при выборе узла."
				: "В текущем AST-индексе связей не найдено. Это не гарантирует отсутствие динамических зависимостей.";
	$("#open-repository").textContent =
		activeRepo.slug === "whole-server"
			? "Перейти в репозиторий ↗"
			: level === "files"
				? "Найти символы этого файла →"
				: "Показать файлы репозитория";
	$("#open-repository").onclick = async () => {
		if (activeRepo.slug === "whole-server") await activate(node.repo);
		else if (level === "files") {
			level = "symbols";
			neighborhood = false;
			closeDetail();
			layout();
			$("#search").value = node.file;
			showSearch();
		} else {
			level = "files";
			neighborhood = false;
			closeDetail();
			layout();
		}
	};
	if (!positions.has(id) || neighborhood) layout(id);
	else if (center) centerNode(id);
	drawSoon();
}
function centerNode(id) {
	const p = positions.get(id);
	if (!p) return;
	transform.k = Math.max(transform.k, 1.5);
	transform.x = width / 2 - p.x * transform.k;
	transform.y = height / 2 - p.y * transform.k;
	drawSoon();
}
function fit() {
	if (!positions.size) return;
	const points = [...positions.values()];
	const minX = Math.min(...points.map((p) => p.x)) - 35,
		maxX = Math.max(...points.map((p) => p.x)) + 35;
	const minY = Math.min(...points.map((p) => p.y)) - 40,
		maxY = Math.max(...points.map((p) => p.y)) + 40;
	const top = width < 500 ? 135 : 155,
		bottom = 95;
	transform.k = Math.min(
		2.2,
		Math.max(
			0.08,
			Math.min(
				(width - 65) / (maxX - minX),
				(height - top - bottom) / (maxY - minY),
			),
		),
	);
	transform.x = width / 2 - ((minX + maxX) / 2) * transform.k;
	transform.y =
		top + (height - top - bottom) / 2 - ((minY + maxY) / 2) * transform.k;
	drawSoon();
}
function zoom(factor, x = width / 2, y = height / 2) {
	const previous = transform.k;
	transform.k = Math.max(0.08, Math.min(12, previous * factor));
	transform.x = x - ((x - transform.x) * transform.k) / previous;
	transform.y = y - ((y - transform.y) * transform.k) / previous;
	drawSoon();
}
function drawSoon() {
	if (!frame)
		frame = requestAnimationFrame(() => {
			frame = 0;
			draw();
		});
}
function draw() {
	const dpr = Math.min(devicePixelRatio || 1, 2);
	ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
	ctx.clearRect(0, 0, width, height);
	$("#zoom-level").textContent = `${Math.round(transform.k * 100)}%`;
	canvas.dataset.transform = [transform.x, transform.y, transform.k].join(",");
	if (!positions.size) return;
	ctx.translate(transform.x, transform.y);
	ctx.scale(transform.k, transform.k);
	for (const cluster of clusters) {
		const c = color({ ...cluster, group: cluster.name });
		ctx.beginPath();
		ctx.arc(cluster.x, cluster.y, cluster.radius + 12, 0, Math.PI * 2);
		ctx.fillStyle = `${c}05`;
		ctx.fill();
		ctx.strokeStyle = `${c}12`;
		ctx.lineWidth = 1 / transform.k;
		ctx.stroke();
	}
	const active = selected || hovered,
		neighbors = active ? index.neighbors.get(active) : null;
	for (const edge of graph.edges) {
		const a = positions.get(edge.source),
			b = positions.get(edge.target);
		if (!a || !b) continue;
		const highlighted = edge.source === active || edge.target === active;
		ctx.globalAlpha = active ? (highlighted ? 0.85 : 0.045) : 0.26;
		ctx.strokeStyle = highlighted ? "#afd4ff" : color(a);
		ctx.lineWidth = (highlighted ? 1.3 : 0.65) / transform.k;
		ctx.beginPath();
		ctx.moveTo(a.x, a.y);
		ctx.lineTo(b.x, b.y);
		ctx.stroke();
		if (highlighted) {
			const angle = Math.atan2(b.y - a.y, b.x - a.x),
				size = 5 / transform.k;
			const x = a.x + (b.x - a.x) * 0.7,
				y = a.y + (b.y - a.y) * 0.7;
			ctx.beginPath();
			ctx.moveTo(x, y);
			ctx.lineTo(
				x - size * Math.cos(angle - 0.5),
				y - size * Math.sin(angle - 0.5),
			);
			ctx.lineTo(
				x - size * Math.cos(angle + 0.5),
				y - size * Math.sin(angle + 0.5),
			);
			ctx.closePath();
			ctx.fillStyle = "#afd4ff";
			ctx.fill();
		}
	}
	let labelCount = 0;
	for (const p of positions.values()) {
		const degree = index.neighbors.get(p.id).size;
		const isActive = p.id === active,
			related = neighbors?.has(p.id);
		const radius = Math.min(6, 2.3 + Math.log2(degree + 1) * 0.48);
		const c = color(p);
		ctx.globalAlpha = active && !isActive && !related ? 0.15 : 1;
		if (degree > 10 || isActive) {
			ctx.beginPath();
			ctx.arc(p.x, p.y, radius + 3 / transform.k, 0, Math.PI * 2);
			ctx.fillStyle = `${c}20`;
			ctx.fill();
		}
		ctx.beginPath();
		ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
		ctx.fillStyle = isActive ? "#e6f3ff" : c;
		ctx.fill();
		if (isActive) {
			ctx.strokeStyle = "#58a6ff";
			ctx.lineWidth = 1.5 / transform.k;
			ctx.stroke();
		}
		const show =
			isActive ||
			related ||
			(labels && labelCount < 120) ||
			(!active && transform.k > 1.4 && degree > 8 && labelCount < 25);
		if (show) {
			labelCount++;
			ctx.font = `${11 / transform.k}px ui-monospace, monospace`;
			const label = p.label.length > 30 ? `${p.label.slice(0, 29)}…` : p.label;
			ctx.lineWidth = 4 / transform.k;
			ctx.strokeStyle = "#0b1017";
			ctx.strokeText(
				label,
				p.x + radius + 4 / transform.k,
				p.y + 3 / transform.k,
			);
			ctx.fillStyle = isActive ? "#ffffff" : "#c6d6e9";
			ctx.fillText(
				label,
				p.x + radius + 4 / transform.k,
				p.y + 3 / transform.k,
			);
		}
	}
	ctx.globalAlpha = 1;
	if (!active)
		for (const cluster of clusters) {
			if (cluster.radius * transform.k < 24) continue;
			ctx.fillStyle = `${color({ ...cluster, group: cluster.name })}cc`;
			ctx.font = `${10 / transform.k}px -apple-system, sans-serif`;
			ctx.textAlign = "center";
			const label =
				activeRepo.slug === "whole-server"
					? repositories.find((r) => r.slug === cluster.name)?.label ||
						cluster.name
					: cluster.name;
			ctx.fillText(
				label.length > 28 ? `…${label.slice(-27)}` : label,
				cluster.x,
				cluster.y + cluster.radius + 24 / transform.k,
			);
		}
	ctx.textAlign = "left";
}
function hit(x, y) {
	let found = null,
		distance = Infinity;
	for (const p of positions.values()) {
		const d = Math.hypot(
			p.x * transform.k + transform.x - x,
			p.y * transform.k + transform.y - y,
		);
		if (d < Math.max(9, 6 * transform.k) && d < distance) {
			found = p.id;
			distance = d;
		}
	}
	return found;
}
function showSearch() {
	if (!index) return;
	const found = searchNodes(index, $("#search").value);
	$("#search-results").replaceChildren(
		...found.map((node) => {
			const button = element("button");
			button.append(
				element("span", node.label),
				element("small", `${node.repo} / ${node.file}`),
			);
			button.onclick = () => inspect(node.id, true);
			return button;
		}),
	);
	if (!found.length)
		$("#search-results").append(element("p", "Ничего не найдено"));
	$("#search-results").hidden = false;
	$("#search").setAttribute("aria-expanded", "true");
}
$("#search").addEventListener("input", showSearch);
$("#search").addEventListener("focus", () => {
	if ($("#search").value) showSearch();
});
$(".search-wrap").addEventListener("keydown", (event) => {
	const buttons = [...$("#search-results").querySelectorAll("button")];
	const current = buttons.indexOf(document.activeElement);
	if (event.key === "ArrowDown") {
		event.preventDefault();
		buttons[Math.min(current + 1, buttons.length - 1)]?.focus();
	}
	if (event.key === "ArrowUp") {
		event.preventDefault();
		if (current <= 0) $("#search").focus();
		else buttons[current - 1].focus();
	}
	if (event.key === "Enter" && document.activeElement === $("#search"))
		buttons[0]?.click();
});
document.addEventListener("pointerdown", (event) => {
	if (!event.target.closest(".search-wrap")) closeSearch();
});
document.addEventListener("keydown", (event) => {
	if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
		event.preventDefault();
		$("#search").focus();
	}
	if (event.key === "Escape") {
		closeSearch();
		closeDetail();
		canvas.focus();
	}
});
$("#zoom-in").onclick = () => zoom(1.3);
$("#zoom-out").onclick = () => zoom(1 / 1.3);
$("#fit").onclick = () => {
	if (neighborhood) {
		neighborhood = false;
		layout();
	} else fit();
};
$("#labels").onclick = () => {
	labels = !labels;
	$("#labels").setAttribute("aria-pressed", String(labels));
	drawSoon();
};
$("#close-detail").onclick = () => {
	closeDetail();
	canvas.focus();
};
$("#focus-node").onclick = () => {
	neighborhood = !neighborhood;
	$("#focus-node").textContent = neighborhood
		? "Вернуть всю карту"
		: "Показать окружение";
	layout(selected);
};
$("#files-view").onclick = () => {
	level = "files";
	closeDetail();
	layout();
};
$("#symbols-view").onclick = () => {
	if (activeRepo.slug === "whole-server") return;
	level = "symbols";
	closeDetail();
	layout();
};
$("#retry").onclick = () =>
	initialRequest ? init() : activate(activeRepo.slug, false);
canvas.addEventListener(
	"wheel",
	(event) => {
		event.preventDefault();
		const box = canvas.getBoundingClientRect();
		zoom(
			Math.exp(-event.deltaY * 0.0015),
			event.clientX - box.left,
			event.clientY - box.top,
		);
	},
	{ passive: false },
);
canvas.addEventListener("keydown", (event) => {
	if (
		[
			"+",
			"=",
			"-",
			"f",
			"F",
			"ArrowLeft",
			"ArrowRight",
			"ArrowUp",
			"ArrowDown",
		].includes(event.key)
	)
		event.preventDefault();
	if (event.key === "+" || event.key === "=") zoom(1.3);
	if (event.key === "-") zoom(1 / 1.3);
	if (event.key.toLowerCase() === "f") fit();
	if (event.key === "ArrowLeft") transform.x += 40;
	if (event.key === "ArrowRight") transform.x -= 40;
	if (event.key === "ArrowUp") transform.y += 40;
	if (event.key === "ArrowDown") transform.y -= 40;
	drawSoon();
});
const pointers = new Map();
let moved = false,
	pinch = 0;
const local = (event) => {
	const b = canvas.getBoundingClientRect();
	return { x: event.clientX - b.left, y: event.clientY - b.top };
};
canvas.addEventListener("pointerdown", (event) => {
	pointers.set(event.pointerId, local(event));
	canvas.setPointerCapture(event.pointerId);
	moved = false;
	pinch = 0;
});
canvas.addEventListener("pointermove", (event) => {
	const p = local(event),
		previous = pointers.get(event.pointerId);
	if (previous) {
		pointers.set(event.pointerId, p);
		if (pointers.size === 2) {
			const [a, b] = [...pointers.values()],
				distance = Math.hypot(a.x - b.x, a.y - b.y);
			if (pinch) zoom(distance / pinch, (a.x + b.x) / 2, (a.y + b.y) / 2);
			pinch = distance;
			moved = true;
		} else {
			const dx = p.x - previous.x,
				dy = p.y - previous.y;
			if (Math.abs(dx) + Math.abs(dy) > 1) moved = true;
			transform.x += dx;
			transform.y += dy;
			drawSoon();
		}
		$("#tooltip").hidden = true;
		return;
	}
	const next = hit(p.x, p.y);
	if (next !== hovered) {
		hovered = next;
		drawSoon();
	}
	$("#tooltip").hidden = !next;
	if (next) {
		$("#tooltip").textContent = index.nodes.get(next).label;
		$("#tooltip").style.left = `${Math.min(p.x + 14, width - 240)}px`;
		$("#tooltip").style.top = `${Math.max(8, p.y - 32)}px`;
	}
});
canvas.addEventListener("pointerup", (event) => {
	const p = local(event);
	if (!moved) {
		const id = hit(p.x, p.y);
		if (id) inspect(id);
		else closeDetail();
	}
	pointers.delete(event.pointerId);
	pinch = 0;
});
canvas.addEventListener("pointercancel", (event) => {
	pointers.delete(event.pointerId);
	pinch = 0;
	moved = true;
});
canvas.addEventListener("pointerleave", () => {
	hovered = null;
	$("#tooltip").hidden = true;
	drawSoon();
});
new ResizeObserver(() => {
	width = stage.clientWidth;
	height = stage.clientHeight;
	const dpr = Math.min(devicePixelRatio || 1, 2);
	canvas.width = Math.round(width * dpr);
	canvas.height = Math.round(height * dpr);
	if (positions.size) fit();
	else drawSoon();
}).observe(stage);

async function init() {
	status("Загружаю список проектов…");
	try {
		const response = await fetch("/repositories.tsv", { cache: "no-cache" });
		if (!response.ok) throw new Error("Manifest request failed");
		repositories = (await response.text())
			.split("\n")
			.filter((line) => line.trim() && !line.startsWith("#"))
			.map((line, i) => {
				const [slug, label, group] = line.split("\t");
				if (!/^[a-z0-9][a-z0-9-]*$/.test(slug) || !label || !group)
					throw new Error("Invalid manifest");
				return { slug, label, group, color: palette[i % palette.length] };
			});
		$("#repo-count").textContent = repositories.length;
		$("#repository-list").replaceChildren();
		$("#repository-select").replaceChildren();
		let group = "";
		for (const repo of [whole, ...repositories]) {
			if (repo !== whole && repo.group !== group) {
				group = repo.group;
				$("#repository-list").append(element("div", group, "repo-group"));
			}
			const button = element("button", null, "repo-button");
			button.dataset.repo = repo.slug;
			button.append(
				dot(repo.color || palette[0]),
				element("span", repo.label, "repo-name"),
				element("small", repo === whole ? repositories.length : ""),
			);
			button.onclick = () => activate(repo.slug);
			$("#repository-list").append(button);
			const option = element("option", repo.label);
			option.value = repo.slug;
			$("#repository-select").append(option);
		}
		initialRequest = false;
		await activate(new URLSearchParams(location.search).get("repo"), false);
		fetch("/built-at.txt", { cache: "no-cache" })
			.then((r) => (r.ok ? r.text() : ""))
			.then((value) => {
				const date = new Date(value.trim());
				if (!Number.isNaN(date.valueOf()))
					$("#build-date").textContent =
						`Снимок ${date.toLocaleDateString("ru")}`;
			})
			.catch(() => {});
	} catch {
		status("Не удалось загрузить список проектов.", true);
	}
}
$("#repository-select").onchange = () =>
	activate($("#repository-select").value);
window.addEventListener("popstate", () =>
	activate(new URLSearchParams(location.search).get("repo"), false),
);
init();
