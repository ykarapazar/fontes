"""User-facing strings for the installer and the `fontes` command line. Standard library only.

Strings live in locales/<lang>.json next to this file, one flat JSON object per language;
en.json is the source and every other file has the same keys. Adding a language means adding
a file: no code changes.

Language: FONTES_LANG, else the OS user-interface language (macOS AppleLanguages, Windows
GetUserDefaultUILanguage, else LANGUAGE / LC_ALL / LC_MESSAGES / LANG), else English. Each
preference is tried with a fallback chain (pt-BR -> pt; pt-AO -> pt-PT -> pt; zh-TW -> zh-Hant;
zh -> zh-Hans), and a
key missing from the chosen file falls back to English.

The same module ships in the installer folder (as fontes_i18n.py, locales/ beside it) and in
the fontes wheel (as world_legal_mcp/_fontes_i18n.py, world_legal_mcp/locales/).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import cache
from pathlib import Path

LOCALES = Path(__file__).resolve().parent / "locales"
SOURCE = "en"
# Region (or bare language) -> the script subtag our files use.
_SCRIPT = {"zh": "Hans", "zh-cn": "Hans", "zh-sg": "Hans", "zh-my": "Hans",
           "zh-tw": "Hant", "zh-hk": "Hant", "zh-mo": "Hant"}
_LEGACY = {"iw": "he", "in": "id", "ji": "yi", "no": "nb", "tzm": "zgh", "tl": "fil"}


def available() -> list[str]:
    """Language codes that have a file, e.g. ['en', 'tr', 'zh-Hans']."""
    return sorted(p.stem for p in LOCALES.glob("*.json"))


def chain(tag: str) -> list[str]:
    """Most to least specific candidates for one BCP 47 tag (POSIX forms like pt_BR.UTF-8 too).

    'pt-BR' -> ['pt-BR', 'pt']; 'pt-AO' -> ['pt-AO', 'pt-PT', 'pt'] (pt is Brazilian, pt-PT European);
    'zh-TW' -> ['zh-TW', 'zh-Hant', 'zh', 'zh-Hans'];
    'sr-Latn-RS' -> ['sr-Latn-RS', 'sr-Latn', 'sr']."""
    tag = (tag or "").split(".")[0].split("@")[0].replace("_", "-").strip()
    if not tag or tag.lower() in ("c", "posix"):
        return []
    parts = tag.split("-")
    parts[0] = _LEGACY.get(parts[0].lower(), parts[0].lower())
    out = []
    for n in range(len(parts), 0, -1):
        out.append("-".join(parts[:n]))
        # zh-TW and plain zh carry no script; add the one our files are named by.
        # Portuguese outside Brazil is written in the European norm.
        if n == 2 and parts[0] == "pt" and parts[1].upper() not in ("BR", "PT") and len(parts[1]) == 2:
            out.append("pt-PT")
        if n <= 2 and not any(len(p) == 4 for p in parts[1:n]):
            script = _SCRIPT.get("-".join(parts[:n]).lower())
            if script:
                out.append(f"{parts[0]}-{script}")
    return list(dict.fromkeys(out))


@cache
def os_languages() -> list[str]:
    """The user's interface languages, most preferred first (may be empty). Read once per process."""
    langs: list[str] = []
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True,
                                 text=True, timeout=5).stdout
            langs += [x.strip().strip('",') for x in out.splitlines()[1:-1] if x.strip().strip('",')]
        except (OSError, subprocess.SubprocessError):
            pass
    elif sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            buf = ctypes.create_unicode_buffer(85)
            if k32.LCIDToLocaleName(k32.GetUserDefaultUILanguage(), buf, 85, 0):
                langs.append(buf.value)
        except (OSError, AttributeError):
            pass
    langs += [x for x in os.environ.get("LANGUAGE", "").split(":") if x]
    langs += [os.environ[v] for v in ("LC_ALL", "LC_MESSAGES", "LANG") if os.environ.get(v)]
    return langs


def language(prefs: list[str] | None = None) -> str:
    """The best available language for these preferences (default: FONTES_LANG, then the OS)."""
    if prefs is None:
        prefs = [os.environ.get("FONTES_LANG", "")] + os_languages()
    have = {c.lower(): c for c in available()}
    for p in prefs:
        for c in chain(p):
            if c.lower() in have:
                return have[c.lower()]
    return SOURCE


@cache
def _load(lang: str) -> dict[str, str]:
    return json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))


def strings(lang: str | None = None) -> dict[str, str]:
    """All strings for a language, English filling any gap."""
    lang = lang or language()
    return {**_load(SOURCE), **(_load(lang) if lang != SOURCE else {})}


def t(key: str, **kw) -> str:
    return strings()[key].format(**kw)


REPO = "https://github.com/ykarapazar/fontes/blob/main/"


def _privacy_languages() -> set[str]:
    """Languages with a translated PRIVACY.md: listed by build.sh in the installer, else read
    from the checkout's docs/i18n/."""
    here = Path(__file__).resolve().parent
    listed = here / "privacy-languages.txt"
    if listed.exists():
        return set(listed.read_text(encoding="utf-8").split())
    return {p.parent.name for p in (here.parent / "docs" / "i18n").glob("*/PRIVACY.md")}


def privacy_url(lang: str | None = None) -> str:
    """The privacy notice in this language if it is translated, else the English one."""
    lang = lang or language()
    if lang != SOURCE and lang in _privacy_languages():
        return f"{REPO}docs/i18n/{lang}/PRIVACY.md"
    return f"{REPO}docs/PRIVACY.md"


def yes(answer: str) -> bool:
    """True only for one of this language's (or English's) explicit yes words."""
    words = strings()["yes"].split(",") + _load(SOURCE)["yes"].split(",")
    return answer.strip().lower() in {w.strip().lower() for w in words if w.strip()}
