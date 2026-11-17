#!/usr/bin/env python3
"""Build the Wildland Pest Systems site.

Edit the page bodies in _src/pages/ and the shared header/footer in
_src/layout.html, then run:   python3 _build.py

Each page file starts with a small header block:
    <!--
    title: Page title
    description: Meta description
    path: /baio/
    -->
Anything after a line containing <!-- @scripts --> is placed at the end of <body>.
Anything after a line containing <!-- @head --> (and before @scripts) goes in <head>.

Screenshot shortcodes (images live in /screenshots/, 1600x900 webp):
    [[shot file.png | Alt text | Window label]]   desktop window frame
    [[phone file.png | Alt text]]                 phone frame

Folders and files starting with "_" are not published by GitHub Pages.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_src"

NAV = [
    ("/baio/", "BAIO"),
    ("/mobile/", "Mobile"),
    ("/standalone/", "Standalone apps"),
    ("/roadmap/", "Roadmap"),
    ("/scanner/", "Coming soon"),
    ("/faq/", "FAQ"),
]


def nav_html(active):
    desk, mob = [], []
    for href, label in NAV:
        on = active.startswith(href)
        cur = ' aria-current="page"' if on else ""
        cls = "text-white" if on else "hover:text-white"
        desk.append(f'            <a href="{href}" class="{cls}"{cur}>{label}</a>')
        mcls = "block py-2 text-white" if on else "block py-2"
        mob.append(f'        <a href="{href}" class="{mcls}"{cur}>{label}</a>')
    return "\n".join(desk), "\n".join(mob)


def shot(m):
    parts = [p.strip() for p in m.group(1).split("|")]
    file, alt = parts[0], parts[1]
    label = parts[2] if len(parts) > 2 else alt
    return (
        '<figure class="shot rounded-xl overflow-hidden bg-ink-900 border border-white/10 glow">'
        '<div class="flex items-center gap-2 px-4 h-9 bg-ink-800 border-b border-white/5">'
        '<span class="w-2.5 h-2.5 rounded-full bg-white/10"></span>'
        '<span class="w-2.5 h-2.5 rounded-full bg-white/10"></span>'
        '<span class="w-2.5 h-2.5 rounded-full bg-moss-500"></span>'
        f'<span class="ml-2 font-mono text-[11px] text-gray-500 truncate">{label}</span></div>'
        f'<img src="/screenshots/{file}" alt="{alt}" loading="lazy" width="1600" height="900" class="zoomable">'
        "</figure>"
    )


def phone(m):
    parts = [p.strip() for p in m.group(1).split("|")]
    file, alt = parts[0], parts[1]
    return (
        '<figure class="phone w-60 sm:w-64 shrink-0 rounded-[2.2rem] bg-ink-950 border border-white/10 p-2.5 glow">'
        f'<img src="/screenshots/{file}" alt="{alt}" loading="lazy" class="zoomable rounded-[1.8rem]">'
        "</figure>"
    )


def build_page(src, layout):
    text = src.read_text(encoding="utf-8")
    header = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = dict(
        (k.strip(), v.strip())
        for k, v in (line.split(":", 1) for line in header.group(1).strip().splitlines() if ":" in line)
    )
    body = text[header.end():]
    scripts = head = ""
    if "<!-- @scripts -->" in body:
        body, scripts = body.split("<!-- @scripts -->", 1)
    if "<!-- @head -->" in body:
        body, head = body.split("<!-- @head -->", 1)
    body = re.sub(r"\[\[shot (.*?)\]\]", shot, body)
    body = re.sub(r"\[\[phone (.*?)\]\]", phone, body)

    path = meta["path"]
    desk, mob = nav_html(path)
    html = layout
    for key, val in {
        "title": meta["title"], "description": meta["description"], "path": path,
        "nav": desk, "mobilenav": mob, "body": body.strip("\n"),
        "head": head.strip("\n"), "scripts": scripts.strip("\n"),
    }.items():
        html = html.replace("{{" + key + "}}", val)

    if src.stem == "404":
        out = ROOT / "404.html"
    elif path == "/":
        out = ROOT / "index.html"
    else:
        out = ROOT / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return path, out


def main():
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    paths = []
    for src in sorted((SRC / "pages").glob("*.html")):
        path, out = build_page(src, layout)
        print(f"{path:14} -> {out.relative_to(ROOT)}")
        if src.stem != "404":
            paths.append(path)
    urls = "\n".join(f"  <url><loc>https://www.wildlandpest.com{p}</loc></url>" for p in sorted(paths))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://www.wildlandpest.com/sitemap.xml\n")


if __name__ == "__main__":
    main()
