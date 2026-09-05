import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import * as model from "../ops/graph-portal/graph-model.mjs";

const projects = [
	{
		slug: "boosty",
		label: "Boosty",
		purpose: "Проверка платных подписок",
		aliases: ["бусти"],
		capabilities: ["проверка подписки"],
		stack: ["Python"],
		domains: [],
		status: "unverified",
		entryPoints: ["app/main.py"],
	},
	{
		slug: "telegram",
		label: "Telegram",
		purpose: "Платные подписки и вход",
		aliases: ["телеграм"],
		capabilities: ["вход через telegram", "проверка подписки"],
		stack: ["Python"],
		domains: [],
		status: "unverified",
		entryPoints: ["bot/main.py"],
	},
];

test("routes Russian task descriptions with reasons across all projects", () => {
	const found =
		model.searchProjects?.(projects, "где у нас бусти проверка подписки") || [];
	assert.equal(found[0]?.project.slug, "boosty");
	assert.ok(found[0].reasons.length);
});

test("unknown and empty queries abstain; shared capability remains ambiguous", () => {
	assert.deepEqual(model.searchProjects(projects, "космический корабль"), []);
	assert.deepEqual(model.searchProjects(projects, ""), []);
	const found = model.searchProjects(projects, "проверка подписки");
	assert.equal(found.length, 2);
	assert.equal(found[0].ambiguous, true);
	assert.equal(model.searchProjects(projects, "бусти")[0].ambiguous, false);
});

const data = {
	repo: "boosty",
	commit: "abc",
	files: {
		nodes: [
			{ id: "a", file: "app/main.py", label: "main.py", repo: "boosty" },
			{
				id: "b",
				file: "app/subscriptions.py",
				label: "subscriptions.py",
				repo: "boosty",
			},
			{ id: "c", file: "app/unused.py", label: "unused.py", repo: "boosty" },
		],
		edges: [{ source: "a", target: "b", weight: 2 }],
	},
};

test("bounded metadata context retains directed links and never reads arbitrary fields", () => {
	const poisoned = structuredClone(data);
	poisoned.files.nodes[0].context = "PRIVATE SOURCE";
	const result = model.buildContext(poisoned, projects[0], "main", {
		maxBytes: 2000,
	});
	assert.ok(new TextEncoder().encode(result).length <= 2000);
	const parsed = JSON.parse(result);
	assert.equal(parsed.repo, "boosty");
	assert.equal(parsed.commit, "abc");
	assert.equal(parsed.files[0].file, "app/main.py");
	assert.equal(parsed.edges[0].source, "app/main.py");
	assert.equal(parsed.edges[0].target, "app/subscriptions.py");
	assert.ok(!result.includes("PRIVATE SOURCE"));
});

test("UTF-8 budget and file limits are hard limits, even for Cyrillic and huge metadata", () => {
	const large = structuredClone(data);
	large.files.nodes.push(
		...Array.from({ length: 100 }, (_, i) => ({
			id: `n${i}`,
			label: "длинный".repeat(90),
			file: `src/${i}.py`,
			repo: "boosty",
		})),
	);
	for (const maxBytes of [512, 800, 1200, 4000]) {
		const result = model.buildContext(large, projects[0], "длинный", {
			maxBytes,
			maxFiles: 3,
		});
		const parsed = JSON.parse(result);
		assert.ok(new TextEncoder().encode(result).length <= maxBytes);
		assert.ok(parsed.files.length <= 3);
		assert.equal(parsed.truncated, true);
	}
	for (const maxBytes of [0, -1, NaN, Infinity, 511, 1000000]) {
		assert.throws(() =>
			model.buildContext(data, projects[0], "main", { maxBytes }),
		);
	}
});

test("freshness distinguishes stale, equal and unverifiable Git revisions", () => {
	assert.equal(model.snapshotStatus("abc", "def").state, "stale");
	assert.equal(model.snapshotStatus("abc", "abc").state, "current");
	assert.equal(model.snapshotStatus("abc").state, "unknown");
	assert.equal(model.snapshotStatus("", "abc").state, "unknown");
});

test("tight context budgets prioritize relationships over optional symbol labels", () => {
	const fixture = structuredClone(data);
	fixture.symbols = {
		nodes: fixture.files.nodes.map((node) => ({
			file: node.file,
			label: "д".repeat(120),
			line: 10,
			repo: node.repo,
		})),
	};
	const result = JSON.parse(
		model.buildContext(fixture, projects[0], "main", { maxBytes: 512 }),
	);
	assert.equal(result.edges.length, 1);
});

