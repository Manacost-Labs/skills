"""Offline browser checks: every request is fulfilled from local test assets."""

import argparse
import json
import mimetypes
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument(
    "--assets",
    type=Path,
    default=Path(__file__).resolve().parents[1] / "ops/graph-portal",
)
parser.add_argument("--screenshots", type=Path)
parser.add_argument("--real-data", action="store_true")
parser.add_argument("--all-repos", action="store_true")
args = parser.parse_args()
nodes = [
    {
        "id": f"demo:f{i}",
        "label": f"file{i}.py",
        "file": f"src/file{i}.py",
        "repo": "demo",
        "kind": "file",
        "symbols": 2,
    }
    for i in range(24)
]
graph = {
    "nodes": nodes,
    "edges": [{"source": "demo:f0", "target": n["id"], "weight": 1} for n in nodes[1:]],
}
stats = {"files": 24, "symbols": 48, "links": 23}
repo = {
    "repo": "demo",
    "label": "Demo",
    "group": "Test",
    "stats": stats,
    "commit": "abc123",
}
symbols = {
    "nodes": [
        {**n, "id": n["id"].replace(":f", ":s"), "kind": "symbol"} for n in nodes
    ],
    "edges": [
        {
            **e,
            "source": e["source"].replace(":f", ":s"),
            "target": e["target"].replace(":f", ":s"),
        }
        for e in graph["edges"]
    ],
}
data = {**repo, "schema": 1, "files": graph, "symbols": symbols, "repositories": [repo]}
errors = []
failed = set()
timings = {}
nginx_conf = (
    Path(__file__).resolve().parents[1] / "ops/nginx/graph.kolodahearthstone.com.conf"
)
csp = re.search(
    r'add_header Content-Security-Policy "([^"]+)"', nginx_conf.read_text()
)[1]


def respond(route):
    url = urlparse(route.request.url)
    path = url.path.lstrip("/") or "index.html"
    if path in failed:
        return route.fulfill(status=503, body="test failure")
    if not args.real_data:
        if path == "repositories.tsv":
            return route.fulfill(body="demo\tDemo\tTest\nsecond\tSecond\tTest\n")
        if path == "projects.json":
            return route.fulfill(
                json={
                    "schema": 1,
                    "projects": [
                        {
                            "slug": slug,
                            "label": label,
                            "purpose": "Тестовый проект для проверки навигации",
                            "aliases": [alias],
                            "capabilities": [],
                            "stack": ["Python"],
                            "domains": [],
                            "entryPoints": ["src/file0.py"],
                            "status": "unverified",
                        }
                        for slug, label, alias in [
                            ("demo", "Demo", "образец"),
                            ("second", "Second", "второй"),
                        ]
                    ],
                }
            )
        if path.startswith("graphs/"):
            value = {**data, "repo": path.split("/")[-1].replace(".json", "")}
            return route.fulfill(json=value)
        if path == "built-at.txt":
            return route.fulfill(body="2026-09-04T20:00:00Z")
    target = args.assets / path
    if not target.is_file() or not target.resolve().is_relative_to(
        args.assets.resolve()
    ):
        return route.fulfill(status=404)
    mime = (
        "text/javascript"
        if target.suffix in {".js", ".mjs"}
        else mimetypes.guess_type(target)[0] or "text/plain"
    )
    route.fulfill(
        path=target, content_type=mime, headers={"Content-Security-Policy": csp}
    )


