"""Translated documentation: string tables, the language switcher, and where each file goes.

    uv run python scripts/i18n_docs.py      # refresh the language switchers

docs/i18n/<lang>/strings.json holds the headings and labels of the generated docs (status page,
COVERAGE.md summary, README tables) and the translation notice; docs/i18n/en/strings.json is
the source. The generators read them: status_page.py embeds every language in the one
docs/status/index.html; catalogue.py and readme_tables.py write docs/i18n/<lang>/{COVERAGE,README}.md
for every language that has a strings.json; data rows stay as they are. HEALTH.md is English
only. See docs/i18n/TRANSLATING.md.

The switcher is the text between <!-- languages:start --> and <!-- languages:end --> in README.md,
docs/index.html and each translated README.md / index.html.

The same run writes the brand blocks of the landing pages (docs/index.html and each
docs/i18n/<lang>/index.html): <!-- favicon:start/end --> in <head> (favicon and touch icon), <!-- seo:start/end -->
in <head> (self canonical, og:url and the hreflang set of all language versions) and
<!-- logo:start/end --> in place of the plain <h1>Fontes</h1> (the lockup from docs/assets/brand/,
dark variant via <picture>). Both are inserted the first time.
"""
from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "docs" / "i18n"
LANGUAGES = ROOT / "research" / "languages.json"
SOURCE = "en"


def translations() -> list[str]:
    """Languages other than English that have a docs string table, e.g. ['tr']."""
    return sorted(p.parent.name for p in I18N.glob("*/strings.json") if p.parent.name != SOURCE)


@cache
def _table(lang: str) -> dict[str, str]:
    f = I18N / lang / "strings.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def labels(lang: str = SOURCE) -> dict[str, str]:
    """The docs strings for a language, English filling any gap."""
    return {**_table(SOURCE), **(_table(lang) if lang != SOURCE else {})}


@cache
def _meta() -> dict[str, dict]:
    return {r["code"]: r for r in json.loads(LANGUAGES.read_text(encoding="utf-8"))["languages"]}


def rtl(lang: str) -> bool:
    return bool(_meta().get(lang, {}).get("rtl"))


def autonym(lang: str) -> str:
    return _meta().get(lang, {}).get("autonym") or lang


def plural(s: dict[str, str], key: str, n: int) -> str:
    """'{n} source' / '{n} sources' from KEY_one / KEY_other."""
    return s[f"{key}_one" if n == 1 else f"{key}_other"].format(n=n)


def notice(lang: str) -> str:
    """The first line of every translated doc (markdown)."""
    return f"> {labels(lang)['doc_notice']}\n"


# Region groups for the README language picker. Each language sits in exactly one group (the
# region of the jurisdictions it serves in Fontes; English and the Council of Europe members
# Turkish, Armenian, Georgian and Azerbaijani under Europe; Spanish under the Americas, where
# most of its covered jurisdictions are). Group names stay English: strings.json has no keys for
# them yet, and adding keys means adding them to all 80 tables.
REGIONS: dict[str, tuple[str, ...]] = {
    "Europe": ("en", "fr", "de", "ru", "it", "pl", "nl", "pt-PT", "ro", "tr", "sv", "cs", "hu",
               "el", "ca", "sr", "sr-Latn", "bg", "da", "sk", "sq", "hr", "fi", "nb", "nn", "bs",
               "bs-Cyrl", "lt", "sl", "ga", "lv", "et", "mt", "lb", "is", "hy", "ka", "az"),
    "Middle East & North Africa": ("ar", "fa", "he", "ckb", "zgh"),
    "Sub-Saharan Africa": ("am", "yo", "mg", "wo", "rw"),
    "South & Central Asia": ("hi", "bn", "ur", "ta", "ps", "ne", "uz", "uz-Cyrl", "tg", "tk", "ky",
                             "dz", "dv"),
    "East & Southeast Asia": ("zh-Hans", "zh-Hant", "nan-Hant", "hak-Hant", "ja", "vi", "id", "fil",
                              "my", "ms", "km", "lo", "mn"),
    "Americas & Pacific": ("es", "pt", "qu", "ay", "gn", "ht"),
}


def top10() -> list[str]:
    """The ten most-spoken languages (`top10_world` in research/languages.json), most speakers first."""
    rows = [r for r in _meta().values() if r.get("top10_world")]
    return [r["code"] for r in sorted(rows, key=lambda r: -(r.get("ethnologue_2026_total_millions") or 0))]


SHOWN = 5   # languages named on the one-line picker; the rest are in the <details>


def _md_link(code: str, here: str) -> str:
    """One language in the picker as seen from `here`: bold when it is the current page."""
    if code == (here or SOURCE):
        return f"**{autonym(code)}**"
    if code == SOURCE:
        return "[English](../../../README.md)"
    target = f"../{code}/README.md" if here else f"docs/i18n/{code}/README.md"
    return f"[{autonym(code)}]({target})"


