"""Write docs/law/<code>/index.html (one page per jurisdiction), docs/law/index.html and docs/sitemap.xml.

    uv run python scripts/country_pages.py

One page per adapter, so a search for a country's case law or legislation can find Fontes.
Everything on a page comes from the adapter: sources, notes, gaps and sample queries.
The style block is copied from docs/index.html so the pages match the landing page.
"""
from __future__ import annotations

import re
from html import escape
from pathlib import Path

from world_legal_mcp import registry
from world_legal_mcp.base import CASELAW, LEGISLATION

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = DOCS / "law"
SITE = "https://ykarapazar.github.io/fontes/"
STYLE = re.search(r"<style>.*?</style>", (DOCS / "index.html").read_text(), re.S).group(0)


def _what(j) -> str:
    c = all(j.supports(m) for m in CASELAW)
    l = all(j.supports(m) for m in LEGISLATION)
    return "case law and legislation" if c and l else "case law" if c else "legislation"


def _head(title: str, desc: str, url: str, up: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="{up}assets/brand/favicon.ico" sizes="32x32">
<link rel="icon" href="{up}assets/brand/favicon-32.svg" type="image/svg+xml">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}assets/brand/social-preview.png">
{STYLE}
</head>
<body>
<main>
<p class="mute"><a href="{up}">Fontes</a> / <a href="{up}law/">Coverage by jurisdiction</a></p>
"""


_FOOT = """<footer>
<p>Fontes is a research aid, not legal advice. Read the full decision or provision at the source before you rely on it.</p>
</footer>
</main>
</body>
</html>
"""


def _source(s) -> str:
    covers = " and ".join({"caselaw": "case law", "legislation": "legislation"}.get(c, c) for c in s.covers)
    extra = []
    if not s.official:
        extra.append("unofficial; every answer says so")
    if s.auth == "free key":
        extra.append('needs a free key (<a href="https://github.com/ykarapazar/fontes/blob/main/docs/KEYS.md">how</a>)')
    if s.needs_permission:
        extra.append("off unless you hold the publisher's permission")
    tail = f" ({'; '.join(extra)})" if extra else ""
    return f'<li><a href="{escape(s.url)}">{escape(s.name)}</a>: {covers}{tail}</li>'


def _ask(j) -> list[str]:
    s = j.samples
    out = []
    if s.get("caselaw_query"):
        out.append(f"Find {j.name} case law on {s['caselaw_query'].strip(chr(34))}")
    if s.get("legislation_query"):
        out.append(f"Find {j.name} legislation: {s['legislation_query'].strip(chr(34))}")
    return out


def page(j) -> str:
    what = _what(j)
    url = f"{SITE}law/{j.code}/"
    names = ", ".join(s.name for s in j.sources)
    title = f"{j.name}: {what} for your AI app | Fontes"
    desc = (f"Let Claude, Codex, Cursor and other AI apps look up {j.name} {what} live from "
            f"{names}. Free and open source; every result links to the original.")
    if len(desc) > 300:
        desc = (f"Let Claude, Codex, Cursor and other AI apps look up {j.name} {what} live from the "
                f"courts' and governments' websites. Free and open source; every result links to the original.")
    h = [_head(title, desc, url, "../../"),
         f"<h1>{escape(j.name)}: {what} for your AI app</h1>",
         f'<p class="lead">Fontes lets your AI app search {escape(j.name)} {what} at the source and '
         f"link every result to the original. It is a free, open-source MCP server for Claude Desktop, "
         f"Claude Code, Codex, Cursor, VS Code and other apps.</p>",
         "<h2>Sources</h2>", "<ul>", *(_source(s) for s in j.sources), "</ul>"]
    if j.notes:
        h += ["<h2>What it covers</h2>", f"<p>{escape(j.notes)}</p>"]
    if j.gaps:
        h += ["<h2>What it does not cover</h2>", "<ul>", *(f"<li>{escape(g)}</li>" for g in j.gaps), "</ul>"]
    ask = _ask(j)
    if ask:
        h += ["<h2>Questions to try</h2>",
              "<p>Ask in any language; the search words work best in the language of the source.</p>",
              "<ul>", *(f"<li><em>{escape(a)}</em></li>" for a in ask), "</ul>"]
    h += ["<h2>Install</h2>",
          "<p>Claude Code: <code>claude mcp add fontes -- uvx fontes-mcp</code>. Codex: "
          "<code>codex mcp add fontes -- uvx fontes-mcp</code>. Claude Desktop and one-click installers "
          'for Mac and Windows: the <a href="https://github.com/ykarapazar/fontes/releases/latest">latest release</a>. '
          'Other apps: the <a href="https://github.com/ykarapazar/fontes/blob/main/docs/INSTALL.md">installation guide</a>.</p>',
          f'<p class="mute">Jurisdiction code: <code>{j.code}</code>. Whether each source is working today: '
          f'<a href="../../status/">source status</a>, checked daily.</p>',
          _FOOT]
    return "\n".join(h)


def index(js) -> str:
    url = f"{SITE}law/"
    title = "Case law and legislation by jurisdiction | Fontes"
    desc = (f"The {len(js)} jurisdictions and international courts Fontes can search from your AI app, "
            "each with its official sources and known gaps.")
    rows = [f'<li><a href="{j.code}/">{escape(j.name)}</a>: {_what(j)}</li>' for j in js]
    return "\n".join([_head(title, desc, url, "../"),
                      "<h1>Coverage by jurisdiction</h1>",
                      f"<p class=\"lead\">{len(js)} jurisdictions and international courts. Each page lists the "
                      "sources Fontes reads and what it does not cover.</p>",
                      "<ul>", *rows, "</ul>", _FOOT])


def sitemap(js) -> str:
    urls = [SITE, f"{SITE}status/", f"{SITE}compare.html", f"{SITE}law/"] + [f"{SITE}law/{j.code}/" for j in js]
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def main() -> None:
    registry.discover()
    js = sorted(registry._all.values(), key=lambda j: j.name.lower())
    for j in js:
        d = OUT / j.code
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(j))
    (OUT / "index.html").write_text(index(js))
    (DOCS / "sitemap.xml").write_text(sitemap(js))
    print(f"wrote {len(js)} pages, docs/law/index.html and docs/sitemap.xml")


if __name__ == "__main__":
    main()