with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium", args=["--disable-dev-shm-usage"]
    )
    context = browser.new_context(
        viewport={"width": 1440, "height": 960}, service_workers="block"
    )
    context.route("**/*", respond)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(error.stack or str(error)))
    page.on(
        "console",
        lambda msg: (
            errors.append(msg.text) if msg.type == "error" and not failed else None
        ),
    )
    started = time.monotonic()
    page.goto("https://graph.test/", wait_until="networkidle")
    expect(page.locator("#graph-canvas")).to_be_visible()
    expect(page.locator("#graph-canvas")).to_have_attribute(
        "data-ready", "true", timeout=30000
    )
    expect(page.locator("iframe")).to_have_count(0)
    timings["initialReadySeconds"] = round(time.monotonic() - started, 2)
    if not args.real_data:
        page.locator("#search").fill("где у нас второй")
        page.locator('[data-project="second"]').click()
        expect(page.locator("#current-title")).to_have_text("Second")
        expect(page.locator("#graph-canvas")).to_have_attribute("data-ready", "true")
        page.locator("#search").fill("образец")
        page.locator('[data-project="demo"]').click()
        expect(page.locator("#current-title")).to_have_text("Demo")
        expect(page.locator("#graph-canvas")).to_have_attribute("data-ready", "true")
        expect(page.locator("#snapshot-state")).to_contain_text("HEAD не проверен")
        page.locator("#prepare-context").click()
        packed = page.locator("#context-preview").input_value()
        assert len(packed.encode("utf-8")) <= 8000
        assert json.loads(packed)["repo"] == "demo"
        page.locator("#search").fill("космический корабль")
        expect(page.locator("#search-results")).to_contain_text("Ничего не найдено")
        page.keyboard.press("Escape")
        page.goto("https://graph.test/", wait_until="networkidle")
        expect(page.locator("#graph-canvas")).to_have_attribute("data-ready", "true")
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=args.screenshots / "graph-native-desktop.png")
    initial_zoom = page.locator("#zoom-level").inner_text()
    page.get_by_role("button", name="Увеличить", exact=True).click()
    expect(page.locator("#zoom-level")).not_to_have_text(initial_zoom)
    page.get_by_role("button", name="Вписать граф", exact=True).click()
    page.locator("#graph-canvas").focus()
    previous_transform = page.locator("#graph-canvas").get_attribute("data-transform")
    page.keyboard.press("ArrowLeft")
    expect(page.locator("#graph-canvas")).not_to_have_attribute(
        "data-transform", previous_transform
    )
    page.get_by_role("button", name="Вписать граф", exact=True).click()
    page.keyboard.press("Control+k")
    expect(page.locator("#search")).to_be_focused()
    if not args.real_data:
        page.locator("#search").fill("src/file3")
        page.locator("#search-results button").first.click()
        expect(page.locator("#detail-title")).to_have_text("file3.py")
        expect(page.locator("#detail-path")).to_have_text("src/file3.py")
        expect(page.locator("#neighbors button")).to_have_count(1)
        page.locator("#neighbors button").first.click()
        expect(page.locator("#detail-title")).to_have_text("file0.py")
        page.get_by_role("button", name="Закрыть детали").click()
        page.locator('#repository-list button[data-repo="demo"]').click()
        expect(page).to_have_url("https://graph.test/?repo=demo")
        page.get_by_role("button", name="Символы", exact=True).click()
        expect(
            page.get_by_role("button", name="Символы", exact=True)
        ).to_have_attribute("aria-pressed", "true")
        page.go_back()
        expect(page.locator("#current-title")).to_have_text("Весь сервер")
        failed.add("graphs/second.json")
        page.locator('#repository-list button[data-repo="second"]').click()
        expect(page.locator("#status")).to_contain_text("Не удалось")
        failed.clear()
        page.get_by_role("button", name="Повторить").click()
        expect(page.locator("#graph-canvas")).to_have_attribute("data-ready", "true")
    if args.all_repos:
        slugs = [
            line.split("\t")[0]
            for line in (args.assets / "repositories.tsv").read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        for slug in slugs:
            started = time.monotonic()
            page.locator(f'#repository-list button[data-repo="{slug}"]').click()
            expect(page.locator("#graph-canvas")).to_have_attribute(
                "data-ready", "true", timeout=30000
            )
            page.get_by_role("button", name="Символы", exact=True).click()
            expect(page.locator("#graph-canvas")).to_have_attribute(
                "data-ready", "true", timeout=30000
            )
            page.locator("#entry-nodes button").first.click()
            expect(page.locator("#detail-title")).not_to_be_empty()
            page.get_by_role("button", name="Закрыть детали").click()
            timings[slug] = round(time.monotonic() - started, 2)
        page.locator('#repository-list button[data-repo="whole-server"]').click()
        expect(page.locator("#graph-canvas")).to_have_attribute(
            "data-ready", "true", timeout=30000
        )
    page.set_viewport_size({"width": 390, "height": 844})
    expect(page.locator("#repository-select")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator("#repository-select").select_option("whole-server")
    expect(page.locator("#graph-canvas")).to_have_attribute("data-ready", "true")
    if args.screenshots:
        page.screenshot(path=args.screenshots / "graph-native-mobile.png")
    for viewport in [
        {"width": 320, "height": 740},
        {"width": 768, "height": 900},
        {"width": 1024, "height": 900},
    ]:
        page.set_viewport_size(viewport)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("#project-info").click()
        expect(page.locator("#overview")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#inspector")).to_be_hidden()
    assert not errors, errors
    print(
        json.dumps(
            {
                "browser": "passed",
                "consoleErrors": errors,
                "offline": True,
                "realData": args.real_data,
                "timings": timings,
            }
        )
    )
    browser.close()
