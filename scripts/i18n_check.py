"""Check the translations: complete, well-formed, and which required languages are still missing.

    uv run python scripts/i18n_check.py          # exit 1 if any file is malformed

Malformed (fails): a locale or string table that is not a flat JSON object of strings, lacks an
English key, has an empty string, or whose {placeholders} differ from English (a key English no
longer has is only a warning); a docs/i18n/<lang>/ folder missing a required file or the translation notice, or
whose index.html lacks lang="<lang>" (and dir="rtl" for right-to-left languages); a file named
for a language that is not in research/languages.json.
Missing (reported, not a failure): a required language with no file yet. The target is every
language in research/languages.json (all required; tier 1 is only done first).
Stale language switchers are a warning: run scripts/i18n_docs.py.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n_docs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "installer" / "locales"
DOCS = ROOT / "docs" / "i18n"
LANGUAGES = ROOT / "research" / "languages.json"
TRANSLATED_MD = ("README.md", "INSTALL.md", "PRIVACY.md", "FAQ.md", "KEYS.md")
REQUIRED_DOCS = (*TRANSLATED_MD, "index.html", "strings.json")
PLACEHOLDER = re.compile(r"\{(\w*)\}")


def check_table(path: Path, en: dict[str, str], warnings: list[str] | None = None) -> list[str]:
    """Errors in one flat string table compared with English. A key English no longer has is
    unused, so it is only a warning (appended to `warnings`)."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"{path}: not valid JSON ({e})"]
    if not isinstance(d, dict):
        return [f"{path}: not a JSON object"]
    errs = [f"{path}: missing key {k!r}" for k in en if k not in d]
    if warnings is not None:
        warnings += [f"{path}: unknown key {k!r} (not in English; unused)" for k in d if k not in en]
    for k, v in d.items():
        if not isinstance(v, str):
            errs.append(f"{path}: {k!r} is not a string")
        elif not v.strip():
            errs.append(f"{path}: {k!r} is empty")
        elif k in en and sorted(PLACEHOLDER.findall(v)) != sorted(PLACEHOLDER.findall(en[k])):
            errs.append(f"{path}: {k!r} placeholders {sorted(set(PLACEHOLDER.findall(v)))} differ from "
                        f"English {sorted(set(PLACEHOLDER.findall(en[k])))}")
    return errs


def check_docs(folder: Path, lang: str, is_rtl: bool) -> list[str]:
    """Errors in one docs/i18n/<lang>/ folder (the string table is checked separately)."""
    errs = [f"{folder}: missing {name}" for name in REQUIRED_DOCS if not (folder / name).exists()]
    try:
        doc_notice = json.loads((folder / "strings.json").read_text(encoding="utf-8")).get("doc_notice", "")
    except (OSError, ValueError, AttributeError):
        doc_notice = ""
    for name in TRANSLATED_MD:
        f = folder / name
        if f.exists():
            first = next((ln for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()), "")
            if not doc_notice or doc_notice not in first:
                errs.append(f"{f}: must start with the translation notice (doc_notice in strings.json)")
    f = folder / "index.html"
    if f.exists():
        html = f.read_text(encoding="utf-8")
        tag = re.search(r"<html\b[^>]*>", html, re.I)
        attrs = tag.group(0) if tag else ""
        if not re.search(rf"""\blang=["']?{re.escape(lang)}\b""", attrs):
            errs.append(f"{f}: <html> needs lang=\"{lang}\"")
        if is_rtl and not re.search(r"""\bdir=["']?rtl\b""", attrs):
            errs.append(f"{f}: <html> needs dir=\"rtl\" ({lang} is right-to-left)")
        if doc_notice and doc_notice not in html:
            errs.append(f"{f}: must show the translation notice")
    readme = folder / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for name in ("languages", "coverage", "sources"):
            if f"<!-- {name}:start -->" not in text or f"<!-- {name}:end -->" not in text:
                errs.append(f"{readme}: missing <!-- {name}:start/end --> markers")
    return errs


def check(locales: Path = LOCALES, docs: Path = DOCS, languages: Path = LANGUAGES) -> dict:
    """{'errors': [...], 'warnings': [...], 'target': [...], 'missing': {...}}."""
    meta = json.loads(languages.read_text(encoding="utf-8"))
    target = meta["target"]
    rows = {r["code"]: r for r in meta["languages"]}
    errors: list[str] = []
    warnings: list[str] = []

    en_ui = json.loads((locales / "en.json").read_text(encoding="utf-8"))
    ui = sorted(p.stem for p in locales.glob("*.json"))
    for code in ui:
        if code not in rows:
            errors.append(f"{locales / (code + '.json')}: {code!r} is not a language in {languages.name}")
        if code != "en":
            errors += check_table(locales / f"{code}.json", en_ui, warnings)

    en_docs = json.loads((docs / "en" / "strings.json").read_text(encoding="utf-8"))
    translated = sorted(p.name for p in docs.iterdir() if p.is_dir() and p.name != "en")
    for code in translated:
        if code not in rows:
            errors.append(f"{docs / code}: {code!r} is not a language in {languages.name}")
            continue
        if (docs / code / "strings.json").exists():
            errors += check_table(docs / code / "strings.json", en_docs, warnings)
        errors += check_docs(docs / code, code, rows[code]["rtl"])

    if docs == DOCS:
        for path, body in i18n_docs.switcher_targets():
            if path.exists() and body not in path.read_text(encoding="utf-8"):
                warnings.append(f"{path.relative_to(ROOT)}: language switcher out of date "
                                "(run scripts/i18n_docs.py)")

    have_docs = set(translated) | {"en"}
    missing = {
        "installer": [c for c in target if c not in ui],
        "docs": [c for c in target if c not in have_docs],
    }
    return {"errors": errors, "warnings": warnings, "target": target, "tier1": meta["tier1"],
            "missing": missing}


def main() -> int:
    r = check()
    done = [c for c in r["target"] if c not in r["missing"]["installer"] and c not in r["missing"]["docs"]]
    print(f"Target: {len(r['target'])} languages, all required "
          f"(tier 1: {len(r['tier1'])}, tier 2: {len(r['target']) - len(r['tier1'])}). "
          f"Complete: {len(done)} ({', '.join(done)}).")
    for part in ("installer", "docs"):
        miss = r["missing"][part]
        t1 = [c for c in miss if c in r["tier1"]]
        t2 = [c for c in miss if c not in r["tier1"]]
        print(f"Missing {part} translations: {len(miss)}"
              + (f"\n  tier 1: {' '.join(t1)}" if t1 else "") + (f"\n  tier 2: {' '.join(t2)}" if t2 else ""))
    for w in r["warnings"]:
        print(f"warning: {w}")
    for e in r["errors"]:
        print(f"error: {e}")
    print(f"{len(r['errors'])} errors.")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
