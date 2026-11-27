"""Draw the coverage world map from the same scorecard as docs/COVERAGE.md.

    uv run python scripts/coverage_map.py      # also run at the end of scripts/catalogue.py

Writes docs/assets/coverage-map.svg and coverage-map-dark.svg (static, no script; docs/assets/map.js
makes them interactive on the landing pages), and fills
the <!-- map:start/end --> block in README.md, docs/index.html and every translated
docs/i18n/<lang>/{README.md,index.html} (inserting it the first time).

Categories: covered = at least one complete area in the COVERAGE.md scorecard; partial = an
adapter that is not covered; not yet = no adapter (Russia and Belarus, excluded on purpose,
look the same). Jurisdictions with no territory of their own (EU, international courts, DIFC)
are chips under the map; small ones that 110m geometry drops or shrinks to a speck get a dot.
Boundaries follow Natural Earth's default de facto view (Kashmir, Western Sahara, Crimea,
Taiwan and other contested areas as Natural Earth draws them). Geometry: scripts/data/countries.json.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from world_legal_mcp import registry

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogue  # noqa: E402
import i18n_docs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GEO = Path(__file__).resolve().parent / "data" / "countries.json"
OUT = ROOT / "docs" / "assets"

# Chip labels for jurisdictions without a territory (the adapter name is too long for a chip).
SHORT = {"afchpr": "African Court (AfCHPR)", "ccj": "Caribbean Court of Justice", "echr": "ECHR",
         "efta": "EFTA Court", "eu": "European Union", "ecowas": "ECOWAS Court", "icj": "ICJ",
         "icsid": "ICSID", "itlos": "ITLOS", "untc": "UN Treaty Collection", "wto": "WTO disputes",
         "difc": "DIFC Courts (Dubai)"}

# Ordinal one-hue ramp (dataviz reference palette, blue steps), validated against each surface.
THEMES = {
    "light": {"surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "border": "#fcfcfb",
              "line": "#e1e0d9", "covered": "#1c5cab", "partial": "#86b6ef", "none": "#dddcd6"},
    "dark": {"surface": "#1a1a19", "ink": "#f0efec", "ink2": "#c3c2b7", "border": "#1a1a19",
             "line": "#2c2c2a", "covered": "#6da7ec", "partial": "#1c5cab", "none": "#3a3a37"},
}
LABEL = {"covered": "Covered", "partial": "Partial", "none": "Not yet"}

W, PAD = 960, 16
FONT = 'system-ui,-apple-system,&quot;Segoe UI&quot;,Helvetica,Arial,sans-serif'
DOT_R, DOT_BELOW = 4.0, 10.0   # dot radius; dot a jurisdiction whose shape is under this many px²


def equal_earth(lon: float, lat: float) -> tuple[float, float]:
    """Equal Earth projection (Šavrič, Patterson, Jenny 2018), unit sphere; y grows north."""
    a1, a2, a3, a4 = 1.340264, -0.081106, 0.000893, 0.003796
    t = math.asin(math.sqrt(3) / 2 * math.sin(math.radians(lat)))
    t2, t6 = t * t, t ** 6
    x = 2 * math.sqrt(3) * math.radians(lon) * math.cos(t) / (3 * (9 * a4 * t6 * t2 + 7 * a3 * t6 + 3 * a2 * t2 + a1))
    return x, t * (a4 * t6 * t2 + a3 * t6 + a2 * t2 + a1)


def scorecard() -> tuple[dict[str, str], dict[str, str]]:
    """code -> 'covered' | 'partial', and code -> name, for every adapter (as COVERAGE.md counts them)."""
    registry.discover()
    cat, names = {}, {}
    for j in registry._all.values():
        if getattr(j, "via_lexifina", False):
            continue
        (a, _), (b, _) = catalogue._score(j.code, catalogue._map(j.code))
        cat[j.code] = "covered" if "complete" in (a, b) else "partial"
        names[j.code] = j.name
    return cat, names


def _text_w(s: str, size: float) -> float:
    """Rough width of system-ui text (no font metrics in a static SVG)."""
    return size * sum(0.85 if ch in "mwMW" else 0.3 if ch in " ().,:'IJlijtf" else 0.7 if ch.isupper() else 0.55
                      for ch in s)


def _area(pts) -> float:
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2


def build(theme: str, cat: dict[str, str], names: dict[str, str], today: str) -> tuple[str, int]:
    c = THEMES[theme]
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    shapes, points = geo["shapes"], geo["points"]
    proj = {k: [[[equal_earth(x, y) for x, y in r] for r in poly] for poly in v["polygons"]] for k, v in shapes.items()}
    xs = [p[0] for v in proj.values() for poly in v for r in poly for p in r]
    ys = [p[1] for v in proj.values() for poly in v for r in poly for p in r]
    s = (W - 2 * PAD) / (max(xs) - min(xs))
    top = 76
    x0, y0 = PAD - min(xs) * s, top + max(ys) * s

    def px(p):
        return x0 + p[0] * s, y0 - p[1] * s

    map_h = (max(ys) - min(ys)) * s
    territorial = {code for code in cat if code.upper() in points}
    body, areas = [], {}
    for k, polys in proj.items():
        code = k.lower()
        kind = cat.get(code, "none")
        d, area = [], 0.0
        for poly in polys:
            for i, r in enumerate(poly):
                q = [px(p) for p in r]
                if i == 0:
                    area += _area(q)
                d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in q) + "Z")
        areas[code] = area
        body.append(f'<path data-code="{code}" data-kind="{kind}" fill="{c[kind]}" d="{"".join(d)}"><title>{escape(shapes[k]["name"])}: '
                    f'{LABEL[kind].lower()}</title></path>')
    dots = []
    for code in sorted(territorial, key=lambda x: (cat[x] == "covered", x)):
        if areas.get(code, 0) >= DOT_BELOW:
            continue
        x, y = px(equal_earth(*points[code.upper()]))
        dots.append(f'<circle data-code="{code}" data-kind="{cat[code]}" cx="{x:.1f}" cy="{y:.1f}" r="{DOT_R}" fill="{c[cat[code]]}" stroke="{c["surface"]}" '
                    f'stroke-width="1.5"><title>{escape(names[code])}: {LABEL[cat[code]].lower()}</title></circle>')

    covered = sum(v == "covered" for v in cat.values())
    out = [f'<text x="{PAD}" y="34" font-size="20" font-weight="600" fill="{c["ink"]}">'
           f'Coverage: {covered} of {len(cat)} jurisdictions</text>',
           f'<text x="{PAD}" y="57" font-size="13" fill="{c["ink2"]}">Covered = one complete area: the top court\'s '
           f'precedents, or the constitution and primary acts. Generated {today}.</text>',
           f'<g stroke="{c["border"]}" stroke-width="0.6" stroke-linejoin="round">', *body, "</g>", *dots]

    # Legend: swatch + label, ink text; dot sample says what the dots are.
    y = top + map_h + 30
    n_part = sum(v == "partial" for v in cat.values())
    items = [("covered", f"Covered ({covered})"), ("partial", f"Partial: some sources, no complete area ({n_part})"),
             ("none", "Not yet or not included")]
    x = PAD
    for kind, text in items:
        out.append(f'<rect x="{x}" y="{y - 11}" width="14" height="14" rx="3" fill="{c[kind]}"/>')
        out.append(f'<text x="{x + 20}" y="{y}" font-size="13" fill="{c["ink"]}">{escape(text)}</text>')
        x += 20 + _text_w(text, 13) + 22
    out.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="{DOT_R}" fill="{c["covered"]}" stroke="{c["surface"]}" stroke-width="1.5"/>')
    out.append(f'<text x="{x + 16}" y="{y}" font-size="13" fill="{c["ink"]}">Small jurisdiction</text>')

    # Chips: jurisdictions with no territory of their own.
    y += 30
    out.append(f'<text x="{PAD}" y="{y}" font-size="13" font-weight="600" fill="{c["ink2"]}">'
               f'No territory of their own: international courts and bodies, the EU, DIFC</text>')
    y += 12
    x = PAD
    chips = sorted((code for code in cat if code not in territorial),
                   key=lambda k: (cat[k] != "covered", SHORT.get(k, names[k]).lower()))
    for code in chips:
        text = SHORT.get(code, names[code])
        w = 10 + 10 + 6 + _text_w(text, 12.5) + 10
        if x + w > W - PAD:
            x, y = PAD, y + 32
        out.append(f'<g data-code="{code}" data-kind="{cat[code]}"><title>{escape(names[code])}: {LABEL[cat[code]].lower()}</title>'
                   f'<rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="none" stroke="{c["line"]}"/>'
                   f'<rect x="{x + 10}" y="{y + 7}" width="10" height="10" rx="2" fill="{c[cat[code]]}"/>'
                   f'<text x="{x + 26}" y="{y + 16.5}" font-size="12.5" fill="{c["ink"]}">{escape(text)}</text></g>')
        x += w + 8
    y += 24 + 26
    out.append(f'<text x="{PAD}" y="{y}" font-size="11.5" fill="{c["ink2"]}">Boundaries: Natural Earth, '
               f'de facto (public domain). Per-jurisdiction detail: docs/COVERAGE.md</text>')
    h = int(y + 16)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
           f'font-family="{FONT}" role="img" aria-labelledby="t">'
           f'<title id="t">Fontes coverage map: {covered} of {len(cat)} jurisdictions covered</title>'
           f'<rect width="{W}" height="{h}" rx="12" fill="{c["surface"]}"/>' + "".join(out) + "</svg>\n")
    return svg, h


# --- the <!-- map --> block in the READMEs and landing pages -------------------------------


def _alt(lang: str, covered: int, total: int) -> str:
    if lang == "en":  # English is a sentence; the translations keep their string-table labels
        return f"Map of the {total} live jurisdictions Fontes searches, {covered} of them covered completely."
    L = i18n_docs.labels(lang)
    return escape(L["cov_title"] + ": " + L["cov_covered"].format(n=covered, total=total).replace("*", ""), {'"': "&quot;"})


def block_md(up: str, coverage: str, alt: str) -> str:
    return (f'<p align="center"><a href="{coverage}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{up}assets/coverage-map-dark.svg">'
            f'<img src="{up}assets/coverage-map.svg" alt="{alt}" width="880"></picture></a></p>')


def block_html(up: str, coverage: str, alt: str, h: int, lang: str = "en") -> str:
    # Wider than the 720px text column, so the legend stays legible; centred, never past the viewport.
    L = i18n_docs.labels(lang)
    words = "".join(f' data-{k.replace("_", "-")}="{escape(L[k], {chr(34): "&quot;"})}"'
                    for k in ("map_hint", "map_table", "map_covered", "map_partial", "map_none"))
    return (f'<div id="map" data-map{words} style="width:min({W}px,calc(100vw - 32px));max-width:none;margin:16px 0 16px 50%;transform:translateX(-50%)">'
            f'<a href="{coverage}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{up}assets/coverage-map-dark.svg">'
            f'<img src="{up}assets/coverage-map.svg" alt="{alt}" width="{W}" height="{h}" '
            f'style="max-width:100%;height:auto"></picture></a></div>'
            f'<script src="{up}assets/map.js" defer></script>')


def _insert_md(text: str, body: str) -> str:
    """Put a new block before the heading that follows Quickstart (or the first heading after the
    language switcher, in translations without a Quickstart section)."""
    m = re.search(r"^## Quickstart\n.*?(?=^## )", text, re.S | re.M) or \
        re.search(r"<!-- languages:end -->\n.*?(?=^## )", text, re.S | re.M)
    if not m:
        raise SystemExit("no place for the map block")
    return text[:m.end()] + f"<!-- map:start -->\n{body}\n<!-- map:end -->\n\n" + text[m.end():]


def _insert_html(text: str, body: str) -> str:
    i = text.index("</header>") + len("</header>")
    return text[:i] + f"\n<!-- map:start -->\n{body}\n<!-- map:end -->" + text[i:]


def fill(path: Path, body: str, insert) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = i18n_docs.replace_block(text, "map", body) or insert(text, body)
    if new != text:
        path.write_text(new, encoding="utf-8")


def main() -> None:
    cat, names = scorecard()
    today = dt.date.today().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, name in (("light", "coverage-map.svg"), ("dark", "coverage-map-dark.svg")):
        svg, h = build(theme, cat, names, today)
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"wrote {(OUT / name).relative_to(ROOT)} ({len(svg.encode()) // 1024} KB)")
    covered, total = sum(v == "covered" for v in cat.values()), len(cat)
    gh = "https://github.com/ykarapazar/fontes/blob/main/docs/"
    # GitHub runs no script in a README, so its map links to the interactive one on the landing page.
    fill(ROOT / "README.md", block_md("docs/", "https://ykarapazar.github.io/fontes/#map", _alt("en", covered, total)), _insert_md)
    fill(ROOT / "docs" / "index.html", block_html("", gh + "COVERAGE.md", _alt("en", covered, total), h), _insert_html)
    for lang in i18n_docs.translations():
        alt = _alt(lang, covered, total)
        fill(i18n_docs.I18N / lang / "README.md", block_md("../../", "COVERAGE.md", alt), _insert_md)
        fill(i18n_docs.I18N / lang / "index.html",
             block_html("../../", f"{gh}i18n/{lang}/COVERAGE.md", alt, h, lang), _insert_html)
    print(f"map: {covered} of {total} covered; README and landing-page blocks filled")


if __name__ == "__main__":
    main()
