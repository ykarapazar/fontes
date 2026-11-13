"""Check relative links and #anchors in the Markdown docs. Changes nothing.

    uv run python scripts/linkcheck.py            # README.md, docs/*.md, every docs/i18n/*/*.md
    uv run python scripts/linkcheck.py tr ar      # only those languages' folders

Anchors use GitHub's heading slugs, so a translated heading changes its anchor: links to it,
in the same file or another one, must use the translated slug. Exit 1 on any problem.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
HTML = re.compile(r"""(?:href|src)=["']([^"']+)["']""")


def slug(heading: str) -> str:
    h = re.sub(r"<[^>]+>", "", heading).strip().lower()
    h = "".join(ch for ch in h if ch in "- _" or unicodedata.category(ch)[0] in "LMN")
    return h.replace(" ", "-")


def _body(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def anchors(path: Path) -> set[str]:
    body = _body(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for h in re.findall(r"^#{1,6} (.+)$", body, re.M):
        s, n = slug(h), 1
        while s in out:  # GitHub numbers repeated headings: x, x-1, x-2
            s = f"{slug(h)}-{n}"
            n += 1
        out.add(s)
    return out | set(re.findall(r"""<a\s+(?:id|name)=["']([^"']+)["']""", body))


def files(langs: list[str]) -> list[Path]:
    if langs:
        return sorted(p for c in langs for p in (ROOT / "docs" / "i18n" / c).glob("*.md"))
    return [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")),
            *sorted((ROOT / "docs" / "i18n").glob("*/*.md"))]


def check(paths: list[Path]) -> list[str]:
    problems: list[str] = []
    cache: dict[Path, set[str]] = {}
    for f in paths:
        body = _body(f.read_text(encoding="utf-8"))
        nocode = re.sub(r"`[^`\n]*`", "", body)
        for link in MD.findall(nocode) + HTML.findall(nocode):
            if re.match(r"^[a-z]+:", link) or link.startswith("//"):
                continue
            path, _, frag = link.partition("#")
            target = (f.parent / path).resolve() if path else f.resolve()
            where = f.relative_to(ROOT)
            if not target.exists():
                problems.append(f"{where}: broken link {link}")
            elif frag and target.suffix == ".md":
                if frag not in cache.setdefault(target, anchors(target) if target.exists() else set()):
                    problems.append(f"{where}: missing anchor {link}")
        for tag in ("details", "summary", "p"):
            o, c = len(re.findall(rf"<{tag}[\s>]", body)), len(re.findall(rf"</{tag}>", body))
            if o != c:
                problems.append(f"{f.relative_to(ROOT)}: <{tag}> opened {o} times, closed {c}")
    return problems


def main() -> None:
    paths = files(sys.argv[1:])
    problems = check(paths)
    print("\n".join(problems))
    print(f"{len(paths)} files, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