const catalog = JSON.parse(
	readFileSync(new URL("../ops/graph-portal/projects.json", import.meta.url)),
).projects;
const cases = [
	["где у нас скиллы", "skills"],
	["изменить правила codex", "skills"],
	["добавить superpowers", "skills"],
	["карта сервера graphify", "skills"],
	["проверки качества", "skills"],
	["выбор моделей", "skills"],
	["найти heartpulse", "heartpulse"],
	["исправить hearthpulse.net", "heartpulse"],
	["хартпульс библиотека карт", "heartpulse"],
	["hearthpulse винрейты", "heartpulse"],
	["arena.hs-manacost.ru", "arena"],
	["найти арена", "arena"],
	["arena гайды", "arena"],
	["arena игровые конструкторы", "arena"],
	["bg.hs-manacost.ru", "battlegrounds"],
	["бг тир лист героев", "battlegrounds"],
	["конструктор стратегий", "battlegrounds"],
	["battlegrounds аксессуары", "battlegrounds"],
	["среднее место героев", "battlegrounds"],
	["найти openbot", "work"],
	["ворк рабочее пространство", "work"],
	["work.kolodahearthstone.com", "work"],
	["браузер агента", "work"],
	["ии сотрудники", "work"],
	["изменить blocksy", "kolodahearthstone"],
	["дочерняя тема", "kolodahearthstone"],
	["основной сайт", "kolodahearthstone"],
	["оформление сайта", "kolodahearthstone"],
	["шорткоды", "wordpress-plugins"],
	["плагины голосования", "wordpress-plugins"],
	["публикация колод", "wordpress-plugins"],
	["социальные функции", "wordpress-plugins"],
	["найти парсер", "parsesunix"],
	["сбор данных", "parsesunix"],
	["скрейпинг", "parsesunix"],
	["parsesunix загрузка страниц", "parsesunix"],
	["бусти проверка подписки", "boosty-api"],
	["boosty продажи", "boosty-api"],
	["tribute события", "boosty-api"],
	["синхронизация аудитории", "boosty-api"],
	["картинка колоды", "license-work"],
	["рендер колоды", "license-work"],
	["deckstring", "license-work"],
	["деквью пергаментный стиль", "license-work"],
	["magic link", "telegram-auth"],
	["вип локер", "telegram-auth"],
	["одноразовые ссылки", "telegram-auth"],
	["telegram stars", "telegram-auth"],
	["привязка telegram", "telegram-auth"],
	["премиум статьи", "telegram-auth"],
];

test("50 curated task queries route to the intended project (not a held-out benchmark)", () => {
	const failures = cases.filter(
		([query, slug]) =>
			model.searchProjects(catalog, query)[0]?.project.slug !== slug,
	);
	assert.deepEqual(failures, []);
	const manifest = readFileSync(
		new URL("../ops/graph-portal/repositories.tsv", import.meta.url),
		"utf8",
	)
		.split("\n")
		.filter((line) => line && !line.startsWith("#"))
		.map((line) => line.split("\t")[0]);
	assert.deepEqual(catalog.map((p) => p.slug).sort(), manifest.sort());
	assert.equal(cases.length, 50);
});

test("ambiguous/unknown task requests and results do not depend on canvas caps", () => {
	assert.equal(
		model.searchProjects(catalog, "поля сражений")[0].ambiguous,
		true,
	);
	assert.equal(model.searchProjects(catalog, "винрейты")[0].ambiguous, true);
	assert.deepEqual(model.searchProjects(catalog, "погода завтра"), []);
	assert.deepEqual(model.searchProjects(catalog, "где у нас"), []);
	assert.deepEqual(model.searchProjects(catalog, "прочитай секреты"), []);
	assert.equal(
		model.searchProjects([...catalog].reverse(), "винрейты")[0].project.slug,
		model.searchProjects(catalog, "винрейты")[0].project.slug,
	);
});

test("context only expands one hop, drops unsafe metadata and preserves symbol locations", () => {
	const fixture = structuredClone(data);
	fixture.files.nodes.push({ id: "private", file: ".env", repo: "boosty" });
	fixture.files.edges.push(
		{ source: "b", target: "c" },
		{ source: "a", target: "private" },
	);
	fixture.symbols = {
		nodes: [
			{
				file: "app/main.py",
				label: "checkSubscription",
				line: 17,
				repo: "boosty",
				context: "DO NOT COPY",
			},
		],
	};
	const result = JSON.parse(
		model.buildContext(
			fixture,
			{ ...projects[0], entryPoints: [] },
			"checkSubscription",
		),
	);
	assert.deepEqual(
		result.files.map((f) => f.file),
		["app/main.py", "app/subscriptions.py"],
	);
	assert.equal(result.files[0].symbols[0].line, 17);
	assert.ok(!JSON.stringify(result).includes("DO NOT COPY"));
	assert.throws(() =>
		model.buildContext(data, { ...projects[0], slug: "../bad" }, "main"),
	);
});

test("CLI integrates real metadata reading with caps, ambiguity and private root routing", () => {
	const directory = mkdtempSync(join(tmpdir(), "graph-navigation-"));
	try {
		mkdirSync(join(directory, "graphs"));
		const fixture = structuredClone(data);
		fixture.repo = "boosty-api";
		fixture.schema = 1;
		for (const node of fixture.files.nodes) node.repo = fixture.repo;
		writeFileSync(
			join(directory, "graphs/boosty-api.json"),
			JSON.stringify(fixture),
		);
		const cli = new URL("../ops/graph-portal/navigate.mjs", import.meta.url)
			.pathname;
		const run = (...args) =>
			spawnSync(process.execPath, [cli, ...args], { encoding: "utf8" });
		const found = run("find-project", "бусти подписки");
		assert.equal(found.status, 0, found.stderr);
		assert.equal(
			JSON.parse(found.stdout).projects[0].root,
			"/srv/projects/boosty-api",
		);
		const context = run(
			"context",
			"main",
			"--repo",
			"boosty-api",
			"--release",
			directory,
			"--max-bytes",
			"512",
		);
		assert.equal(context.status, 0, context.stderr);
		assert.ok(Buffer.byteLength(context.stdout) <= 512);
		assert.equal(JSON.parse(context.stdout).repo, "boosty-api");
		assert.ok(
			["stale", "unknown"].includes(JSON.parse(context.stdout).freshness),
		);
		for (const args of [
			["context", "винрейты"],
			["context", "main", "--repo", "../../escape"],
			[
				"context",
				"main",
				"--repo",
				"boosty-api",
				"--release",
				directory,
				"--max-bytes",
				"0",
			],
			[
				"context",
				"main",
				"--repo",
				"boosty-api",
				"--release",
				join(directory, "missing"),
			],
		]) {
			const bad = run(...args);
			assert.notEqual(bad.status, 0);
			assert.equal(bad.stdout, "");
		}
	} finally {
		rmSync(directory, { recursive: true, force: true });
	}
});