def switcher_md(here: str) -> str:
    """The README language picker as seen from `here` ('' = repository root, else the language
    code of a docs/i18n/<lang>/ folder): the five most-spoken languages on one line (the current
    language first when it is not among them), then every language grouped by region in a
    collapsed <details>. Only languages with a translated README are listed."""
    have = set(translations()) | {SOURCE}
    grouped = [c for codes in REGIONS.values() for c in codes]
    if sorted(grouped) != sorted(_meta()) or len(grouped) != len(set(grouped)):
        raise SystemExit("i18n_docs.REGIONS must list every language in research/languages.json once")
    first = [c for c in top10() if c in have][:SHOWN]
    if here and here not in first:
        first.insert(0, here)
    lines = [f"{labels(here or SOURCE)['doc_languages']}: " + " · ".join(_md_link(c, here) for c in first),
             "", "<details>", f"<summary>All {len(have)} languages</summary>", ""]
    for region, codes in REGIONS.items():
        shown = [c for c in codes if c in have]
        if shown:
            lines.append(f"- **{region}:** " + " · ".join(_md_link(c, here) for c in shown))
    lines += ["", "</details>"]
    return "\n".join(lines)


def switcher_html(here: str) -> str:
    """Same for the landing pages (docs/index.html and docs/i18n/<lang>/index.html)."""
    up = "" if not here else "../../"
    links = [f'<a href="{up}" hreflang="en" lang="en">English</a>' if here else "<b>English</b>"]
    for c in translations():
        if c == here:
            links.append(f'<b lang="{c}">{autonym(c)}</b>')
        else:
            href = f"../{c}/" if here else f"i18n/{c}/"
            links.append(f'<a href="{href}" hreflang="{c}" lang="{c}">{autonym(c)}</a>')
    return (f'<p class="mute">{labels(here or SOURCE)["doc_languages"]}: ' + " · ".join(links) + "</p>")


def replace_block(text: str, name: str, body: str) -> str | None:
    """Text with the <!-- name:start/end --> block replaced; None when the markers are missing."""
    pat = re.compile(rf"(<!-- {name}:start -->)\n?.*?\n?(<!-- {name}:end -->)", re.S)
    if not pat.search(text):
        return None
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)


def favicon_html(here: str) -> str:
    """The <head> icon links of a landing page."""
    b = ("../../" if here else "") + "assets/brand/"
    return (f'<link rel="icon" href="{b}favicon.ico" sizes="32x32">\n'
            f'<link rel="icon" href="{b}favicon-32.svg" type="image/svg+xml">\n'
            f'<link rel="apple-touch-icon" href="{b}apple-touch-icon.png">')


SITE = "https://ykarapazar.github.io/fontes/"


def page_url(lang: str) -> str:
    return SITE if lang in ("", SOURCE) else f"{SITE}i18n/{lang}/"


def seo_html(here: str) -> str:
    """The <head> canonical and hreflang set of a landing page: the page names itself as canonical
    and lists every language version (English and each translation), plus x-default."""
    langs = [SOURCE] + translations()
    alts = [f'<link rel="alternate" hreflang="{c}" href="{page_url(c)}">' for c in langs]
    alts.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}">')
    return f'<link rel="canonical" href="{page_url(here)}">\n' + "\n".join(alts)


def logo_html(here: str) -> str:
    """The page heading of a landing page: the Fontes lockup, light and dark."""
    b = ("../../" if here else "") + "assets/brand/"
    return (f'<h1><picture><source media="(prefers-color-scheme: dark)" srcset="{b}lockup-dark.svg">'
            f'<img src="{b}lockup.svg" alt="Fontes" width="211" height="56" style="display:block"></picture></h1>')


def brand(text: str, here: str) -> str:
    """Landing-page text with its favicon and logo blocks written (inserted the first time)."""
    head = replace_block(text, "favicon", favicon_html(here))
    if head is None:
        m = re.search(r'<meta name="viewport"[^>]*>\n', text)
        head = text[:m.end()] + f"<!-- favicon:start -->\n{favicon_html(here)}\n<!-- favicon:end -->\n" + text[m.end():]
    seo = replace_block(head, "seo", seo_html(here))
    if seo is None:   # first time: drop the page's own canonical line (it may point at English)
        head = re.sub(r'<link rel="canonical" href="[^"]*">\n', "", head)
        i = head.index("<!-- favicon:end -->\n") + len("<!-- favicon:end -->\n")
        seo = head[:i] + f"<!-- seo:start -->\n{seo_html(here)}\n<!-- seo:end -->\n" + head[i:]
    head = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: f'{m.group(1)}{page_url(here)}"', seo)
    out = replace_block(head, "logo", logo_html(here))
    if out is None:
        out = head.replace("<h1>Fontes</h1>\n", f"<!-- logo:start -->\n{logo_html(here)}\n<!-- logo:end -->\n", 1)
    return out


def switcher_targets() -> list[tuple[Path, str]]:
    """(file, expected switcher) for every page that carries one."""
    out = [(ROOT / "README.md", switcher_md("")), (ROOT / "docs" / "index.html", switcher_html(""))]
    for c in translations():
        out += [(I18N / c / "README.md", switcher_md(c)), (I18N / c / "index.html", switcher_html(c))]
    return out


def main() -> None:
    for path, body in switcher_targets():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new = replace_block(text, "languages", body)
        if new is None:
            print(f"no <!-- languages:start/end --> markers in {path.relative_to(ROOT)}")
            continue
        if path.name == "index.html":
            new = brand(new, "" if path.parent.name == "docs" else path.parent.name)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"updated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
